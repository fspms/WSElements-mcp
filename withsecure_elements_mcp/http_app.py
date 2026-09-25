"""
HTTP transports (streamable-http and SSE) for the WithSecure Elements MCP server.

Both options are opt-in and backward compatible:

- ``MCP_AUTH_TOKEN``: when set, every MCP request must carry
  ``Authorization: Bearer <token>`` (``/health`` and CORS preflight excepted).
  When unset, the server stays open as before and logs a warning.
- ``MCP_HTTP_MODE=sdk``: additionally serves the official MCP SDK
  streamable-HTTP transport on ``/mcp``. The legacy JSON-RPC endpoint on ``/``
  is always kept so existing clients keep working unchanged.
"""

import contextlib
import hmac
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.types import ASGIApp, Receive, Scope, Send

if TYPE_CHECKING:
    from .server import WithSecureElementsMCPServer

logger = logging.getLogger("withsecure-elements-mcp")

SDK_PATH = "/mcp"
_PUBLIC_PATHS = {"/health"}


class BearerTokenMiddleware:
    """Require ``Authorization: Bearer <token>`` on HTTP requests.

    Pure ASGI middleware (not BaseHTTPMiddleware) so streamed/SSE responses are
    not buffered. Health checks and CORS preflight requests are exempt.
    """

    def __init__(self, app: ASGIApp, token: str):
        self.app = app
        self._expected = f"Bearer {token}".encode()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in _PUBLIC_PATHS or scope["method"] == "OPTIONS":
            await self.app(scope, receive, send)
            return
        provided = dict(scope.get("headers") or []).get(b"authorization", b"")
        if not hmac.compare_digest(provided, self._expected):
            response = JSONResponse(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32001, "message": "Unauthorized"}},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def _middleware(token: Optional[str]) -> list:
    """CORS (outermost, so preflight never needs a token) then optional auth."""
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization", "Accept", "Mcp-Session-Id", "Mcp-Protocol-Version"],
            expose_headers=["Mcp-Session-Id"],
        )
    ]
    if token:
        middleware.append(Middleware(BearerTokenMiddleware, token=token))
    else:
        logger.warning(
            "MCP_AUTH_TOKEN is not set: the HTTP endpoint accepts unauthenticated requests. "
            "Set MCP_AUTH_TOKEN to require 'Authorization: Bearer <token>'."
        )
    return middleware


def _rpc_result(request_id: Any, result: Dict[str, Any]) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": result})


def _rpc_error(request_id: Any, code: int, message: str, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}},
        status_code=status_code,
    )


def build_streamable_http_app(mcp: "WithSecureElementsMCPServer") -> Starlette:
    """Build the ASGI app for ``--transport streamable-http``."""
    config = mcp.mcp_config

    async def handle_legacy(request: Request) -> Response:
        """Legacy JSON-RPC endpoint (plain JSON responses), kept for compatibility."""
        data: Dict[str, Any] = {}
        try:
            data = await request.json()
            method = data.get("method", "")
            request_id = data.get("id")
            params = data.get("params") or {}
            logger.info(f"Received MCP request: {method}")

            # JSON-RPC notifications (no id) get no response body.
            if method.startswith("notifications/") or "id" not in data:
                return Response(status_code=202)

            if method == "initialize":
                return _rpc_result(request_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                    },
                    "serverInfo": {"name": "withsecure-elements-mcp", "version": "0.2.0"},
                })

            if method == "ping":
                return _rpc_result(request_id, {})

            if method == "tools/list":
                tools = [t.model_dump(exclude_none=True, by_alias=True) for t in mcp._build_tools()]
                return _rpc_result(request_id, {"tools": tools})

            if method == "tools/call":
                tool_name = params.get("name", "")
                result = await mcp._dispatch_tool(tool_name, params.get("arguments") or {})
                if result is None:
                    return _rpc_error(request_id, -32601, f"Tool '{tool_name}' not found")
                return _rpc_result(request_id, result.model_dump(exclude_none=True, by_alias=True))

            if method == "resources/list":
                resources = [r for module in mcp.modules for r in module.get_resources()]
                return _rpc_result(request_id, {"resources": resources})

            if method == "resources/read":
                uri = params.get("uri", "")
                for module in mcp.modules:
                    text = await module.read_resource(uri)
                    if text is not None:
                        return _rpc_result(request_id, {"contents": [
                            {"uri": uri, "mimeType": "application/json", "text": text}
                        ]})
                return _rpc_error(request_id, -32002, f"Resource '{uri}' not found")

            return _rpc_error(request_id, -32601, f"Method '{method}' not found")

        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            request_id = data.get("id") if isinstance(data, dict) else None
            return _rpc_error(request_id, -32603, str(e), status_code=500)

    async def health(request: Request) -> Response:
        return JSONResponse({"status": "ok"})

    routes = [
        Route("/", handle_legacy, methods=["POST"]),
        Route("/health", health, methods=["GET"]),
    ]
    lifespan = None

    if config.http_mode == "sdk":
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

        # Stateless: no server-side session, so restarts and multiple replicas
        # behind a load balancer need no sticky sessions.
        manager = StreamableHTTPSessionManager(app=mcp.server, stateless=True)

        class _SdkEndpoint:
            """ASGI endpoint (a Route, not a Mount, so /mcp is not redirected to /mcp/)."""

            async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
                await manager.handle_request(scope, receive, send)

        routes.append(Route(SDK_PATH, _SdkEndpoint(), methods=["GET", "POST", "DELETE"]))

        @contextlib.asynccontextmanager
        async def lifespan(app: Starlette):
            async with manager.run():
                yield

    return Starlette(routes=routes, middleware=_middleware(config.auth_token), lifespan=lifespan)


def build_sse_app(mcp: "WithSecureElementsMCPServer") -> Starlette:
    """Build the ASGI app for ``--transport sse``."""
    from mcp.server.sse import SseServerTransport

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await mcp.server.run(read_stream, write_stream, mcp.server.create_initialization_options())
        return Response()

    async def health(request: Request) -> Response:
        return JSONResponse({"status": "ok"})

    return Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/health", health, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        middleware=_middleware(mcp.mcp_config.auth_token),
    )

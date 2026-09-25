"""
Main MCP server for WithSecure Elements.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, Resource, TextContent, Tool

from .config import load_config
from .auth import WithSecureAuth
from .modules import IncidentsModule, EventsModule, OrganizationsModule, DevicesModule, ResponseActionsModule, SoftwareUpdatesModule, ManagementModule


class WithSecureElementsMCPServer:
    """MCP server for WithSecure Elements."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        debug: bool = False,
        enabled_modules: Optional[List[str]] = None
    ):
        """Initialize MCP server."""
        self.withsecure_config, self.mcp_config = load_config()
        
        # Override with provided parameters
        if base_url:
            self.withsecure_config.base_url = base_url
        if debug is not None:
            self.mcp_config.debug = debug
        if enabled_modules:
            self.mcp_config.enabled_modules = enabled_modules
        
        # Logging configuration
        self._setup_logging()
        
        # MCP server initialization
        self.server = Server("withsecure-elements-mcp", version="0.2.0")
        self.auth = None
        self.modules = []
    
    def _setup_logging(self) -> None:
        """Configure logging system."""
        level = logging.DEBUG if self.mcp_config.debug else getattr(logging, self.mcp_config.log_level.upper())
        
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stderr)]
        )
        
        self.logger = logging.getLogger("withsecure-elements-mcp")
    
    async def _initialize_modules(self) -> None:
        """Initialize enabled modules."""
        if not self.auth:
            raise RuntimeError("Authentication not initialized")
        
        available_modules = {
            "incidents": IncidentsModule,
            "events": EventsModule,
            "organizations": OrganizationsModule,
            "devices": DevicesModule,
            "response_actions": ResponseActionsModule,
            "software_updates": SoftwareUpdatesModule,
            "management": ManagementModule,
        }
        
        for module_name in self.mcp_config.enabled_modules:
            if module_name in available_modules:
                module_class = available_modules[module_name]
                module = module_class(self.server, self.auth, self.withsecure_config)
                self.modules.append(module)
                self.logger.info(f"Module '{module_name}' initialized")
            else:
                self.logger.warning(f"Module '{module_name}' not recognized, ignored")

    @staticmethod
    def _to_text_content(result: Any) -> List[TextContent]:
        """Normalize a module call_tool result into MCP TextContent blocks."""
        if isinstance(result, dict) and "content" in result:
            blocks = result.get("content") or []
            out = [
                TextContent(type="text", text=b.get("text", ""))
                for b in blocks
                if isinstance(b, dict) and b.get("type") == "text"
            ]
            if out:
                return out
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        if isinstance(result, str):
            return [TextContent(type="text", text=result)]
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

    # Tools that perform disruptive/destructive actions on endpoints. Used to
    # set the MCP destructiveHint so clients (e.g. Claude) can warn/confirm.
    _DESTRUCTIVE_TOOLS = {
        "isolate_device",
        "restart_system",
        "scan_device",
        "install_software_updates",
        "create_response_action",
        "update_devices",
        "delete_devices",
        "create_invitation",
        "delete_invitations",
        "renew_invitations",
    }

    @classmethod
    def _annotations_for(cls, name: str) -> Optional[Dict[str, Any]]:
        """Derive MCP tool annotations from the tool name.

        Read tools (list_*/get_*) are flagged read-only; known disruptive tools
        are flagged destructive so clients can prompt for confirmation.
        """
        annotations: Dict[str, Any] = {}
        if name.startswith(("list_", "get_")):
            annotations["readOnlyHint"] = True
        if name in cls._DESTRUCTIVE_TOOLS:
            annotations["destructiveHint"] = True
        return annotations or None

    def _build_tools(self) -> List[Tool]:
        """Aggregate tool definitions from every enabled module (deduplicated)."""
        tools: List[Tool] = []
        seen: set = set()
        for module in self.modules:
            for tool in module.get_tools():
                name = tool["name"]
                if name in seen:
                    continue
                seen.add(name)
                tools.append(
                    Tool(
                        name=name,
                        description=tool.get("description", ""),
                        inputSchema=tool.get(
                            "inputSchema", {"type": "object", "properties": {}}
                        ),
                        annotations=tool.get("annotations")
                        or self._annotations_for(name),
                    )
                )
        return tools

    async def _dispatch_tool(self, name: str, arguments: Dict[str, Any]) -> Optional[CallToolResult]:
        """Route a tool call to the owning module; None if no module handles it.

        Preserves the module's isError flag so clients can tell failures apart
        from successful results.
        """
        for module in self.modules:
            result = await module.call_tool(name, arguments or {})
            if result is not None:
                is_error = isinstance(result, dict) and bool(result.get("isError"))
                return CallToolResult(content=self._to_text_content(result), isError=is_error)
        return None

    def _register_central_handlers(self) -> None:
        """Register MCP handlers that aggregate every enabled module.

        The MCP low-level Server keeps a single handler per request type, so each
        module registering its own @server.list_tools()/call_tool() would overwrite
        the previous one. These central handlers are registered after all modules
        are initialized and dispatch to each module, exposing the full tool surface
        across every transport (stdio included).
        """

        @self.server.list_tools()
        async def _list_tools() -> List[Tool]:
            return self._build_tools()

        @self.server.call_tool()
        async def _call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            result = await self._dispatch_tool(name, arguments)
            if result is None:
                raise ValueError(f"Tool '{name}' not found")
            return result

        @self.server.list_resources()
        async def _list_resources() -> List[Resource]:
            resources: List[Resource] = []
            seen: set = set()
            for module in self.modules:
                for res in module.get_resources():
                    uri = res["uri"]
                    if uri in seen:
                        continue
                    seen.add(uri)
                    resources.append(
                        Resource(
                            uri=uri,
                            name=res["name"],
                            description=res.get("description"),
                            mimeType=res.get("mimeType", "application/json"),
                        )
                    )
            return resources

        @self.server.read_resource()
        async def _read_resource(uri) -> str:
            uri_str = str(uri)
            for module in self.modules:
                result = await module.read_resource(uri_str)
                if result is not None:
                    return result
            raise ValueError(f"Unrecognized resource URI: {uri_str}")

    async def run(self, transport: str = "stdio", host: str = "localhost", port: int = 8000) -> None:
        """Run MCP server."""
        try:
            # Configuration validation
            if not self.withsecure_config.client_id or not self.withsecure_config.client_secret:
                raise ValueError("WITHSECURE_CLIENT_ID and WITHSECURE_CLIENT_SECRET must be defined")
            
            self.logger.info("Initializing WithSecure Elements MCP server...")
            self.logger.info(f"Base URL: {self.withsecure_config.base_url}")
            self.logger.info(f"Enabled modules: {', '.join(self.mcp_config.enabled_modules)}")
            
            # Authentication initialization
            async with WithSecureAuth(self.withsecure_config) as auth:
                self.auth = auth
                
                # Probe authentication, but do NOT fail startup on error: the
                # server must still come up so the client can list tools and get
                # a clear error on first call. Tokens are fetched lazily per call.
                try:
                    await auth.get_token()
                    self.logger.info("Authentication successful")
                except Exception as e:
                    self.logger.warning(
                        f"Initial authentication probe failed ({e}); the server will "
                        f"start anyway and retry authentication on the first tool call."
                    )

                # Initialize modules
                await self._initialize_modules()

                # Register central handlers that aggregate all modules.
                # Done after module init so they supersede per-module handlers.
                self._register_central_handlers()

                # Transport configuration
                if transport == "stdio":
                    self.logger.info("Starting server with stdio transport")
                    async with stdio_server() as (read_stream, write_stream):
                        await self.server.run(
                            read_stream,
                            write_stream,
                            self.server.create_initialization_options()
                        )
                
                elif transport in ("sse", "streamable-http"):
                    import uvicorn
                    from .http_app import SDK_PATH, build_sse_app, build_streamable_http_app

                    if transport == "sse":
                        app = build_sse_app(self)
                        endpoints = "/sse"
                    else:
                        app = build_streamable_http_app(self)
                        endpoints = "/ (legacy JSON-RPC)"
                        if self.mcp_config.http_mode == "sdk":
                            endpoints += f", {SDK_PATH} (MCP SDK streamable HTTP)"
                    self.logger.info(
                        f"Starting server with {transport} transport on http://{host}:{port} "
                        f"- endpoints: {endpoints}; auth: "
                        f"{'bearer token' if self.mcp_config.auth_token else 'none'}"
                    )
                    uvicorn_server = uvicorn.Server(
                        uvicorn.Config(app, host=host, port=port, log_level="info")
                    )
                    await uvicorn_server.serve()

                else:
                    raise ValueError(f"Unsupported transport: {transport}")
        
        except Exception as e:
            self.logger.error(f"Error running server: {e}")
            raise


def main() -> None:
    """Main server entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="WithSecure Elements MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport type to use"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="IP address for HTTP transports (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transports (default: 8000)"
    )
    parser.add_argument(
        "--modules",
        help="Modules to enable (comma-separated)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--base-url",
        help="WithSecure Elements API base URL"
    )
    
    args = parser.parse_args()
    
    # Parse modules
    enabled_modules = None
    if args.modules:
        enabled_modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    
    # Create and run server
    server = WithSecureElementsMCPServer(
        base_url=args.base_url,
        debug=args.debug,
        enabled_modules=enabled_modules
    )
    
    try:
        asyncio.run(server.run(args.transport, args.host, args.port))
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

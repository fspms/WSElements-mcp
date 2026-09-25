"""
Tests for the HTTP transport: optional bearer token and optional MCP SDK endpoint.
"""

from starlette.testclient import TestClient

from withsecure_elements_mcp.auth import WithSecureAuth
from withsecure_elements_mcp.config import WithSecureConfig
from withsecure_elements_mcp.http_app import build_streamable_http_app
from withsecure_elements_mcp.server import WithSecureElementsMCPServer

import asyncio

LIST_TOOLS = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
SDK_HEADERS = {"Accept": "application/json, text/event-stream"}
INITIALIZE = {
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}},
}


def _client(token=None, http_mode="legacy") -> TestClient:
    server = WithSecureElementsMCPServer(enabled_modules=["incidents"])
    server.mcp_config.auth_token = token
    server.mcp_config.http_mode = http_mode
    server.auth = WithSecureAuth(WithSecureConfig(client_id="x", client_secret="y"))
    asyncio.run(server._initialize_modules())
    server._register_central_handlers()
    return TestClient(build_streamable_http_app(server))


def test_legacy_without_token_is_open_and_has_no_sdk_endpoint():
    with _client() as client:
        response = client.post("/", json=LIST_TOOLS)
        assert response.status_code == 200
        assert any(t["name"] == "list_incident_detections" for t in response.json()["result"]["tools"])
        assert client.post("/mcp", json=INITIALIZE, headers=SDK_HEADERS).status_code == 404


def test_token_is_enforced_when_configured():
    with _client(token="s3cret") as client:
        assert client.post("/", json=LIST_TOOLS).status_code == 401
        assert client.post("/", json=LIST_TOOLS, headers={"Authorization": "Bearer nope"}).status_code == 401
        ok = client.post("/", json=LIST_TOOLS, headers={"Authorization": "Bearer s3cret"})
        assert ok.status_code == 200
        # Health checks and CORS preflight stay public.
        assert client.get("/health").status_code == 200
        preflight = client.options("/", headers={
            "Origin": "https://n8n.example", "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        })
        assert preflight.status_code == 200


def test_sdk_mode_serves_official_transport_alongside_legacy():
    auth = {"Authorization": "Bearer s3cret"}
    with _client(token="s3cret", http_mode="sdk") as client:
        assert client.post("/mcp", json=INITIALIZE, headers=SDK_HEADERS).status_code == 401
        response = client.post("/mcp", json=INITIALIZE, headers={**SDK_HEADERS, **auth})
        assert response.status_code == 200
        assert "withsecure-elements-mcp" in response.text
        # Legacy endpoint keeps working in sdk mode.
        assert client.post("/", json=LIST_TOOLS, headers=auth).status_code == 200

"""
Tests that the central MCP handlers expose tools from every enabled module.

This guards against the single-handler-per-server pitfall: each module must not
overwrite another's tool registration, so the full tool surface is available on
every transport (stdio included).
"""

import pytest

from withsecure_elements_mcp.server import WithSecureElementsMCPServer
from withsecure_elements_mcp.auth import WithSecureAuth
from withsecure_elements_mcp.config import WithSecureConfig
import mcp.types as t


async def _build_server() -> WithSecureElementsMCPServer:
    server = WithSecureElementsMCPServer()
    server.auth = WithSecureAuth(WithSecureConfig(client_id="x", client_secret="y"))
    await server._initialize_modules()
    server._register_central_handlers()
    return server


@pytest.mark.asyncio
async def test_all_modules_expose_tools():
    """Every module must contribute at least one signature tool."""
    server = await _build_server()
    handler = server.server.request_handlers[t.ListToolsRequest]
    result = await handler(t.ListToolsRequest(method="tools/list"))
    names = {tool.name for tool in result.root.tools}

    expected = [
        "list_incidents",            # incidents
        "list_events",               # events
        "list_organizations",        # organizations
        "list_devices",              # devices
        "list_response_actions_responses",  # response_actions
        "install_software_updates",  # software_updates
    ]
    for tool_name in expected:
        assert tool_name in names, f"missing tool {tool_name} (module collision?)"

    # No duplicate tool names across modules.
    all_names = [tool.name for tool in result.root.tools]
    assert len(all_names) == len(set(all_names)), "duplicate tool names exposed"


@pytest.mark.asyncio
async def test_tool_input_schemas_are_valid():
    """Each tool inputSchema must be a valid JSON Schema."""
    import jsonschema

    server = await _build_server()
    handler = server.server.request_handlers[t.ListToolsRequest]
    result = await handler(t.ListToolsRequest(method="tools/list"))
    for tool in result.root.tools:
        jsonschema.Draft7Validator.check_schema(tool.inputSchema)


@pytest.mark.asyncio
async def test_tool_annotations():
    """Read tools are read-only; disruptive tools are flagged destructive."""
    server = await _build_server()
    handler = server.server.request_handlers[t.ListToolsRequest]
    result = await handler(t.ListToolsRequest(method="tools/list"))
    by_name = {tool.name: tool for tool in result.root.tools}

    assert by_name["list_devices"].annotations.readOnlyHint is True
    assert by_name["get_incident"].annotations.readOnlyHint is True
    for destructive in ("isolate_device", "restart_system", "scan_device"):
        assert by_name[destructive].annotations.destructiveHint is True


@pytest.mark.asyncio
async def test_unknown_tool_returns_error():
    """Calling an unknown tool yields an error result rather than crashing."""
    server = await _build_server()
    handler = server.server.request_handlers[t.CallToolRequest]
    req = t.CallToolRequest(
        method="tools/call",
        params=t.CallToolRequestParams(name="nope", arguments={}),
    )
    result = await handler(req)
    assert result.root.isError is True

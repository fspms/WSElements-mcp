"""
Tests for the incidents module against a mocked WithSecure API.
"""

import json
import time

import httpx
import pytest
import mcp.types as t

from withsecure_elements_mcp.auth import WithSecureAuth
from withsecure_elements_mcp.config import WithSecureConfig
from withsecure_elements_mcp.modules.incidents import IncidentsModule
from withsecure_elements_mcp.server import WithSecureElementsMCPServer


def _module(handler) -> IncidentsModule:
    auth = WithSecureAuth(WithSecureConfig(client_id="x", client_secret="y"))
    auth._client = httpx.AsyncClient(
        base_url="https://api.test", transport=httpx.MockTransport(handler)
    )
    auth._token = "tok"
    auth._token_expires_at = time.time() + 3600
    module = IncidentsModule.__new__(IncidentsModule)
    module.auth, module.config = auth, auth.config
    module._tools, module._resources = [], []
    module._register_tools()
    return module


def _text(result) -> dict:
    return json.loads(result["content"][0]["text"])


@pytest.mark.asyncio
async def test_list_incidents_params_follow_api_spec():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["params"] = request.url.params
        return httpx.Response(200, json={"items": []})

    module = _module(handler)
    await module.call_tool(
        "list_incidents",
        {"limit": 100, "status": ["new", "inProgress"], "severity": "critical", "source": ["endpoint", "cloud"]},
    )
    params = seen["params"]
    assert params["limit"] == "50"  # API maximum
    assert params.get_list("status") == ["new", "inProgress"]
    assert params.get_list("riskLevel") == ["severe"]  # legacy severity alias
    assert params["source"] == "endpoint,cloud"
    assert "severity" not in params


@pytest.mark.asyncio
async def test_list_incident_detections_fetch_all_follows_pagination():
    pages = {
        None: {"items": [{"detectionId": "1", "activityContext": [{"type": "x"}]}], "nextAnchor": "a2"},
        "a2": {"items": [{"detectionId": "2"}], "nextAnchor": "a3"},
        "a3": {"items": [{"detectionId": "3"}]},
    }
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/incidents/v1/detections"
        assert request.url.params["incidentId"] == "bcd-1"
        anchor = request.url.params.get("anchor")
        calls.append(anchor)
        return httpx.Response(200, json=pages[anchor])

    module = _module(handler)
    result = _text(await module.call_tool(
        "list_incident_detections",
        {"incident_id": "bcd-1", "fetch_all": True, "include_activity_context": False},
    ))
    assert calls == [None, "a2", "a3"]
    assert [d["detectionId"] for d in result["items"]] == ["1", "2", "3"]
    assert result["count"] == 3 and result["complete"] is True
    assert "activityContext" not in result["items"][0]


@pytest.mark.asyncio
async def test_list_incident_detections_fetch_all_respects_max_items():
    def handler(request: httpx.Request) -> httpx.Response:
        limit = int(request.url.params["limit"])
        return httpx.Response(200, json={"items": [{"detectionId": "d"}] * limit, "nextAnchor": "more"})

    module = _module(handler)
    result = _text(await module.call_tool(
        "list_incident_detections", {"incident_id": "bcd-1", "fetch_all": True, "max_items": 150},
    ))
    assert result["count"] == 150
    assert result["complete"] is False and result["nextAnchor"] == "more"


@pytest.mark.asyncio
async def test_update_status_multistatus_failure_is_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(207, json={"multistatus": [{"target": "bcd-1", "status": 404}]})

    module = _module(handler)
    result = await module.call_tool(
        "update_incident_status", {"incident_id": "bcd-1", "status": "inProgress"}
    )
    assert result["isError"] is True


@pytest.mark.asyncio
async def test_get_incident_updates():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/incidents/v1/updates"
        assert request.url.params["type"] == "comment"
        return httpx.Response(200, json={"items": [{"id": "u1", "type": "comment"}]})

    module = _module(handler)
    result = _text(await module.call_tool(
        "get_incident_updates", {"incident_id": "bcd-1", "type": "comment"}
    ))
    assert result["items"][0]["id"] == "u1"


@pytest.mark.asyncio
async def test_central_handler_preserves_is_error():
    server = WithSecureElementsMCPServer(enabled_modules=["incidents"])
    server.modules = [_module(lambda r: httpx.Response(500, text="boom"))]
    server._register_central_handlers()
    handler = server.server.request_handlers[t.CallToolRequest]
    result = await handler(t.CallToolRequest(
        method="tools/call",
        params=t.CallToolRequestParams(name="get_incident", arguments={"incident_id": "bcd-1"}),
    ))
    assert result.root.isError is True

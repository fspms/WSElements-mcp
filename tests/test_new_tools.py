"""
Request-shape tests for the write/admin tools, against a mocked WithSecure API.
"""

import json
import time

import httpx
import pytest

from withsecure_elements_mcp.auth import WithSecureAuth
from withsecure_elements_mcp.config import WithSecureConfig
from withsecure_elements_mcp.modules.devices import DevicesModule
from withsecure_elements_mcp.modules.management import ManagementModule
from withsecure_elements_mcp.modules.response_actions import ResponseActionsModule


def _module(cls, handler, organization_id=None):
    config = WithSecureConfig(client_id="x", client_secret="y", organization_id=organization_id)
    auth = WithSecureAuth(config)
    auth._client = httpx.AsyncClient(base_url="https://api.test", transport=httpx.MockTransport(handler))
    auth._token, auth._token_expires_at = "tok", time.time() + 3600
    module = cls.__new__(cls)
    module.auth, module.config = auth, config
    module._tools, module._resources = [], []
    return module


def _recorder(status=200, body=None):
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(status, json=body if body is not None else {})

    return seen, handler


@pytest.mark.asyncio
async def test_update_devices_sends_single_change():
    seen, handler = _recorder(207, {"multistatus": []})
    module = _module(DevicesModule, handler)
    result = await module.call_tool("update_devices", {"device_ids": ["d1", "d2"], "importance": "critical"})
    assert not result.get("isError")
    req = seen[0]
    assert req.method == "PATCH" and req.url.path == "/devices/v1/devices"
    assert json.loads(req.content) == {"targets": ["d1", "d2"], "importance": "critical"}


@pytest.mark.asyncio
async def test_update_devices_rejects_ambiguous_or_invalid_changes():
    seen, handler = _recorder()
    module = _module(DevicesModule, handler)
    both = await module.call_tool("update_devices", {"device_ids": ["d1"], "state": "blocked", "alias": "x"})
    alias_many = await module.call_tool("update_devices", {"device_ids": ["d1", "d2"], "alias": "x"})
    assert both["isError"] and alias_many["isError"]
    assert seen == []  # nothing sent to the API


@pytest.mark.asyncio
async def test_delete_devices_uses_repeated_query_params():
    seen, handler = _recorder(200, {"devices": ["d1", "d2"]})
    module = _module(DevicesModule, handler)
    await module.call_tool("delete_devices", {"device_ids": ["d1", "d2"]})
    req = seen[0]
    assert req.method == "DELETE"
    assert req.url.params.get_list("deviceId") == ["d1", "d2"]


@pytest.mark.asyncio
async def test_response_action_tasks_requires_org_and_sends_action():
    seen, handler = _recorder(200, {"items": []})
    no_org = await _module(ResponseActionsModule, handler).call_tool("get_response_action_tasks", {"action_id": "a"})
    assert no_org["isError"] and seen == []
    await _module(ResponseActionsModule, handler, "org-1").call_tool(
        "get_response_action_tasks", {"action_id": "a", "limit": 500}
    )
    params = seen[0].url.params
    assert params["organizationId"] == "org-1" and params["actionId"] == "a" and params["limit"] == "100"


@pytest.mark.asyncio
async def test_audit_logs_rejects_end_without_start():
    seen, handler = _recorder()
    result = await _module(ManagementModule, handler).call_tool(
        "list_audit_logs", {"server_timestamp_end": "2026-09-01T00:00:00Z"}
    )
    assert result["isError"] and seen == []


@pytest.mark.asyncio
async def test_create_invitation_body():
    seen, handler = _recorder(200, {"items": []})
    await _module(ManagementModule, handler, "org-1").call_tool(
        "create_invitation", {"email": "a@b.c", "subscription_key": "KEY", "language": "fr_FR"}
    )
    body = json.loads(seen[0].content)
    assert body == {
        "organizationId": "org-1",
        "invitations": [{"email": "a@b.c", "subscriptionKey": "KEY", "language": "fr_FR"}],
    }


@pytest.mark.asyncio
async def test_renew_invitations_handles_204():
    def handler(request):
        assert request.method == "PUT"
        return httpx.Response(204)

    result = await _module(ManagementModule, handler, "org-1").call_tool(
        "renew_invitations", {"invitation_ids": ["i1"], "operation": "renew"}
    )
    assert json.loads(result["content"][0]["text"])["success"] is True

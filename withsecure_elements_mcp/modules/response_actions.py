"""
MCP module for WithSecure Elements response actions management.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from .base import BaseModule


# Actions exposed by POST /response-actions/v1/execute/{action} (also the
# `type` filter enum of GET /response-actions/v1/responses).
RESPONSE_ACTION_TYPES = [
    "blockUserAccess",
    "deleteRegistry",
    "deleteScheduledTasks",
    "deleteServices",
    "deleteWmiPersistence",
    "endCurrentSession",
    "enumerateProcesses",
    "enumerateScheduledTasks",
    "enumerateWmiPersistence",
    "fullMemoryDump",
    "mapFileSystem",
    "mapRegistry",
    "netstat",
    "processMemoryDump",
    "resetPassword",
    "retrieveAmcache",
    "retrieveAntivirusLogs",
    "retrieveBrowserArtefacts",
    "retrieveEventLogFiles",
    "retrieveEventLogTracing",
    "retrieveFiles",
    "retrieveJumpList",
    "retrieveLogEntries",
    "retrieveMbr",
    "retrieveMft",
    "retrievePrefetch",
    "retrieveRdpCache",
    "retrieveRecentlyAccessed",
    "retrieveRegistryHives",
    "retrieveSrumdb",
    "terminateProcess",
    "terminateThread",
]

RESPONSES_MAX_LIMIT = 100
TASKS_MAX_LIMIT = 100
TASK_STATES = [
    "pending", "sent", "cancellationSent", "cancellationAcknowledged", "received",
    "acknowledged", "running", "stopped", "finished", "canceling",
]
TASK_RESULTS = ["succeeded", "failed", "timeout", "canceled"]


class ResponseActionFilters(BaseModel):
    """Filters for response actions search."""

    organization_id: Optional[str] = None
    order: Optional[str] = "desc"
    anchor: Optional[str] = None
    limit: Optional[int] = 100
    type: Optional[str] = None
    action_id: Optional[str] = None
    state: Optional[str] = None
    result: Optional[str] = None
    device_id: Optional[str] = None


class ResponseActionCreate(BaseModel):
    """Model for creating response actions."""

    targets: List[str]
    organization_id: Optional[str] = None
    action_type: str
    comment: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ResponseActionsModule(BaseModule):
    """Module for response actions management."""

    @property
    def name(self) -> str:
        return "response_actions"

    @property
    def description(self) -> str:
        return "WithSecure Elements response actions management"

    def _register_resources(self) -> None:
        """Register resources for response actions."""

        # Add resources to the list for HTTP transport
        self._resources.extend([
            {
                "uri": "withsecure://response-actions/responses",
                "name": "Response Actions Responses",
                "description": "WithSecure Elements response actions responses",
                "mimeType": "application/json"
            }
        ])

    def _register_tools(self) -> None:
        """Register tools for response actions."""

        # Add tools to the list for HTTP transport
        self._tools.extend([
            {
                "name": "list_response_actions_responses",
                "description": "List response actions and their status (paginated via anchor/nextAnchor)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization UUID (defaults to configured org)"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "default": "desc"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": RESPONSES_MAX_LIMIT,
                            "default": 100
                        },
                        "anchor": {
                            "type": "string",
                            "description": "nextAnchor from previous page"
                        },
                        "type": {
                            "type": "string",
                            "enum": RESPONSE_ACTION_TYPES,
                            "description": "Filter by action type"
                        },
                        "action_id": {
                            "type": "string",
                            "description": "Filter by action UUID"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["created", "initializing", "sending", "running", "canceling", "finished"]
                        },
                        "result": {
                            "type": "string",
                            "enum": ["succeeded", "failed", "timeout", "cancelled"]
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Filter by device UUID"
                        }
                    }
                }
            },
            {
                "name": "create_response_action",
                "description": "Execute a response action on devices (or Entra tenants for identity actions). Returns the action id; track it with list_response_actions_responses",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "minItems": 1,
                            "maxItems": 10,
                            "description": "Device IDs (Entra tenant IDs for blockUserAccess/endCurrentSession/resetPassword)"
                        },
                        "organization_id": {
                            "type": "string",
                            "description": "Organization UUID (defaults to configured org)"
                        },
                        "action_type": {
                            "type": "string",
                            "enum": RESPONSE_ACTION_TYPES,
                            "description": "Response action to execute"
                        },
                        "comment": {
                            "type": "string",
                            "description": "Comment for the action"
                        },
                        "parameters": {
                            "type": "object",
                            "description": (
                                "Action-specific parameters, e.g. terminateProcess {os:windows|mac|linux|mac_or_linux, "
                                "match:processIds|processNames|processNameRegexes|processPaths|processPathRegexes, <match>:[...]}; "
                                "terminateThread {threadId:int}; netstat {maxFileSizeToHashMB}; "
                                "fullMemoryDump {winpmemVersion:v1_6|v2_1} (Windows) or {captureMemory,collectProfile} (Linux); "
                                "processMemoryDump {match:processId|processName, processId|processName, flags:full|pmem}; "
                                "retrieveFiles {match:pathBasic|pathRegex, pathBasic|pathRegex, pathStructure:all|sub|none, maxFiles}; "
                                "retrieveMbr/retrieveMft {drive}; identity actions {userPrincipal}"
                            )
                        }
                    },
                    "required": ["targets", "action_type"]
                }
            },
            {
                "name": "get_response_action_tasks",
                "description": "Per-device tasks of a response action: execution state, result and "
                               "output files (attachments)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action_id": {"type": "string", "description": "Response action UUID"},
                        "organization_id": {"type": "string", "description": "Organization UUID (defaults to configured org)"},
                        "device_id": {"type": "string", "description": "Filter by device UUID"},
                        "state": {"type": "string", "enum": TASK_STATES},
                        "result": {"type": "string", "enum": TASK_RESULTS},
                        "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": TASKS_MAX_LIMIT, "default": 10},
                        "anchor": {"type": "string", "description": "nextAnchor from a previous response"}
                    },
                    "required": ["action_id"]
                }
            }
        ])

    async def _get_response_actions_responses(self, filters: ResponseActionFilters) -> str:
        """Retrieve response actions responses list."""
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        organization_id = filters.organization_id or self.config.organization_id
        if not organization_id:
            raise ValueError("organization_id is required")

        headers = await self.auth.get_headers()
        params = {
            "organizationId": organization_id,
            "order": filters.order or "desc",
            "limit": max(1, min(filters.limit or 100, RESPONSES_MAX_LIMIT))
        }

        optional = {
            "anchor": filters.anchor,
            "type": filters.type,
            "actionId": filters.action_id,
            "state": filters.state,
            "result": filters.result,
            "deviceId": filters.device_id,
        }
        params.update({k: v for k, v in optional.items() if v})

        response = await self.auth._client.get(
            "/response-actions/v1/responses",
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            raise Exception(f"Error retrieving response actions responses: {response.status_code} - {response.text}")

        return self._dump(response.json())

    async def _create_response_action(self, action_data: ResponseActionCreate) -> str:
        """Execute a response action via POST /response-actions/v1/execute/{action}."""
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        if action_data.action_type not in RESPONSE_ACTION_TYPES:
            raise ValueError(
                f"Unsupported action_type '{action_data.action_type}'. Allowed: {', '.join(RESPONSE_ACTION_TYPES)}"
            )
        if not 1 <= len(action_data.targets) <= 10:
            raise ValueError("targets must contain 1 to 10 items")

        organization_id = action_data.organization_id or self.config.organization_id
        if not organization_id:
            raise ValueError("organization_id is required")

        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"

        data = {
            "organizationId": organization_id,
            "targets": action_data.targets
        }

        if action_data.comment:
            data["comment"] = action_data.comment
        if action_data.parameters:
            data["parameters"] = action_data.parameters

        response = await self.auth._client.post(
            f"/response-actions/v1/execute/{action_data.action_type}",
            headers=headers,
            json=data
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Error creating response action: {response.status_code} - {response.text}")

        return self._dump(response.json())

    async def _get_response_action_tasks(self, arguments: Dict[str, Any]) -> str:
        """Retrieve tasks of a response action (GET /response-actions/v1/responses/tasks)."""
        organization_id = self._org_id(arguments.get("organization_id"))
        if not organization_id:
            raise ValueError("organization_id is required")
        params = {
            "organizationId": organization_id,
            "actionId": arguments["action_id"],
            "deviceId": arguments.get("device_id"),
            "state": arguments.get("state"),
            "result": arguments.get("result"),
            "order": arguments.get("order"),
            "limit": max(1, min(int(arguments.get("limit") or 10), TASKS_MAX_LIMIT)),
            "anchor": arguments.get("anchor"),
        }
        data = await self._get_json("/response-actions/v1/responses/tasks", params, "response action tasks")
        return self._dump(data)

    async def read_resource(self, uri: str) -> Optional[str]:
        """Read a response action resource."""
        if uri == "withsecure://response-actions/responses":
            return await self._get_response_actions_responses(ResponseActionFilters())
        return None

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        try:
            if tool_name == "list_response_actions_responses":
                filters = ResponseActionFilters(**arguments)
                responses = await self._get_response_actions_responses(filters)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": responses
                        }
                    ]
                }

            elif tool_name == "create_response_action":
                action_data = ResponseActionCreate(**arguments)
                result = await self._create_response_action(action_data)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }

            elif tool_name == "get_response_action_tasks":
                result = await self._get_response_action_tasks(arguments)
                return {"content": [{"type": "text", "text": result}]}

            else:
                return None

        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }

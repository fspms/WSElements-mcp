"""
MCP module for WithSecure Elements devices management.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from .base import BaseModule


# GET /devices/v1/devices: limit min 1, max 200 (spec default 200).
DEVICES_LIMIT_MIN = 1
DEVICES_LIMIT_MAX = 200
DEVICES_LIMIT_DEFAULT = 100

# POST /devices/v1/operations: 1-5 targets per request.
OPERATION_TARGETS_MAX = 5
OPERATION_MESSAGE_MAX_LENGTH = 512

DEVICE_TYPES = ["computer", "connector", "mobile"]
DEVICE_STATES = ["active", "blocked", "inactive"]
PROTECTION_STATUS_OVERVIEWS = ["isolated", "inactive", "critical", "warning", "allOk"]
PATCH_OVERALL_STATES = [
    "missingCriticalUpdates",
    "missingImportantUpdates",
    "importantUpdatesInstalled",
    "disabled",
    "outdatedScanResults",
    "notScannedYet",
]
COUNT_PROPERTIES = ["protectionStatus", "patchOverallState", "firewallState", "malwareState"]
HISTOGRAM_PROPERTIES = ["protectionStatus"]

AGGREGATION_ACCEPT = "application/vnd.withsecure.aggr+json"

# PATCH /devices/v1/devices: exactly one change per request, 1-5 targets
# (alias: a single target). DELETE: up to 20 devices.
DEVICE_UPDATE_FIELDS = {
    "state": "state",
    "subscription_key": "subscriptionKey",
    "alias": "alias",
    "importance": "importance",
    "business_context": "businessContext",
    "labels": "labels",
}
UPDATE_STATES = ["blocked", "inactive"]
DEVICE_IMPORTANCES = ["critical", "normal", "minor"]
DELETE_DEVICES_MAX = 20

_DEVICE_IDS_SCHEMA = {
    "type": "array",
    "items": {"type": "string"},
    "minItems": 1,
    "maxItems": OPERATION_TARGETS_MAX,
    "description": "Device IDs (1-5)"
}



def _clamp_limit(limit: Optional[int]) -> int:
    """Clamp a page size to the API bounds."""
    if limit is None:
        return DEVICES_LIMIT_DEFAULT
    return max(DEVICES_LIMIT_MIN, min(DEVICES_LIMIT_MAX, int(limit)))


class DeviceFilters(BaseModel):
    """Filters for device search (query parameters of GET /devices/v1/devices)."""

    organization_id: Optional[str] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    state: Optional[str] = None
    online: Optional[bool] = None
    protection_status_overview: Optional[str] = None
    patch_overall_state: Optional[str] = None
    label: Optional[str] = None
    os_name: Optional[str] = None
    serial_number: Optional[str] = None
    public_ip_address: Optional[str] = None
    limit: Optional[int] = DEVICES_LIMIT_DEFAULT
    anchor: Optional[str] = None


class DevicesModule(BaseModule):
    """Module for devices management."""

    @property
    def name(self) -> str:
        return "devices"

    @property
    def description(self) -> str:
        return "WithSecure Elements devices management"

    def _register_resources(self) -> None:
        """Register resources for devices."""
        self._resources.append({
            "uri": "withsecure://devices",
            "name": "Devices",
            "description": "WithSecure Elements devices list",
            "mimeType": "application/json"
        })

    def _register_tools(self) -> None:
        """Register tools for devices."""
        self._tools.extend([
            {
                "name": "list_devices",
                "description": "List devices (filters combine with AND; deviceId overrides other filters)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {"type": "string", "description": "Organization UUID"},
                        "device_id": {"type": "string", "description": "Device UUID"},
                        "device_name": {"type": "string", "maxLength": 255, "description": "Device name"},
                        "device_type": {"type": "string", "enum": DEVICE_TYPES},
                        "state": {"type": "string", "enum": DEVICE_STATES},
                        "online": {"type": "boolean"},
                        "protection_status_overview": {"type": "string", "enum": PROTECTION_STATUS_OVERVIEWS},
                        "patch_overall_state": {"type": "string", "enum": PATCH_OVERALL_STATES},
                        "label": {"type": "string", "maxLength": 255},
                        "os_name": {"type": "string", "maxLength": 128},
                        "serial_number": {"type": "string", "maxLength": 128},
                        "public_ip_address": {"type": "string", "maxLength": 45},
                        "limit": {
                            "type": "integer",
                            "minimum": DEVICES_LIMIT_MIN,
                            "maximum": DEVICES_LIMIT_MAX,
                            "default": DEVICES_LIMIT_DEFAULT
                        },
                        "anchor": {
                            "type": "string",
                            "maxLength": 512,
                            "description": "nextAnchor from previous page"
                        }
                    }
                }
            },
            {
                "name": "get_device",
                "description": "Get one device by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device UUID"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "isolate_device",
                "description": "Isolate a computer from the network",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device UUID"},
                        "reason": {
                            "type": "string",
                            "maxLength": OPERATION_MESSAGE_MAX_LENGTH,
                            "description": "Message shown on the host before isolation"
                        }
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "unisolate_device",
                "description": "Release a computer from network isolation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device UUID"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "scan_device",
                "description": "Run a malware scan on a computer or mobile",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device UUID"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "show_message",
                "description": "Show a message on a computer or mobile",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device UUID"},
                        "message": {"type": "string", "maxLength": OPERATION_MESSAGE_MAX_LENGTH}
                    },
                    "required": ["device_id", "message"]
                }
            },
            {
                "name": "assign_profile",
                "description": "Assign a profile to a device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device UUID"},
                        "profile_id": {"type": "integer", "description": "Profile ID"}
                    },
                    "required": ["device_id", "profile_id"]
                }
            },
            {
                "name": "get_device_operations",
                "description": "List remote operations triggered on a device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device UUID"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "get_device_operation_status",
                "description": "Get status of one operation on a device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device UUID"},
                        "operation_id": {"type": "string", "description": "operationId from the trigger response"}
                    },
                    "required": ["device_id", "operation_id"]
                }
            },
            {
                "name": "get_device_statistics",
                "description": "Count devices grouped by a property",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "string", "enum": COUNT_PROPERTIES, "description": "Group-by property"},
                        "organization_id": {"type": "string", "description": "Organization UUID"},
                        "device_type": {"type": "string", "enum": DEVICE_TYPES},
                        "device_name": {"type": "string", "maxLength": 255},
                        "online": {"type": "boolean"},
                        "label": {"type": "string", "maxLength": 255},
                        "protection_status_overview": {"type": "string", "enum": PROTECTION_STATUS_OVERVIEWS}
                    },
                    "required": ["count"]
                }
            },
            {
                "name": "get_device_histogram",
                "description": "Daily device counts by property over the last 30 days",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "histogram": {
                            "type": "string",
                            "enum": HISTOGRAM_PROPERTIES,
                            "default": "protectionStatus"
                        },
                        "organization_id": {"type": "string", "description": "Organization UUID"},
                        "device_type": {"type": "string", "enum": DEVICE_TYPES}
                    }
                }
            },
            {
                "name": "send_full_status",
                "description": "Request a full status update from computers/mobiles",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": _DEVICE_IDS_SCHEMA
                    },
                    "required": ["device_ids"]
                }
            },
            {
                "name": "restart_system",
                "description": "Restart Windows computers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": _DEVICE_IDS_SCHEMA,
                        "message": {
                            "type": "string",
                            "maxLength": OPERATION_MESSAGE_MAX_LENGTH,
                            "description": "Message shown before restart"
                        }
                    },
                    "required": ["device_ids"]
                }
            },
            {
                "name": "update_devices",
                "description": "Change devices: set exactly ONE of state (block/deactivate), "
                               "subscription_key, alias (single device), importance, business_context "
                               "or labels (replaces existing labels)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": _DEVICE_IDS_SCHEMA,
                        "state": {"type": "string", "enum": UPDATE_STATES},
                        "subscription_key": {"type": "string", "description": "Target subscription key"},
                        "alias": {"type": "string", "description": "Custom device name (1 device only)"},
                        "importance": {"type": "string", "enum": DEVICE_IMPORTANCES},
                        "business_context": {"type": "string"},
                        "labels": {
                            "type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 64
                        }
                    },
                    "required": ["device_ids"]
                }
            },
            {
                "name": "delete_devices",
                "description": "Delete devices from the organization (frees subscription seats; the "
                               "product must be reinstalled to protect them again)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": {
                            "type": "array", "items": {"type": "string"},
                            "minItems": 1, "maxItems": DELETE_DEVICES_MAX,
                            "description": "Device IDs (1-20)"
                        }
                    },
                    "required": ["device_ids"]
                }
            },
        ])

    def _org_id(self, organization_id: Optional[str] = None) -> Optional[str]:
        """Resolve the organization ID (explicit value, else configured default)."""
        return organization_id or self.config.organization_id

    async def _get(self, path: str, params: Dict[str, Any], accept: Optional[str] = None) -> Any:
        """GET a JSON resource from the API."""
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        headers = await self.auth.get_headers()
        if accept:
            headers["Accept"] = accept

        response = await self.auth._client.get(path, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Error calling GET {path}: {response.status_code} - {response.text}")

        return response.json()

    async def _get_devices(self, filters: Optional[DeviceFilters] = None) -> str:
        """Retrieve devices list."""
        filters = filters or DeviceFilters()
        params: Dict[str, Any] = {"limit": _clamp_limit(filters.limit)}

        org_id = self._org_id(filters.organization_id)
        if org_id:
            params["organizationId"] = org_id

        mapping = {
            "deviceId": filters.device_id,
            "name": filters.device_name,
            "type": filters.device_type,
            "state": filters.state,
            "protectionStatusOverview": filters.protection_status_overview,
            "patchOverallState": filters.patch_overall_state,
            "label": filters.label,
            "osName": filters.os_name,
            "serialNumber": filters.serial_number,
            "publicIpAddress": filters.public_ip_address,
            "anchor": filters.anchor,
        }
        params.update({k: v for k, v in mapping.items() if v})
        if filters.online is not None:
            params["online"] = "true" if filters.online else "false"

        return self._dump(await self._get("/devices/v1/devices", params))

    async def _get_device(self, device_id: str) -> str:
        """Retrieve details of a specific device.

        The Elements API has no /devices/{id} sub-resource; a single device is
        fetched from the list endpoint filtered by the deviceId query parameter.
        """
        params = {"deviceId": device_id}
        org_id = self._org_id()
        if org_id:
            params["organizationId"] = org_id

        return self._dump(await self._get("/devices/v1/devices", params))

    async def _device_operation(self, operation: str, targets: List[str], parameters: Optional[Dict[str, Any]] = None) -> str:
        """Trigger a remote operation on devices via POST /devices/v1/operations.

        The API answers 207 Multi-Status with a per-target status in "multistatus".
        """
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        if isinstance(targets, str):
            targets = [targets]
        if not targets or len(targets) > OPERATION_TARGETS_MAX:
            raise ValueError(f"targets must contain 1-{OPERATION_TARGETS_MAX} device IDs")

        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"

        data: Dict[str, Any] = {
            "operation": operation,
            "targets": targets,
        }
        if parameters:
            data["parameters"] = parameters

        response = await self.auth._client.post(
            "/devices/v1/operations",
            headers=headers,
            json=data
        )

        if response.status_code not in (200, 202, 207):
            raise Exception(f"Error triggering {operation}: {response.status_code} - {response.text}")

        return self._dump(response.json())

    async def _isolate_device(self, device_id: str, reason: Optional[str] = None) -> str:
        """Isolate a device from the network (operation: isolateFromNetwork)."""
        return await self._device_operation(
            "isolateFromNetwork", [device_id], {"message": reason} if reason else None
        )

    async def _unisolate_device(self, device_id: str) -> str:
        """Release a device from network isolation (operation: releaseFromNetworkIsolation)."""
        return await self._device_operation("releaseFromNetworkIsolation", [device_id])

    async def _scan_device(self, device_id: str) -> str:
        """Launch a malware scan on a device (operation: scanForMalware, no parameters)."""
        return await self._device_operation("scanForMalware", [device_id])

    async def _show_message(self, device_id: str, message: str) -> str:
        """Show message to device user (operation: showMessage)."""
        return await self._device_operation("showMessage", [device_id], {"message": message})

    async def _assign_profile(self, device_id: str, profile_id: int) -> str:
        """Assign profile to device (operation: assignProfile)."""
        return await self._device_operation("assignProfile", [device_id], {"profileId": profile_id})

    async def _send_full_status(self, device_ids: List[str]) -> str:
        """Request a full status update from devices (operation: sendFullStatus)."""
        return await self._device_operation("sendFullStatus", device_ids)

    async def _restart_system(self, device_ids: List[str], message: Optional[str] = None) -> str:
        """Restart Windows computers (operation: restartSystem)."""
        return await self._device_operation(
            "restartSystem", device_ids, {"message": message} if message else None
        )

    async def _update_devices(self, device_ids: List[str], changes: Dict[str, Any]) -> str:
        """Apply one change to devices via PATCH /devices/v1/devices (207 Multi-Status)."""
        provided = {k: v for k, v in changes.items() if k in DEVICE_UPDATE_FIELDS and v not in (None, "", [])}
        if len(provided) != 1:
            raise ValueError(
                f"Provide exactly one of: {', '.join(DEVICE_UPDATE_FIELDS)} (got {len(provided)})"
            )
        field, value = next(iter(provided.items()))
        targets = [device_ids] if isinstance(device_ids, str) else list(device_ids or [])
        max_targets = 1 if field == "alias" else OPERATION_TARGETS_MAX
        if not 1 <= len(targets) <= max_targets:
            raise ValueError(f"device_ids must contain 1-{max_targets} device IDs for '{field}'")
        body = {"targets": targets, DEVICE_UPDATE_FIELDS[field]: value}
        return self._dump(await self._send(
            "PATCH", "/devices/v1/devices", "updating devices", ok=(200, 207), body=body
        ))

    async def _delete_devices(self, device_ids: List[str]) -> str:
        """Delete devices via DELETE /devices/v1/devices."""
        targets = [device_ids] if isinstance(device_ids, str) else list(device_ids or [])
        if not 1 <= len(targets) <= DELETE_DEVICES_MAX:
            raise ValueError(f"device_ids must contain 1-{DELETE_DEVICES_MAX} device IDs")
        return self._dump(await self._send(
            "DELETE", "/devices/v1/devices", "deleting devices", params={"deviceId": targets}
        ))

    async def _list_device_operations(self, device_id: str) -> List[Dict[str, Any]]:
        """List operations of a device (GET /devices/v1/operations; only deviceId is accepted)."""
        result = await self._get("/devices/v1/operations", {"deviceId": device_id})
        return result.get("items", []) if isinstance(result, dict) else []

    async def _get_device_operations(self, device_id: str) -> str:
        """Get device operations list."""
        return self._dump({"items": await self._list_device_operations(device_id)})

    async def _get_device_operation_status(self, device_id: str, operation_id: str) -> str:
        """Get one operation status; the API has no operationId filter, so match client-side."""
        for item in await self._list_device_operations(device_id):
            if str(item.get("id")) == str(operation_id):
                return self._dump(item)
        raise Exception(f"Operation {operation_id} not found for device {device_id}")

    async def _get_device_aggregation(self, params: Dict[str, Any], organization_id: Optional[str] = None,
                                      device_type: Optional[str] = None) -> str:
        """Query device aggregations (Accept: application/vnd.withsecure.aggr+json)."""
        org_id = self._org_id(organization_id)
        if org_id:
            params["organizationId"] = org_id
        if device_type:
            params["type"] = device_type
        return self._dump(await self._get("/devices/v1/devices", params, accept=AGGREGATION_ACCEPT))

    async def _get_device_statistics(self, count: str, organization_id: Optional[str] = None,
                                     device_type: Optional[str] = None, device_name: Optional[str] = None,
                                     online: Optional[bool] = None, label: Optional[str] = None,
                                     protection_status_overview: Optional[str] = None) -> str:
        """Count devices grouped by a property."""
        params: Dict[str, Any] = {"count": count}
        if device_name:
            params["name"] = device_name
        if online is not None:
            params["online"] = "true" if online else "false"
        if label:
            params["label"] = label
        if protection_status_overview:
            params["protectionStatusOverview"] = protection_status_overview
        return await self._get_device_aggregation(params, organization_id, device_type)

    async def _get_device_histogram(self, histogram: str = "protectionStatus", organization_id: Optional[str] = None,
                                    device_type: Optional[str] = None) -> str:
        """Get device histogram statistics for the last 30 days."""
        return await self._get_device_aggregation({"histogram": histogram}, organization_id, device_type)

    async def read_resource(self, uri: str) -> Optional[str]:
        """Read a device resource."""
        if uri == "withsecure://devices":
            return await self._get_devices()
        if uri.startswith("withsecure://devices/"):
            device_id = uri.split("/")[-1]
            return await self._get_device(device_id)
        return None

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        try:
            if tool_name == "list_devices":
                result = await self._get_devices(DeviceFilters(**arguments))

            elif tool_name == "get_device":
                result = await self._get_device(arguments["device_id"])

            elif tool_name == "isolate_device":
                result = await self._isolate_device(arguments["device_id"], arguments.get("reason"))

            elif tool_name == "unisolate_device":
                result = await self._unisolate_device(arguments["device_id"])

            elif tool_name == "scan_device":
                result = await self._scan_device(arguments["device_id"])

            elif tool_name == "show_message":
                result = await self._show_message(arguments["device_id"], arguments["message"])

            elif tool_name == "assign_profile":
                result = await self._assign_profile(arguments["device_id"], arguments["profile_id"])

            elif tool_name == "get_device_operations":
                result = await self._get_device_operations(arguments["device_id"])

            elif tool_name == "get_device_operation_status":
                result = await self._get_device_operation_status(
                    arguments["device_id"], arguments["operation_id"]
                )

            elif tool_name == "get_device_statistics":
                result = await self._get_device_statistics(
                    arguments["count"],
                    organization_id=arguments.get("organization_id"),
                    device_type=arguments.get("device_type"),
                    device_name=arguments.get("device_name"),
                    online=arguments.get("online"),
                    label=arguments.get("label"),
                    protection_status_overview=arguments.get("protection_status_overview"),
                )

            elif tool_name == "get_device_histogram":
                result = await self._get_device_histogram(
                    arguments.get("histogram") or "protectionStatus",
                    organization_id=arguments.get("organization_id"),
                    device_type=arguments.get("device_type"),
                )

            elif tool_name == "send_full_status":
                result = await self._send_full_status(arguments["device_ids"])

            elif tool_name == "restart_system":
                result = await self._restart_system(arguments["device_ids"], arguments.get("message"))

            elif tool_name == "update_devices":
                result = await self._update_devices(arguments["device_ids"], arguments)

            elif tool_name == "delete_devices":
                result = await self._delete_devices(arguments["device_ids"])

            else:
                return None

            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }

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

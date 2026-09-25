"""
Software Updates module for WithSecure Elements MCP Server.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseModule

logger = logging.getLogger(__name__)

MISSING_UPDATES_MAX_LIMIT = 200
OPERATION_MAX_TARGETS = 5
INSTALL_MAX_BULLETINS = 200
INSTALLATIONS_MAX_DAYS = 90
INSTALLATIONS_MAX_LIMIT = 200


class SoftwareUpdatesModule(BaseModule):
    """Module for managing software updates on devices."""

    @property
    def name(self) -> str:
        """Module name."""
        return "software_updates"

    @property
    def description(self) -> str:
        """Module description."""
        return "Manage software updates on devices"

    def _register_resources(self) -> None:
        """Register module resources."""
        # No resources for this module
        pass

    def _register_tools(self) -> None:
        """Register module tools."""
        tools = [
            {
                "name": "install_software_updates",
                "description": "Install software updates on devices. Provide either bulletin_ids (from get_missing_updates) or severity, not both.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Device IDs",
                            "minItems": 1,
                            "maxItems": OPERATION_MAX_TARGETS
                        },
                        "bulletin_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Bulletin IDs to install",
                            "minItems": 1,
                            "maxItems": INSTALL_MAX_BULLETINS
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "important", "everything"],
                            "description": "Install all updates of this severity"
                        },
                        "force_close": {
                            "type": "boolean",
                            "default": False,
                            "description": "Force close applications being upgraded"
                        }
                    },
                    "required": ["device_ids"]
                }
            },
            {
                "name": "get_missing_updates",
                "description": "List missing software updates for a device (paginated via anchor/nextAnchor). Use bulletinId values with install_software_updates.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device UUID"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "important", "moderate", "low", "unclassified"]
                        },
                        "category": {
                            "type": "string",
                            "enum": ["security", "nonSecurity", "servicePack", "securityTool", "none"]
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": MISSING_UPDATES_MAX_LIMIT,
                            "default": 100
                        },
                        "anchor": {
                            "type": "string",
                            "description": "nextAnchor from previous page"
                        }
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "scan_for_updates",
                "description": "Trigger a software updates scan on devices.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Device IDs",
                            "minItems": 1,
                            "maxItems": OPERATION_MAX_TARGETS
                        }
                    },
                    "required": ["device_ids"]
                }
            },
            {
                "name": "get_software_update_installations",
                "description": "Count software updates installed in the organization over the last N days, "
                               "with a daily breakdown by category and severity",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "last_days": {
                            "type": "integer", "minimum": 1, "maximum": INSTALLATIONS_MAX_DAYS,
                            "description": "Trailing window in days (1-90)"
                        },
                        "organization_id": {"type": "string", "description": "Organization UUID (defaults to configured org)"},
                        "limit": {
                            "type": "integer", "minimum": 1, "maximum": INSTALLATIONS_MAX_LIMIT, "default": 100,
                            "description": "Max daily-breakdown items"
                        },
                        "anchor": {"type": "string", "description": "nextAnchor from a previous response"}
                    },
                    "required": ["last_days"]
                }
            }
        ]

        for tool in tools:
            self._tools.append(tool)

    @staticmethod
    def _text(data: Any) -> Dict[str, Any]:
        """Wrap data as a compact JSON MCP text result."""
        return {
            "content": [
                {
                    "type": "text",
                    "text": BaseModule._dump(data)
                }
            ]
        }

    @staticmethod
    def _error(message: str) -> Dict[str, Any]:
        """Build an MCP error result."""
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {message}"
                }
            ],
            "isError": True
        }

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        """Normalize a scalar-or-list argument into a list."""
        if not value:
            return []
        return value if isinstance(value, list) else [value]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a software updates tool."""
        try:
            if name == "install_software_updates":
                return await self._install_software_updates(arguments)
            elif name == "get_missing_updates":
                return await self._get_missing_updates(arguments)
            elif name == "scan_for_updates":
                return await self._scan_for_updates(arguments)
            elif name == "get_software_update_installations":
                return await self._get_installations(arguments)
            else:
                return None
        except Exception as e:
            return self._error(str(e))

    def _device_ids(self, arguments: Dict[str, Any]) -> List[str]:
        """Get device IDs (accepts device_ids or device_id) and validate count."""
        device_ids = self._as_list(arguments.get("device_ids") or arguments.get("device_id"))
        if not device_ids:
            raise ValueError("device_ids is required")
        if len(device_ids) > OPERATION_MAX_TARGETS:
            raise ValueError(f"At most {OPERATION_MAX_TARGETS} device_ids per request")
        return device_ids

    async def _run_operation(self, request_body: Dict[str, Any], what: str) -> Dict[str, Any]:
        """POST /devices/v1/operations and summarize the 207 multi-status response."""
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"
        response = await self.auth._client.post(
            "/devices/v1/operations",
            headers=headers,
            json=request_body
        )

        if response.status_code != 207:
            return self._error(f"Failed to trigger {what}: {response.status_code} - {response.text}")

        data = response.json()
        results = []
        for item in data.get("multistatus", []):
            result = {"target": item.get("target"), "status": item.get("status")}
            if item.get("operationId") is not None:
                result["operation_id"] = item.get("operationId")
            if item.get("details"):
                result["details"] = item.get("details")
            results.append(result)

        return self._text({
            "triggered": sum(1 for r in results if r["status"] == 202),
            "results": results,
            "transaction_id": data.get("transactionId")
        })

    async def _install_software_updates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Install software updates on specified devices."""
        device_ids = self._device_ids(arguments)
        bulletin_ids = self._as_list(arguments.get("bulletin_ids") or arguments.get("bulletin_id"))
        severity = arguments.get("severity")
        force_close = bool(arguments.get("force_close", False))

        # Validate that either bulletin_ids or severity is provided, but not both
        if bulletin_ids and severity:
            raise ValueError("Cannot specify both bulletin_ids and severity. Choose one.")
        if not bulletin_ids and not severity:
            raise ValueError("Must specify either bulletin_ids or severity.")
        if len(bulletin_ids) > INSTALL_MAX_BULLETINS:
            raise ValueError(f"At most {INSTALL_MAX_BULLETINS} bulletin_ids per request")

        request_body = {
            "operation": "installSoftwareUpdates",
            "targets": device_ids,
            "parameters": {
                "forceClose": force_close
            }
        }

        # Add either bulletin_ids or severity
        if bulletin_ids:
            request_body["parameters"]["bulletinIds"] = bulletin_ids
        else:
            request_body["parameters"]["severity"] = severity

        logger.info(f"Installing software updates on {len(device_ids)} device(s)")
        return await self._run_operation(request_body, "software update installation")

    async def _get_missing_updates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get missing software updates for a specific device."""
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        device_id = arguments.get("device_id")
        if not device_id:
            raise ValueError("device_id is required")

        try:
            limit = int(arguments.get("limit") or 100)
        except (TypeError, ValueError):
            limit = 100

        # Request body (application/x-www-form-urlencoded)
        data = {
            "deviceId": device_id,
            "limit": max(1, min(limit, MISSING_UPDATES_MAX_LIMIT))
        }
        for key in ("severity", "category", "anchor"):
            if arguments.get(key):
                data[key] = arguments[key]

        headers = await self.auth.get_headers()
        response = await self.auth._client.post(
            "/software-updates/v1/missing-updates",
            headers=headers,
            data=data  # httpx sets Content-Type to application/x-www-form-urlencoded
        )

        if response.status_code != 200:
            return self._error(f"Failed to get missing updates: {response.status_code} - {response.text}")

        body = response.json()
        updates = []
        for item in body.get("items", []):
            software = item.get("software") or {}
            update = {
                "bulletinId": item.get("bulletinId"),
                "name": item.get("name"),
                "severity": item.get("severity"),
                "category": item.get("category"),
                "software": software.get("name"),
                "vendor": software.get("vendor"),
                "installedVersion": item.get("installedVersion"),
                "targetVersion": item.get("targetVersion"),
                "cve": [c.get("id") for c in item.get("cve") or [] if c.get("id")]
            }
            updates.append({k: v for k, v in update.items() if v not in (None, "", [])})

        result = {
            "device_id": device_id,
            "count": len(updates),
            "critical": sum(1 for u in updates if u.get("severity") == "critical"),
            "important": sum(1 for u in updates if u.get("severity") == "important"),
            "security": sum(1 for u in updates if u.get("category") == "security"),
            "items": updates
        }
        if body.get("nextAnchor"):
            result["nextAnchor"] = body["nextAnchor"]

        return self._text(result)

    async def _scan_for_updates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a scan for software updates on specified devices."""
        device_ids = self._device_ids(arguments)

        request_body = {
            "operation": "scanForUpdates",
            "targets": device_ids
        }

        logger.info(f"Scanning for updates on {len(device_ids)} device(s)")
        return await self._run_operation(request_body, "scan for updates")

    async def _get_installations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Count installed updates (GET /software-updates/v1/installations)."""
        params = {
            "organizationId": self._org_id(arguments.get("organization_id")),
            "lastDays": max(1, min(int(arguments["last_days"]), INSTALLATIONS_MAX_DAYS)),
            "limit": max(1, min(int(arguments.get("limit") or 100), INSTALLATIONS_MAX_LIMIT)),
            "anchor": arguments.get("anchor"),
        }
        data = await self._get_json("/software-updates/v1/installations", params, "software update installations")
        return self._text(data)

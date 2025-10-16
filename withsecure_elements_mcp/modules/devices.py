"""
MCP module for WithSecure Elements devices management.
"""

from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import BaseModel

from .base import BaseModule
from ..auth import WithSecureAuth
from ..config import WithSecureConfig


class DeviceFilters(BaseModel):
    """Filters for device search."""
    
    organization_id: Optional[str] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    status: Optional[str] = None
    last_seen_start: Optional[str] = None
    last_seen_end: Optional[str] = None
    limit: Optional[int] = 100
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
        
        # Add resources to the list for HTTP transport
        self._resources.append({
            "uri": "withsecure://devices",
            "name": "Devices",
            "description": "WithSecure Elements devices list",
            "mimeType": "application/json"
        })
        
        @self.server.list_resources()
        async def list_devices() -> List[Resource]:
            """List available device resources."""
            return [
                Resource(
                    uri="withsecure://devices",
                    name="Devices",
                    description="WithSecure Elements devices list",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_device(uri: str) -> str:
            """Read a device resource."""
            if uri == "withsecure://devices":
                # Get devices list
                devices = await self._get_devices()
                return devices
            elif uri.startswith("withsecure://devices/"):
                # Get specific device
                device_id = uri.split("/")[-1]
                device = await self._get_device(device_id)
                return device
            else:
                raise ValueError(f"Unrecognized resource URI: {uri}")
    
    def _register_tools(self) -> None:
        """Register tools for devices."""
        
        # Add tools to the list for HTTP transport
        self._tools.extend([
            {
                "name": "list_devices",
                "description": "List WithSecure Elements devices",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID (optional)"
                        },
                        "device_name": {
                            "type": "string",
                            "description": "Filter by device name"
                        },
                        "device_type": {
                            "type": "string",
                            "description": "Filter by device type"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by device status"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of devices to return",
                            "default": 100
                        },
                        "last_seen_start": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Start of last seen time range"
                        },
                        "last_seen_end": {
                            "type": "string",
                            "format": "date-time",
                            "description": "End of last seen time range"
                        }
                    }
                }
            },
            {
                "name": "get_device",
                "description": "Retrieve details of a specific device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID"
                        }
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "isolate_device",
                "description": "Isolate a device from the network",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for isolation"
                        }
                    },
                    "required": ["device_id", "reason"]
                }
            },
            {
                "name": "unisolate_device",
                "description": "Unisolate a device from the network",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID"
                        }
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "scan_device",
                "description": "Launch a scan on a device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID"
                        },
                        "scan_type": {
                            "type": "string",
                            "description": "Type of scan to perform"
                        }
                    },
                    "required": ["device_id", "scan_type"]
                }
            },
            {
                "name": "show_message",
                "description": "Show message to device user",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID to show message to"
                        },
                        "message": {
                            "type": "string",
                            "maxLength": 512,
                            "description": "Message to display to user"
                        }
                    },
                    "required": ["device_id", "message"]
                }
            },
            {
                "name": "assign_profile",
                "description": "Assign profile to device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID to assign profile to"
                        },
                        "profile_id": {
                            "type": "integer",
                            "description": "Profile ID to assign"
                        }
                    },
                    "required": ["device_id", "profile_id"]
                }
            },
            {
                "name": "get_device_operations",
                "description": "Get device operations list",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID to get operations for"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 200,
                            "default": 100,
                            "description": "Maximum number of operations to return"
                        },
                        "anchor": {
                            "type": "string",
                            "description": "Pagination anchor for next page"
                        }
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "get_device_operation_status",
                "description": "Get specific device operation status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID"
                        },
                        "operation_id": {
                            "type": "string",
                            "description": "Operation ID to check status for"
                        }
                    },
                    "required": ["device_id", "operation_id"]
                }
            },
            {
                "name": "get_device_statistics",
                "description": "Get device statistics and aggregated data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID (optional)"
                        },
                        "count": {
                            "type": "string",
                            "enum": ["protectionStatus", "type", "state", "online", "label"],
                            "description": "Property to count and group devices by"
                        },
                        "device_type": {
                            "type": "string",
                            "enum": ["computer", "mobile", "connector"],
                            "description": "Filter by device type"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["active", "blocked", "inactive"],
                            "description": "Filter by device state"
                        }
                    }
                }
            },
            {
                "name": "get_device_histogram",
                "description": "Get device histogram statistics for the last 30 days",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID (optional)"
                        },
                        "histogram": {
                            "type": "string",
                            "enum": ["protectionStatus", "type", "state", "online"],
                            "description": "Property to create histogram for"
                        },
                        "device_type": {
                            "type": "string",
                            "enum": ["computer", "mobile", "connector"],
                            "description": "Filter by device type"
                        }
                    },
                    "required": ["histogram"]
                }
            },
            {
                "name": "send_full_status",
                "description": "Request a full status update from specified devices. This operation forces devices to send their complete status information to the server.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of device IDs to request full status from (1-5 devices). Example: [\"34b8cd7a-7cff-4868-a238-4c8754909945\"]",
                            "minItems": 1,
                            "maxItems": 5
                        }
                    },
                    "required": ["device_ids"]
                }
            },
            {
                "name": "restart_system",
                "description": "Restart specified devices (Windows computers only). A message can be displayed to the user before the restart.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of device IDs to restart (1-5 devices, Windows computers only). Example: [\"34b8cd7a-7cff-4868-a238-4c8754909945\"]",
                            "minItems": 1,
                            "maxItems": 5
                        },
                        "message": {
                            "type": "string",
                            "description": "Optional message to display on the remote host before the device is restarted (max 512 characters)",
                            "maxLength": 512
                        }
                    },
                    "required": ["device_ids"]
                }
            },
        ])
        
        @self.server.list_tools()
        async def list_device_tools() -> List[Tool]:
            """List available tools for devices."""
            return [
                Tool(
                    name="list_devices",
                    description="List WithSecure Elements devices",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "string",
                                "description": "Organization ID (optional)"
                            },
                            "device_name": {
                                "type": "string",
                                "description": "Filter by device name"
                            },
                            "device_type": {
                                "type": "string",
                                "description": "Filter by device type"
                            },
                            "status": {
                                "type": "string",
                                "description": "Filter by device status"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of devices to return",
                                "default": 100
                            },
                            "last_seen_start": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Start of last seen time range"
                            },
                            "last_seen_end": {
                                "type": "string",
                                "format": "date-time",
                                "description": "End of last seen time range"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_device",
                    description="Retrieve details of a specific device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device ID"
                            }
                        },
                        "required": ["device_id"]
                    }
                ),
                Tool(
                    name="get_device_events",
                    description="Retrieve device events",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device ID"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of events to return",
                                "default": 100
                            },
                            "created_timestamp_start": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Start of time range"
                            },
                            "created_timestamp_end": {
                                "type": "string",
                                "format": "date-time",
                                "description": "End of time range"
                            }
                        },
                        "required": ["device_id"]
                    }
                ),
                Tool(
                    name="get_device_statistics",
                    description="Retrieve device statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device ID"
                            }
                        },
                        "required": ["device_id"]
                    }
                ),
                Tool(
                    name="isolate_device",
                    description="Isolate a device from the network",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device ID"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Reason for isolation"
                            }
                        },
                        "required": ["device_id"]
                    }
                ),
                Tool(
                    name="unisolate_device",
                    description="Unisolate a device from the network",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device ID"
                            }
                        },
                        "required": ["device_id"]
                    }
                ),
                Tool(
                    name="scan_device",
                    description="Launch a scan on a device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device ID"
                            },
                            "scan_type": {
                                "type": "string",
                                "description": "Type of scan to perform",
                                "enum": ["quick", "full", "custom"]
                            }
                        },
                        "required": ["device_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_device_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a device tool."""
            if name == "list_devices":
                filters = DeviceFilters(**arguments)
                devices = await self._get_devices(filters)
                return [TextContent(type="text", text=devices)]
            
            elif name == "get_device":
                device_id = arguments["device_id"]
                device = await self._get_device(device_id)
                return [TextContent(type="text", text=device)]
            
            elif name == "get_device_events":
                device_id = arguments["device_id"]
                limit = arguments.get("limit", 100)
                created_start = arguments.get("created_timestamp_start")
                created_end = arguments.get("created_timestamp_end")
                events = await self._get_device_events(device_id, limit, created_start, created_end)
                return [TextContent(type="text", text=events)]
            
            elif name == "get_device_statistics":
                device_id = arguments["device_id"]
                statistics = await self._get_device_statistics(device_id)
                return [TextContent(type="text", text=statistics)]
            
            elif name == "isolate_device":
                device_id = arguments["device_id"]
                reason = arguments.get("reason", "Manual isolation")
                result = await self._isolate_device(device_id, reason)
                return [TextContent(type="text", text=result)]
            
            elif name == "unisolate_device":
                device_id = arguments["device_id"]
                result = await self._unisolate_device(device_id)
                return [TextContent(type="text", text=result)]
            
            elif name == "scan_device":
                device_id = arguments["device_id"]
                scan_type = arguments.get("scan_type", "quick")
                result = await self._scan_device(device_id, scan_type)
                return [TextContent(type="text", text=result)]
            
            else:
                raise ValueError(f"Unrecognized tool: {name}")
    
    async def _get_devices(self, filters: Optional[DeviceFilters] = None) -> str:
        """Retrieve devices list."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        params = {}
        
        if filters:
            if filters.organization_id:
                params["organizationId"] = filters.organization_id
            elif self.config.organization_id:
                params["organizationId"] = self.config.organization_id
            
            if filters.device_id:
                params["deviceId"] = filters.device_id
            if filters.device_name:
                params["deviceName"] = filters.device_name
            if filters.device_type:
                params["deviceType"] = filters.device_type
            if filters.status:
                params["status"] = filters.status
            if filters.last_seen_start:
                params["lastSeenStart"] = filters.last_seen_start
            if filters.last_seen_end:
                params["lastSeenEnd"] = filters.last_seen_end
            if filters.limit:
                params["limit"] = filters.limit
            if filters.anchor:
                params["anchor"] = filters.anchor
        
        response = await self.auth._client.get(
            "/devices/v1/devices",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving devices: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_device(self, device_id: str) -> str:
        """Retrieve details of a specific device."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.get(
            f"/devices/v1/devices/{device_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving device: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_device_events(self, device_id: str, limit: int = 100, created_start: Optional[str] = None, created_end: Optional[str] = None) -> str:
        """Retrieve device events."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        params = {
            "deviceId": device_id,
            "limit": limit
        }
        
        if created_start:
            params["createdTimestampStart"] = created_start
        if created_end:
            params["createdTimestampEnd"] = created_end
        
        response = await self.auth._client.get(
            "/events/v1/events",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving device events: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_device_statistics(self, device_id: str) -> str:
        """Retrieve device statistics."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.get(
            f"/devices/v1/devices/{device_id}/statistics",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving statistics: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _isolate_device(self, device_id: str, reason: str) -> str:
        """Isolate a device from the network."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "deviceId": device_id,
            "reason": reason
        }
        
        response = await self.auth._client.post(
            f"/devices/v1/devices/{device_id}/isolate",
            headers=headers,
            json=data
        )
        
        if response.status_code not in [200, 202]:
            raise Exception(f"Error isolating device: {response.status_code} - {response.text}")
        
        return json.dumps({"success": True, "message": f"Device {device_id} isolated"})
    
    async def _unisolate_device(self, device_id: str) -> str:
        """Unisolate a device from the network."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.post(
            f"/devices/v1/devices/{device_id}/unisolate",
            headers=headers
        )
        
        if response.status_code not in [200, 202]:
            raise Exception(f"Error unisolating device: {response.status_code} - {response.text}")
        
        return json.dumps({"success": True, "message": f"Device {device_id} unisolated"})
    
    async def _scan_device(self, device_id: str, scan_type: str) -> str:
        """Launch a scan on a device."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "deviceId": device_id,
            "scanType": scan_type
        }
        
        response = await self.auth._client.post(
            f"/devices/v1/devices/{device_id}/scan",
            headers=headers,
            json=data
        )
        
        if response.status_code not in [200, 202]:
            raise Exception(f"Error launching scan: {response.status_code} - {response.text}")
        
        return json.dumps({"success": True, "message": f"{scan_type} scan launched on device {device_id}"})
    
    async def _show_message(self, device_id: str, message: str) -> str:
        """Show message to device user."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "operation": "showMessage",
            "targets": [device_id],
            "parameters": {
                "message": message
            }
        }
        
        response = await self.auth._client.post(
            "/devices/v1/operations",
            headers=headers,
            json=data
        )
        
        if response.status_code not in [200, 202, 207]:
            raise Exception(f"Error showing message: {response.status_code} - {response.text}")
        
        result = response.json()
        return json.dumps(result)
    
    async def _assign_profile(self, device_id: str, profile_id: int) -> str:
        """Assign profile to device."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "operation": "assignProfile",
            "targets": [device_id],
            "parameters": {
                "profileId": profile_id
            }
        }
        
        response = await self.auth._client.post(
            "/devices/v1/operations",
            headers=headers,
            json=data
        )
        
        if response.status_code not in [200, 202, 207]:
            raise Exception(f"Error assigning profile: {response.status_code} - {response.text}")
        
        result = response.json()
        return json.dumps(result)
    
    async def _get_device_operations(self, device_id: str, limit: int = 100, anchor: str = None) -> str:
        """Get device operations list."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        params = {
            "deviceId": device_id,
            "limit": limit
        }
        if anchor:
            params["anchor"] = anchor
        
        response = await self.auth._client.get(
            "/devices/v1/operations",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error getting device operations: {response.status_code} - {response.text}")
        
        result = response.json()
        return json.dumps(result)
    
    async def _get_device_operation_status(self, device_id: str, operation_id: str) -> str:
        """Get specific device operation status."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.get(
            f"/devices/v1/devices/operations/{operation_id}",
            headers=headers,
            params={"deviceId": device_id}
        )
        
        if response.status_code != 200:
            raise Exception(f"Error getting operation status: {response.status_code} - {response.text}")
        
        result = response.json()
        return json.dumps(result)
    
    async def _get_device_statistics(self, organization_id: str = None, count: str = None, device_type: str = None, state: str = None) -> str:
        """Get device statistics and aggregated data."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Accept"] = "application/vnd.withsecure.aggr+json"
        
        params = {}
        if organization_id:
            params["organizationId"] = organization_id
        if count:
            params["count"] = count
        if device_type:
            params["type"] = device_type
        if state:
            params["state"] = state
        
        response = await self.auth._client.get(
            "/devices/v1/devices",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error getting device statistics: {response.status_code} - {response.text}")
        
        result = response.json()
        return json.dumps(result)
    
    async def _get_device_histogram(self, histogram: str, organization_id: str = None, device_type: str = None) -> str:
        """Get device histogram statistics for the last 30 days."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Accept"] = "application/vnd.withsecure.aggr+json"
        
        params = {
            "histogram": histogram
        }
        if organization_id:
            params["organizationId"] = organization_id
        if device_type:
            params["type"] = device_type
        
        response = await self.auth._client.get(
            "/devices/v1/devices",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error getting device histogram: {response.status_code} - {response.text}")
        
        result = response.json()
        return json.dumps(result)
    
    async def _send_full_status(self, device_ids: List[str]) -> str:
        """Request a full status update from specified devices."""
        headers = await self.auth.get_headers()
        
        # Build request body
        request_body = {
            "operation": "sendFullStatus",
            "targets": device_ids
        }
        
        # Make API request
        response = await self.auth._client.post(
            "/devices/v1/operations",
            headers=headers,
            json=request_body
        )
        
        if response.status_code == 207:
            # Multi-status response
            data = response.json()
            results = []
            
            for item in data.get("multistatus", []):
                result = {
                    "target": item.get("target"),
                    "status": item.get("status"),
                    "details": item.get("details"),
                    "operation_id": item.get("operationId")
                }
                results.append(result)
            
            return json.dumps({
                "success": True,
                "message": f"Full status request sent to {len(device_ids)} device(s)",
                "results": results,
                "transaction_id": data.get("transactionId")
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "message": f"Failed to send full status request: {response.status_code}",
                "error": response.text
            }, indent=2)
    
    async def _restart_system(self, device_ids: List[str], message: Optional[str] = None) -> str:
        """Restart specified devices (Windows computers only)."""
        headers = await self.auth.get_headers()
        
        # Build request body
        request_body = {
            "operation": "restartSystem",
            "targets": device_ids
        }
        
        # Add message parameter if provided
        if message:
            request_body["parameters"] = {
                "message": message
            }
        
        # Make API request
        response = await self.auth._client.post(
            "/devices/v1/operations",
            headers=headers,
            json=request_body
        )
        
        if response.status_code == 207:
            # Multi-status response
            data = response.json()
            results = []
            
            for item in data.get("multistatus", []):
                result = {
                    "target": item.get("target"),
                    "status": item.get("status"),
                    "details": item.get("details"),
                    "operation_id": item.get("operationId")
                }
                results.append(result)
            
            return json.dumps({
                "success": True,
                "message": f"System restart triggered on {len(device_ids)} device(s)",
                "results": results,
                "transaction_id": data.get("transactionId")
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "message": f"Failed to trigger system restart: {response.status_code}",
                "error": response.text
            }, indent=2)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        try:
            if tool_name == "list_devices":
                filters = DeviceFilters(**arguments)
                devices = await self._get_devices(filters)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": devices
                        }
                    ]
                }
            
            elif tool_name == "get_device":
                device_id = arguments["device_id"]
                device = await self._get_device(device_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": device
                        }
                    ]
                }
            
            elif tool_name == "isolate_device":
                device_id = arguments["device_id"]
                reason = arguments["reason"]
                result = await self._isolate_device(device_id, reason)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "unisolate_device":
                device_id = arguments["device_id"]
                result = await self._unisolate_device(device_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "scan_device":
                device_id = arguments["device_id"]
                scan_type = arguments["scan_type"]
                result = await self._scan_device(device_id, scan_type)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "show_message":
                device_id = arguments["device_id"]
                message = arguments["message"]
                result = await self._show_message(device_id, message)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "assign_profile":
                device_id = arguments["device_id"]
                profile_id = arguments["profile_id"]
                result = await self._assign_profile(device_id, profile_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "get_device_operations":
                device_id = arguments["device_id"]
                limit = arguments.get("limit", 100)
                anchor = arguments.get("anchor")
                result = await self._get_device_operations(device_id, limit, anchor)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "get_device_operation_status":
                device_id = arguments["device_id"]
                operation_id = arguments["operation_id"]
                result = await self._get_device_operation_status(device_id, operation_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "get_device_statistics":
                organization_id = arguments.get("organization_id")
                count = arguments.get("count")
                device_type = arguments.get("device_type")
                state = arguments.get("state")
                result = await self._get_device_statistics(organization_id, count, device_type, state)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "get_device_histogram":
                histogram = arguments["histogram"]
                organization_id = arguments.get("organization_id")
                device_type = arguments.get("device_type")
                result = await self._get_device_histogram(histogram, organization_id, device_type)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "send_full_status":
                device_ids = arguments["device_ids"]
                result = await self._send_full_status(device_ids)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "restart_system":
                device_ids = arguments["device_ids"]
                message = arguments.get("message")
                result = await self._restart_system(device_ids, message)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
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

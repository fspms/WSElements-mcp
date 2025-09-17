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

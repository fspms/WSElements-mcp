"""
Software Updates module for WithSecure Elements MCP Server.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .base import BaseModule


class SoftwareUpdateRequest(BaseModel):
    """Request model for software update operations."""
    
    bulletin_ids: Optional[List[str]] = Field(
        None,
        description="Bulletin IDs of software updates to install. Can be retrieved from missing-updates endpoint."
    )
    severity: Optional[str] = Field(
        None,
        description="Severity of software updates to install. Options: critical, important, everything"
    )
    force_close: bool = Field(
        False,
        description="Whether to force close applications that are being upgraded"
    )


class SoftwareUpdateResponse(BaseModel):
    """Response model for software update operations."""
    
    operation_id: str = Field(..., description="ID of the triggered operation")
    target: str = Field(..., description="Target device ID")
    status: int = Field(..., description="HTTP status of the operation")
    details: Optional[str] = Field(None, description="Additional details about the operation")


class MissingUpdate(BaseModel):
    """Model for missing software updates."""
    
    bulletin_id: str = Field(..., description="Bulletin ID of the update")
    title: str = Field(..., description="Title of the update")
    severity: str = Field(..., description="Severity level of the update")
    description: Optional[str] = Field(None, description="Description of the update")
    published_date: Optional[str] = Field(None, description="Date when the update was published")


class SoftwareUpdatesModule(BaseModule):
    """Module for managing software updates on devices."""
    
    def __init__(self, server, auth, config):
        super().__init__(server, auth, config)
    
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
                "description": "Install software updates on specified devices. Use either bulletinIds or severity, not both.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of device IDs to install updates on (1-5 devices)",
                            "minItems": 1,
                            "maxItems": 5
                        },
                        "bulletin_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific bulletin IDs to install (1-200 IDs). Cannot be used with severity.",
                            "minItems": 1,
                            "maxItems": 200
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "important", "everything"],
                            "description": "Severity level of updates to install. Cannot be used with bulletin_ids."
                        },
                        "force_close": {
                            "type": "boolean",
                            "default": False,
                            "description": "Force close applications that are being upgraded"
                        }
                    },
                    "required": ["device_ids"],
                    "oneOf": [
                        {"required": ["bulletin_ids"]},
                        {"required": ["severity"]}
                    ]
                }
            },
            {
                "name": "get_missing_updates",
                "description": "Get list of missing software updates for a specific device.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID to get missing updates for"
                        }
                    },
                    "required": ["device_id"]
                }
            }
        ]
        
        for tool in tools:
            self._tools.append(tool)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a software updates tool."""
        if name == "install_software_updates":
            return await self._install_software_updates(arguments)
        elif name == "get_missing_updates":
            return await self._get_missing_updates(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _install_software_updates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Install software updates on specified devices."""
        device_ids = arguments.get("device_ids", [])
        bulletin_ids = arguments.get("bulletin_ids")
        severity = arguments.get("severity")
        force_close = arguments.get("force_close", False)
        
        # Validate that either bulletin_ids or severity is provided, but not both
        if bulletin_ids and severity:
            raise ValueError("Cannot specify both bulletin_ids and severity. Choose one.")
        if not bulletin_ids and not severity:
            raise ValueError("Must specify either bulletin_ids or severity.")
        
        # Prepare request body
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
        
        # Make API request
        headers = await self.auth.get_headers()
        response = await self.auth._client.post(
            "/devices/v1/response-actions",
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
            
            return {
                "success": True,
                "message": f"Software update installation triggered for {len(device_ids)} device(s)",
                "results": results,
                "transaction_id": data.get("transactionId")
            }
        else:
            return {
                "success": False,
                "message": f"Failed to trigger software update installation: {response.status_code}",
                "error": response.text
            }
    
    async def _get_missing_updates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get missing software updates for a specific device."""
        device_id = arguments.get("device_id")
        
        if not device_id:
            raise ValueError("device_id is required")
        
        # Make API request to get missing updates
        headers = await self.auth.get_headers()
        response = await self.auth._client.get(
            f"/devices/v1/devices/{device_id}/missing-updates",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            updates = []
            
            for item in data.get("items", []):
                update = {
                    "bulletin_id": item.get("bulletinId"),
                    "title": item.get("title"),
                    "severity": item.get("severity"),
                    "description": item.get("description"),
                    "published_date": item.get("publishedDate")
                }
                updates.append(update)
            
            return {
                "success": True,
                "message": f"Found {len(updates)} missing updates for device {device_id}",
                "device_id": device_id,
                "updates": updates
            }
        else:
            return {
                "success": False,
                "message": f"Failed to get missing updates: {response.status_code}",
                "error": response.text
            }

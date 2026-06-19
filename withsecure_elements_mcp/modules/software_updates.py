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
                "description": "Install software updates on specified devices. You can provide either bulletin_ids (array) OR severity (string). Example: {\"device_ids\": [\"34b8cd7a-7cff-4868-a238-4c8754909945\"], \"bulletin_ids\": [\"FSPM-1103-65290-5066835/x64\"]}",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of device IDs to install updates on (1-5 devices). Example: [\"34b8cd7a-7cff-4868-a238-4c8754909945\"]",
                            "minItems": 1,
                            "maxItems": 5
                        },
                        "bulletin_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of bulletin IDs to install (1-200 IDs). Example: [\"FSPM-1103-65290-5066835/x64\"]",
                            "minItems": 1,
                            "maxItems": 200
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "important", "everything"],
                            "description": "Install all updates of a certain severity. Cannot be used with bulletin_ids."
                        },
                        "force_close": {
                            "type": "boolean",
                            "default": False,
                            "description": "Force close applications that are being upgraded"
                        }
                    },
                    "required": ["device_ids"]
                }
            },
            {
                "name": "get_missing_updates",
                "description": "Get list of missing software updates for a specific device. Can filter by severity and category. IMPORTANT: Remember the device_id from the response - you'll need it to install updates using install_software_updates.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID to get missing updates for. Example: 34b8cd7a-7cff-4868-a238-4c8754909945"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "important", "moderate", "low", "unclassified"],
                            "description": "Filter by severity level (optional)"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["security", "nonSecurity", "servicePack", "securityTool", "none"],
                            "description": "Filter by category (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of items to return (1-200, default: 100)",
                            "minimum": 1,
                            "maximum": 200
                        }
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "scan_for_updates",
                "description": "Trigger a scan for software updates on specified devices. This operation forces the device to check for available updates.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of device IDs to scan for updates (1-5 devices). Example: [\"34b8cd7a-7cff-4868-a238-4c8754909945\"]",
                            "minItems": 1,
                            "maxItems": 5
                        }
                    },
                    "required": ["device_ids"]
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
        elif name == "scan_for_updates":
            return await self._scan_for_updates(arguments)
        else:
            return None
    
    async def _install_software_updates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Install software updates on specified devices."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Received arguments: {arguments}")
        
        # Try to get device_ids (plural) or device_id (singular)
        device_ids = arguments.get("device_ids", [])
        if not device_ids:
            device_id = arguments.get("device_id")
            if device_id:
                device_ids = [device_id]
                logger.info(f"Converted device_id to device_ids: {device_ids}")
        
        # Try to get bulletin_ids (plural) or bulletin_id (singular)
        bulletin_ids = arguments.get("bulletin_ids")
        if not bulletin_ids:
            bulletin_id = arguments.get("bulletin_id")
            if bulletin_id:
                bulletin_ids = [bulletin_id]
                logger.info(f"Converted bulletin_id to bulletin_ids: {bulletin_ids}")
        
        severity = arguments.get("severity")
        force_close = arguments.get("force_close", False)
        
        # Validate that either bulletin_ids or severity is provided, but not both
        if bulletin_ids and severity:
            raise ValueError("Cannot specify both bulletin_ids and severity. Choose one.")
        if not bulletin_ids and not severity:
            raise ValueError("Must specify either bulletin_ids or severity.")
        
        # Ensure device_ids is a list
        if device_ids and not isinstance(device_ids, list):
            logger.info(f"Converting device_ids to list: {device_ids}")
            device_ids = [device_ids]
        
        # Ensure bulletin_ids is a list if provided
        if bulletin_ids and not isinstance(bulletin_ids, list):
            logger.info(f"Converting bulletin_ids to list: {bulletin_ids}")
            bulletin_ids = [bulletin_ids]
        
        logger.info(f"Final device_ids: {device_ids}, bulletin_ids: {bulletin_ids}, severity: {severity}")
        
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
        severity = arguments.get("severity")
        category = arguments.get("category")
        limit = arguments.get("limit", 100)
        
        if not device_id:
            raise ValueError("device_id is required")
        
        # Prepare request body (application/x-www-form-urlencoded)
        data = {
            "deviceId": device_id,
            "limit": limit
        }
        
        if severity:
            data["severity"] = severity
        if category:
            data["category"] = category
        
        # Make API request to get missing updates
        headers = await self.auth.get_headers()
        response = await self.auth._client.post(
            "/software-updates/v1/missing-updates",
            headers=headers,
            data=data  # httpx will automatically set Content-Type to application/x-www-form-urlencoded
        )
        
        if response.status_code == 200:
            data = response.json()
            updates = []
            
            for item in data.get("items", []):
                update = {
                    "bulletin_id": item.get("bulletinId"),
                    "title": item.get("title"),
                    "severity": item.get("severity"),
                    "category": item.get("category"),
                    "description": item.get("description"),
                    "published_date": item.get("publishedDate"),
                    "vendor": item.get("vendor"),
                    "product": item.get("product"),
                    "version": item.get("version")
                }
                updates.append(update)
            
            # Format the response as text for better AI understanding
            summary = {
                "total": len(updates),
                "critical": len([u for u in updates if u.get("severity") == "critical"]),
                "important": len([u for u in updates if u.get("severity") == "important"]),
                "security": len([u for u in updates if u.get("category") == "security"])
            }
            
            response_text = f"Found {len(updates)} missing software update(s) for device {device_id}\n\n"
            response_text += f"Device ID: {device_id}\n"
            response_text += f"Summary: {summary['total']} total ({summary['critical']} critical, {summary['important']} important, {summary['security']} security)\n\n"
            if updates:
                response_text += "Updates:\n"
                for update in updates:
                    response_text += f"- {update['bulletin_id']}: {update['severity']} / {update['category']}\n"
                response_text += "\n---\n"
                response_text += "To install an update, call install_software_updates with:\n"
                response_text += f"  device_ids: [\"{device_id}\"]\n"
                response_text += "  bulletin_ids: [\"<BULLETIN_ID>\"]\n"
                response_text += "\nExample for the first update:\n"
                response_text += f"  device_ids: [\"{device_id}\"]\n"
                response_text += f"  bulletin_ids: [\"{updates[0]['bulletin_id']}\"]\n"
                response_text += "\nCRITICAL: Both parameters must be ARRAYS, not strings!"
            else:
                response_text += "No missing updates for this device."
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: Failed to get missing updates: {response.status_code} - {response.text}"
                    }
                ]
            }
    
    async def _scan_for_updates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a scan for software updates on specified devices."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Get device IDs
        device_ids = arguments.get("device_ids", [])
        
        # Support both singular and plural forms
        if not device_ids and "device_id" in arguments:
            device_ids = [arguments["device_id"]]
        
        if not device_ids:
            return {
                "success": False,
                "message": "No device IDs provided"
            }
        
        logger.info(f"Scanning for updates on {len(device_ids)} device(s): {device_ids}")
        
        # Build request body
        request_body = {
            "operation": "scanForUpdates",
            "targets": device_ids
        }
        
        # Make API request
        headers = await self.auth.get_headers()
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
            
            return {
                "success": True,
                "message": f"Scan for updates triggered on {len(device_ids)} device(s)",
                "results": results,
                "transaction_id": data.get("transactionId")
            }
        else:
            return {
                "success": False,
                "message": f"Failed to trigger scan for updates: {response.status_code}",
                "error": response.text
            }

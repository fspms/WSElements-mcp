"""
MCP module for WithSecure Elements incidents (BCDs) management.
"""

from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import BaseModel

from .base import BaseModule
from ..auth import WithSecureAuth
from ..config import WithSecureConfig


class IncidentFilters(BaseModel):
    """Filters for incident search."""
    
    organization_id: Optional[str] = None
    incident_id: Optional[str] = None
    created_timestamp_start: Optional[str] = None
    created_timestamp_end: Optional[str] = None
    updated_timestamp_start: Optional[str] = None
    updated_timestamp_end: Optional[str] = None
    archived: Optional[bool] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = 100
    anchor: Optional[str] = None


class IncidentComment(BaseModel):
    """Model for incident comment."""
    
    targets: List[str]
    comment: str


class DetectionFilters(BaseModel):
    """Filters for detection search."""
    
    organization_id: Optional[str] = None
    incident_id: str
    anchor: Optional[str] = None
    limit: Optional[int] = 100


class IncidentsModule(BaseModule):
    """Module for incidents (Broad Context Detections) management."""
    
    @property
    def name(self) -> str:
        return "incidents"
    
    @property
    def description(self) -> str:
        return "WithSecure Elements incidents (Broad Context Detections) management"
    
    def _register_resources(self) -> None:
        """Register resources for incidents."""
        
        # Add resources to the list for HTTP transport
        self._resources.extend([
            {
                "uri": "withsecure://incidents",
                "name": "Incidents",
                "description": "WithSecure Elements incidents list",
                "mimeType": "application/json"
            },
            {
                "uri": "withsecure://incidents/comments",
                "name": "Incident Comments",
                "description": "WithSecure Elements incident comments",
                "mimeType": "application/json"
            },
            {
                "uri": "withsecure://incidents/detections",
                "name": "Incident Detections",
                "description": "WithSecure Elements incident detections",
                "mimeType": "application/json"
            }
        ])
        
        @self.server.list_resources()
        async def list_incidents() -> List[Resource]:
            """List available incident resources."""
            return [
                Resource(
                    uri="withsecure://incidents",
                    name="Incidents",
                    description="WithSecure Elements incidents list",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_incident(uri: str) -> str:
            """Read an incident resource."""
            if uri == "withsecure://incidents":
                # Get incidents list
                incidents = await self._get_incidents()
                return incidents
            elif uri.startswith("withsecure://incidents/"):
                # Get specific incident
                incident_id = uri.split("/")[-1]
                incident = await self._get_incident(incident_id)
                return incident
            else:
                raise ValueError(f"Unrecognized resource URI: {uri}")
    
    def _register_tools(self) -> None:
        """Register tools for incidents."""
        
        # Add tools to the list for HTTP transport
        self._tools.extend([
            {
                "name": "list_incidents",
                "description": "List WithSecure Elements incidents (BCDs)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID (optional)"
                        },
                        "archived": {
                            "type": "boolean",
                            "description": "Filter by archive status"
                        },
                        "severity": {
                            "type": "string",
                            "description": "Filter by severity level"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of incidents to return",
                            "default": 100
                        },
                        "created_timestamp_start": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Start of creation time range"
                        },
                        "created_timestamp_end": {
                            "type": "string",
                            "format": "date-time",
                            "description": "End of creation time range"
                        }
                    }
                }
            },
            {
                "name": "get_incident",
                "description": "Retrieve details of a specific incident",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "Incident ID"
                        }
                    },
                    "required": ["incident_id"]
                }
            },
            {
                "name": "update_incident_status",
                "description": "Update incident status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "Incident ID"
                        },
                        "status": {
                            "type": "string",
                            "description": "New incident status"
                        }
                    },
                    "required": ["incident_id", "status"]
                }
            },
            {
                "name": "archive_incident",
                "description": "Archive an incident",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "Incident ID"
                        }
                    },
                    "required": ["incident_id"]
                }
            },
            {
                "name": "unarchive_incident",
                "description": "Unarchive an incident",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "Incident ID"
                        }
                    },
                    "required": ["incident_id"]
                }
            },
            {
                "name": "add_incident_comment",
                "description": "Add comment to incidents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of incident IDs to add comment to"
                        },
                        "comment": {
                            "type": "string",
                            "description": "Comment text to add"
                        }
                    },
                    "required": ["targets", "comment"]
                }
            },
            {
                "name": "list_incident_detections",
                "description": "List detections for a specific incident",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "Incident ID to get detections for"
                        },
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of detections to return",
                            "default": 100
                        },
                        "anchor": {
                            "type": "string",
                            "description": "Pagination anchor for next page"
                        }
                    },
                    "required": ["incident_id"]
                }
            }
        ])
        
        @self.server.list_tools()
        async def list_incident_tools() -> List[Tool]:
            """List available tools for incidents."""
            return [
                Tool(
                    name="list_incidents",
                    description="List WithSecure Elements incidents (BCDs)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "string",
                                "description": "Organization ID (optional)"
                            },
                            "archived": {
                                "type": "boolean",
                                "description": "Filter by archive status"
                            },
                            "severity": {
                                "type": "string",
                                "description": "Filter by severity level"
                            },
                            "status": {
                                "type": "string",
                                "description": "Filter by status"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of incidents to return",
                                "default": 100
                            },
                            "created_timestamp_start": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Start of creation time range"
                            },
                            "created_timestamp_end": {
                                "type": "string",
                                "format": "date-time",
                                "description": "End of creation time range"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_incident",
                    description="Retrieve details of a specific incident",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "incident_id": {
                                "type": "string",
                                "description": "Incident ID"
                            }
                        },
                        "required": ["incident_id"]
                    }
                ),
                Tool(
                    name="update_incident_status",
                    description="Update incident status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "incident_id": {
                                "type": "string",
                                "description": "Incident ID"
                            },
                            "status": {
                                "type": "string",
                                "description": "New incident status"
                            }
                        },
                        "required": ["incident_id", "status"]
                    }
                ),
                Tool(
                    name="archive_incident",
                    description="Archive an incident",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "incident_id": {
                                "type": "string",
                                "description": "Incident ID"
                            }
                        },
                        "required": ["incident_id"]
                    }
                ),
                Tool(
                    name="unarchive_incident",
                    description="Unarchive an incident",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "incident_id": {
                                "type": "string",
                                "description": "Incident ID"
                            }
                        },
                        "required": ["incident_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_incident_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute an incident tool."""
            if name == "list_incidents":
                filters = IncidentFilters(**arguments)
                incidents = await self._get_incidents(filters)
                return [TextContent(type="text", text=incidents)]
            
            elif name == "get_incident":
                incident_id = arguments["incident_id"]
                incident = await self._get_incident(incident_id)
                return [TextContent(type="text", text=incident)]
            
            elif name == "update_incident_status":
                incident_id = arguments["incident_id"]
                status = arguments["status"]
                result = await self._update_incident_status(incident_id, status)
                return [TextContent(type="text", text=result)]
            
            elif name == "archive_incident":
                incident_id = arguments["incident_id"]
                result = await self._archive_incident(incident_id)
                return [TextContent(type="text", text=result)]
            
            elif name == "unarchive_incident":
                incident_id = arguments["incident_id"]
                result = await self._unarchive_incident(incident_id)
                return [TextContent(type="text", text=result)]
            
            else:
                raise ValueError(f"Unrecognized tool: {name}")
    
    async def _get_incidents(self, filters: Optional[IncidentFilters] = None) -> str:
        """Retrieve incidents list."""
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
            
            if filters.incident_id:
                params["incidentId"] = filters.incident_id
            if filters.created_timestamp_start:
                params["createdTimestampStart"] = filters.created_timestamp_start
            if filters.created_timestamp_end:
                params["createdTimestampEnd"] = filters.created_timestamp_end
            if filters.updated_timestamp_start:
                params["updatedTimestampStart"] = filters.updated_timestamp_start
            if filters.updated_timestamp_end:
                params["updatedTimestampEnd"] = filters.updated_timestamp_end
            if filters.archived is not None:
                params["archived"] = str(filters.archived).lower()
            if filters.severity:
                params["severity"] = filters.severity
            if filters.status:
                params["status"] = filters.status
            if filters.limit:
                params["limit"] = filters.limit
            if filters.anchor:
                params["anchor"] = filters.anchor
        
        response = await self.auth._client.get(
            "/incidents/v1/incidents",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving incidents: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_incident(self, incident_id: str) -> str:
        """Retrieve details of a specific incident."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        params = {"incidentId": incident_id}
        
        if self.config.organization_id:
            params["organizationId"] = self.config.organization_id
        
        response = await self.auth._client.get(
            "/incidents/v1/incidents",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving incident: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _update_incident_status(self, incident_id: str, status: str) -> str:
        """Update incident status."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "incidentId": incident_id,
            "status": status
        }
        
        response = await self.auth._client.put(
            f"/incidents/v1/incidents/{incident_id}/status",
            headers=headers,
            json=data
        )
        
        if response.status_code not in [200, 204]:
            raise Exception(f"Error updating status: {response.status_code} - {response.text}")
        
        return json.dumps({"success": True, "message": f"Incident {incident_id} status updated to {status}"})
    
    async def _archive_incident(self, incident_id: str) -> str:
        """Archive an incident."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.post(
            f"/incidents/v1/incidents/{incident_id}/archive",
            headers=headers
        )
        
        if response.status_code not in [200, 204]:
            raise Exception(f"Error archiving: {response.status_code} - {response.text}")
        
        return json.dumps({"success": True, "message": f"Incident {incident_id} archived"})
    
    async def _unarchive_incident(self, incident_id: str) -> str:
        """Unarchive an incident."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.post(
            f"/incidents/v1/incidents/{incident_id}/unarchive",
            headers=headers
        )
        
        if response.status_code not in [200, 204]:
            raise Exception(f"Error unarchiving: {response.status_code} - {response.text}")
        
        return json.dumps({"success": True, "message": f"Incident {incident_id} unarchived"})
    
    async def _add_incident_comment(self, targets: List[str], comment: str) -> str:
        """Add comment to incidents."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "targets": targets,
            "comment": comment
        }
        
        response = await self.auth._client.post(
            "/incidents/v1/comments",
            headers=headers,
            json=data
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Error adding comment: {response.status_code} - {response.text}")
        
        return json.dumps({"success": True, "message": f"Comment added to {len(targets)} incident(s)"})
    
    async def _get_incident_detections(self, incident_id: str, organization_id: Optional[str] = None, 
                                     limit: int = 100, anchor: Optional[str] = None) -> str:
        """Retrieve detections for a specific incident."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        params = {
            "incidentId": incident_id,
            "limit": limit
        }
        
        if organization_id:
            params["organizationId"] = organization_id
        elif self.config.organization_id:
            params["organizationId"] = self.config.organization_id
        
        if anchor:
            params["anchor"] = anchor
        
        response = await self.auth._client.get(
            "/incidents/v1/detections",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving detections: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        try:
            if tool_name == "list_incidents":
                filters = IncidentFilters(**arguments)
                incidents = await self._get_incidents(filters)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": incidents
                        }
                    ]
                }
            
            elif tool_name == "get_incident":
                incident_id = arguments["incident_id"]
                incident = await self._get_incident(incident_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": incident
                        }
                    ]
                }
            
            elif tool_name == "update_incident_status":
                incident_id = arguments["incident_id"]
                status = arguments["status"]
                result = await self._update_incident_status(incident_id, status)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "archive_incident":
                incident_id = arguments["incident_id"]
                result = await self._archive_incident(incident_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "unarchive_incident":
                incident_id = arguments["incident_id"]
                result = await self._unarchive_incident(incident_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "add_incident_comment":
                targets = arguments["targets"]
                comment = arguments["comment"]
                result = await self._add_incident_comment(targets, comment)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "list_incident_detections":
                incident_id = arguments["incident_id"]
                organization_id = arguments.get("organization_id")
                limit = arguments.get("limit", 100)
                anchor = arguments.get("anchor")
                detections = await self._get_incident_detections(incident_id, organization_id, limit, anchor)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": detections
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

"""
MCP module for WithSecure Elements security events management.
"""

from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import BaseModel

from .base import BaseModule
from ..auth import WithSecureAuth
from ..config import WithSecureConfig


class EventFilters(BaseModel):
    """Filters for event search."""
    
    organization_id: Optional[str] = None
    event_id: Optional[str] = None
    created_timestamp_start: Optional[str] = None
    created_timestamp_end: Optional[str] = None
    device_id: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    limit: Optional[int] = 100
    anchor: Optional[str] = None


class EventsModule(BaseModule):
    """Module for security events management."""
    
    @property
    def name(self) -> str:
        return "events"
    
    @property
    def description(self) -> str:
        return "WithSecure Elements security events management"
    
    def _register_resources(self) -> None:
        """Register resources for events."""
        
        @self.server.list_resources()
        async def list_events() -> List[Resource]:
            """List available event resources."""
            return [
                Resource(
                    uri="withsecure://events",
                    name="Security Events",
                    description="WithSecure Elements security events list",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_event(uri: str) -> str:
            """Read an event resource."""
            if uri == "withsecure://events":
                # Get events list
                events = await self._get_events()
                return events
            elif uri.startswith("withsecure://events/"):
                # Get specific event
                event_id = uri.split("/")[-1]
                event = await self._get_event(event_id)
                return event
            else:
                raise ValueError(f"Unrecognized resource URI: {uri}")
    
    def _register_tools(self) -> None:
        """Register tools for events."""
        
        @self.server.list_tools()
        async def list_event_tools() -> List[Tool]:
            """List available tools for events."""
            return [
                Tool(
                    name="list_events",
                    description="List WithSecure Elements security events",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "string",
                                "description": "Organization ID (optional)"
                            },
                            "device_id": {
                                "type": "string",
                                "description": "Filter by device ID"
                            },
                            "event_type": {
                                "type": "string",
                                "description": "Filter by event type"
                            },
                            "severity": {
                                "type": "string",
                                "description": "Filter by severity level"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of events to return",
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
                    name="get_event",
                    description="Retrieve details of a specific event",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "Event ID"
                            }
                        },
                        "required": ["event_id"]
                    }
                ),
                Tool(
                    name="get_event_types",
                    description="Retrieve list of available event types",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_event_statistics",
                    description="Retrieve event statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "string",
                                "description": "Organization ID (optional)"
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
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_event_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute an event tool."""
            if name == "list_events":
                filters = EventFilters(**arguments)
                events = await self._get_events(filters)
                return [TextContent(type="text", text=events)]
            
            elif name == "get_event":
                event_id = arguments["event_id"]
                event = await self._get_event(event_id)
                return [TextContent(type="text", text=event)]
            
            elif name == "get_event_types":
                event_types = await self._get_event_types()
                return [TextContent(type="text", text=event_types)]
            
            elif name == "get_event_statistics":
                stats = await self._get_event_statistics(arguments)
                return [TextContent(type="text", text=stats)]
            
            else:
                raise ValueError(f"Unrecognized tool: {name}")
    
    async def _get_events(self, filters: Optional[EventFilters] = None) -> str:
        """Retrieve events list."""
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
            
            if filters.event_id:
                params["eventId"] = filters.event_id
            if filters.created_timestamp_start:
                params["createdTimestampStart"] = filters.created_timestamp_start
            if filters.created_timestamp_end:
                params["createdTimestampEnd"] = filters.created_timestamp_end
            if filters.device_id:
                params["deviceId"] = filters.device_id
            if filters.event_type:
                params["eventType"] = filters.event_type
            if filters.severity:
                params["severity"] = filters.severity
            if filters.limit:
                params["limit"] = filters.limit
            if filters.anchor:
                params["anchor"] = filters.anchor
        
        response = await self.auth._client.get(
            "/events/v1/events",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving events: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_event(self, event_id: str) -> str:
        """Retrieve details of a specific event."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        params = {"eventId": event_id}
        
        if self.config.organization_id:
            params["organizationId"] = self.config.organization_id
        
        response = await self.auth._client.get(
            "/events/v1/events",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving event: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_event_types(self) -> str:
        """Retrieve list of available event types."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.get(
            "/events/v1/event-types",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving event types: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_event_statistics(self, filters: Dict[str, Any]) -> str:
        """Retrieve event statistics."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        params = {}
        
        if filters.get("organization_id"):
            params["organizationId"] = filters["organization_id"]
        elif self.config.organization_id:
            params["organizationId"] = self.config.organization_id
        
        if filters.get("created_timestamp_start"):
            params["createdTimestampStart"] = filters["created_timestamp_start"]
        if filters.get("created_timestamp_end"):
            params["createdTimestampEnd"] = filters["created_timestamp_end"]
        
        response = await self.auth._client.get(
            "/events/v1/statistics",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving statistics: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)

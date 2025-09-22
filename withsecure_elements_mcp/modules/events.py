"""
MCP module for WithSecure Elements security events management.
"""

from typing import Any, Dict, List, Optional, Union
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import BaseModel

from .base import BaseModule
from ..auth import WithSecureAuth
from ..config import WithSecureConfig


# ===== CONSTANTES DE VALIDATION DEPUIS LES SPÉCIFICATIONS API =====
# Extraites de api-spec (1).yaml et api-spec (2).yaml

# Engines (moteurs de sécurité) - Liste complète depuis les spécifications
ALLOWED_ENGINES: List[str] = [
    "AMSI",
    "activityMonitor",
    "activityMonitorClientProtection",
    "applicationControl",
    "browsingProtection",
    "cloudIdentityAzure",
    "cloudWorkloadAzure",
    "connectionControl",
    "connector",
    "dataGuard",
    "deepGuard",
    "deviceControl",
    "edr",
    "emailBreach",
    "emailScan",
    "fileScanning",
    "firewall",
    "inboxRuleScan",
    "integrityChecker",
    "oneDriveScan",
    "realtimeScanning",
    "reputationBasedBrowsing",
    "setting",
    "sharePointScan",
    "systemEventsLog",
    "tamperProtection",
    "teamsScan",
    "webContentControl",
    "webTrafficScanning",
    "xFence",
    "xmRecommendation",
    # Engines supplémentaires de la spécification 2
    "manualScanning",
    "cloud",  # deprecated mais encore présent
]

# Engine Groups (groupes de moteurs)
ALLOWED_ENGINE_GROUPS: List[str] = ["epp", "edr", "ecp", "xm"]

# Severities (niveaux de gravité)
ALLOWED_SEVERITIES: List[str] = ["critical", "warning", "info"]

# Count values (pour l'agrégation)
ALLOWED_COUNT_VALUES: List[str] = [
    "engine",
    "url",
    "alertType", 
    "deviceId",
    "infectionName",
    "categories",
    "appliedRule",
    "filePath",
    "description"
]

# Order (ordre de tri)
ALLOWED_ORDER_VALUES: List[str] = ["asc", "desc"]

# Language (langues supportées)
ALLOWED_LANGUAGES: List[str] = [
    "en",      # English
    "de",      # German
    "es-MX",   # Spanish (Mexico)
    "fi",      # Finnish
    "fr",      # French
    "it",      # Italian
    "ja",      # Japanese
    "pl",      # Polish
    "pt-BR",   # Portuguese (Brazil)
    "sv",      # Swedish
    "zh-TW"    # Chinese (Taiwan)
]

# Actions (actions effectuées)
ALLOWED_ACTIONS: List[str] = [
    "none",
    "blocked",
    "renamed", 
    "deleted",
    "disinfected",
    "quarantined",
    "created",
    "closed",
    "merged",
    "updated",
    "reported"
]

# Limites
SECURITY_EVENTS_LIMIT_MIN = 1
SECURITY_EVENTS_LIMIT_MAX = 200

# Mapping des engines vers leurs groupes
ENGINE_TO_GROUP_MAPPING: Dict[str, str] = {
    # EPP (Endpoint Protection)
    "AMSI": "epp",
    "activityMonitor": "epp", 
    "activityMonitorClientProtection": "epp",
    "applicationControl": "epp",
    "browsingProtection": "epp",
    "connectionControl": "epp",
    "dataGuard": "epp",
    "deepGuard": "epp", 
    "deviceControl": "epp",
    "fileScanning": "epp",
    "firewall": "epp",
    "integrityChecker": "epp",
    "manualScanning": "epp",
    "realtimeScanning": "epp",
    "reputationBasedBrowsing": "epp",
    "setting": "epp",
    "systemEventsLog": "epp",
    "tamperProtection": "epp",
    "webContentControl": "epp",
    "webTrafficScanning": "epp",
    "xFence": "epp",
    
    # EDR (Detection and Response)
    "edr": "edr",
    
    # ECP (Collaboration Protection)
    "emailBreach": "ecp",
    "emailScan": "ecp",
    "inboxRuleScan": "ecp",
    "oneDriveScan": "ecp",
    "sharePointScan": "ecp",
    "teamsScan": "ecp",
    "cloudIdentityAzure": "ecp",
    "cloudWorkloadAzure": "ecp",
    "cloud": "ecp",  # deprecated
    
    # XM (Exposure Management)
    "xmRecommendation": "xm",
    
    # Connector
    "connector": "epp"
}


class EventFilters(BaseModel):
    """Filters for event search."""
    
    organization_id: Optional[str] = None
    event_id: Optional[str] = None
    created_timestamp_start: Optional[str] = None
    created_timestamp_end: Optional[str] = None
    device_id: Optional[str] = None
    # Accept single or multiple engines/severities/engine groups
    event_type: Optional[Union[str, List[str]]] = None
    engine_group: Optional[Union[str, List[str]]] = None
    severity: Optional[Union[str, List[str]]] = None
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
        
        # Add resources to the list for HTTP transport
        self._resources.append({
            "uri": "withsecure://events",
            "name": "Security Events",
            "description": "WithSecure Elements security events list",
            "mimeType": "application/json"
        })
        
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
        
        # Add tools to the list for HTTP transport
        self._tools.extend([
            {
                "name": "list_events",
                "description": "List WithSecure Elements security events",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID (optional)"
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Filter by device ID (targetId)"
                        },
                        "event_type": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "array", "items": {"type": "string"}}
                            ],
                            "description": "Filter by engine(s). Use get_event_types to see allowed values"
                        },
                        "engine_group": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "array", "items": {"type": "string"}}
                            ],
                            "description": "Filter by engine group(s). Allowed: epp, edr, ecp, xm"
                        },
                        "severity": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "array", "items": {"type": "string"}}
                            ],
                            "description": "Filter by severity(ies). Allowed: critical, warning, info"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of events to return",
                            "default": 100
                        },
                        "created_timestamp_start": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Start of persistence time range (persistenceTimestampStart)"
                        },
                        "created_timestamp_end": {
                            "type": "string",
                            "format": "date-time",
                            "description": "End of persistence time range (persistenceTimestampEnd)"
                        }
                    }
                }
            },
            {
                "name": "get_event",
                "description": "Retrieve details of a specific event",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "Event ID"
                        }
                    },
                    "required": ["event_id"]
                }
            },
            {
                "name": "get_event_types",
                "description": "Retrieve list of available event types and all allowed values for filtering",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_event_statistics",
                "description": "Retrieve event statistics",
                "inputSchema": {
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
            }
        ])
        
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
                                "description": "Filter by device ID (targetId)"
                            },
                            "event_type": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "string"}}
                                ],
                                "description": "Filter by engine(s). Use get_event_types to see allowed values"
                            },
                            "engine_group": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "string"}}
                                ],
                                "description": "Filter by engine group(s). Allowed: epp, edr, ecp, xm"
                            },
                            "severity": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "string"}}
                                ],
                                "description": "Filter by severity(ies). Allowed: critical, warning, info"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of events to return",
                                "default": 100
                            },
                            "created_timestamp_start": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Start of persistence time range (persistenceTimestampStart)"
                            },
                            "created_timestamp_end": {
                                "type": "string",
                                "format": "date-time",
                                "description": "End of persistence time range (persistenceTimestampEnd)"
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
                    description="Retrieve list of available event types and all allowed values for filtering",
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
    
    def _ensure_list(self, value: Optional[Union[str, List[str]]]) -> Optional[List[str]]:
        if value is None:
            return None
        if isinstance(value, list):
            return value
        return [value]

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
            
            # Map parameters to correct API names
            if filters.created_timestamp_start:
                params["persistenceTimestampStart"] = filters.created_timestamp_start
            if filters.created_timestamp_end:
                params["persistenceTimestampEnd"] = filters.created_timestamp_end
            if filters.device_id:
                params["targetId"] = filters.device_id
            # Validate and map engines
            engines = self._ensure_list(filters.event_type)
            if engines:
                invalid = [e for e in engines if e not in ALLOWED_ENGINES]
                if invalid:
                    raise ValueError(
                        "Invalid engine(s): " + ", ".join(invalid) +
                        ". Allowed: " + ", ".join(ALLOWED_ENGINES)
                    )
                params["engine"] = engines
            # Validate and map engine groups
            engine_groups = self._ensure_list(filters.engine_group)
            if engine_groups:
                invalid_g = [g for g in engine_groups if g not in ALLOWED_ENGINE_GROUPS]
                if invalid_g:
                    raise ValueError(
                        "Invalid engine_group(s): " + ", ".join(invalid_g) +
                        ". Allowed: epp, edr, ecp, xm"
                    )
                params["engineGroup"] = engine_groups
            # Validate and map severities
            severities = self._ensure_list(filters.severity)
            if severities:
                invalid_s = [s for s in severities if s not in ALLOWED_SEVERITIES]
                if invalid_s:
                    raise ValueError(
                        "Invalid severity(ies): " + ", ".join(invalid_s) +
                        ". Allowed: critical, warning, info"
                    )
                params["severity"] = severities
            if filters.limit:
                params["limit"] = filters.limit
            if filters.anchor:
                params["anchor"] = filters.anchor
                
        # Add required parameters if not provided
        if "persistenceTimestampStart" not in params and "persistenceTimestampEnd" not in params:
            # Default to last 24 hours if no time range specified
            from datetime import datetime, timedelta
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=1)
            params["persistenceTimestampStart"] = start_time.isoformat() + "Z"
            params["persistenceTimestampEnd"] = end_time.isoformat() + "Z"
        
        # Add default engine group if no engine specified
        if "engine" not in params and "engineGroup" not in params:
            params["engineGroup"] = "epp"  # Default to Endpoint Protection
        
        # Add required headers for security events endpoint
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Accept"] = "application/json"
        
        response = await self.auth._client.post(
            "/security-events/v1/security-events",
            headers=headers,
            data=params
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
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Accept"] = "application/json"
        
        params = {"targetId": event_id}  # Use targetId instead of eventId
        
        if self.config.organization_id:
            params["organizationId"] = self.config.organization_id
            
        # Add required time range parameters
        from datetime import datetime, timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)  # Search last 7 days
        params["persistenceTimestampStart"] = start_time.isoformat() + "Z"
        params["persistenceTimestampEnd"] = end_time.isoformat() + "Z"
        
        # Add default engine group
        params["engineGroup"] = "epp"
        
        response = await self.auth._client.post(
            "/security-events/v1/security-events",
            headers=headers,
            data=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving event: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_event_types(self) -> str:
        """Retrieve list of available event types and all allowed values."""
        import json
        # Event types endpoint not available; return allowed engines and all values from spec
        return json.dumps({
            "engines": ALLOWED_ENGINES,
            "engineGroups": ALLOWED_ENGINE_GROUPS,
            "severities": ALLOWED_SEVERITIES,
            "countValues": ALLOWED_COUNT_VALUES,
            "orderValues": ALLOWED_ORDER_VALUES,
            "languages": ALLOWED_LANGUAGES,
            "actions": ALLOWED_ACTIONS,
            "limits": {
                "min": SECURITY_EVENTS_LIMIT_MIN,
                "max": SECURITY_EVENTS_LIMIT_MAX
            },
            "engineGroupMapping": ENGINE_TO_GROUP_MAPPING,
            "note": "Toutes les valeurs autorisées extraites des spécifications API officielles"
        }, indent=2, ensure_ascii=False)

    
    async def _get_event_statistics(self, filters: Dict[str, Any]) -> str:
        """Retrieve event statistics."""
        import json
        
        # Statistics endpoint not available in WithSecure Elements API
        # Use aggregation feature instead
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Accept"] = "application/vnd.withsecure.aggr+json"
        
        params = {}
        
        if filters.get("organization_id"):
            params["organizationId"] = filters["organization_id"]
        elif self.config.organization_id:
            params["organizationId"] = self.config.organization_id
        
        if filters.get("created_timestamp_start"):
            params["persistenceTimestampStart"] = filters["created_timestamp_start"]
        if filters.get("created_timestamp_end"):
            params["persistenceTimestampEnd"] = filters["created_timestamp_end"]
        
        # Add required parameters for aggregation
        params["count"] = "engine"  # Group by engine
        params["engineGroup"] = "epp"  # Default to EPP events
        
        response = await self.auth._client.post(
            "/security-events/v1/security-events",
            headers=headers,
            data=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving statistics: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        try:
            if tool_name == "list_events":
                filters = EventFilters(**arguments)
                events = await self._get_events(filters)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": events
                        }
                    ]
                }
            
            elif tool_name == "get_event":
                event_id = arguments["event_id"]
                event = await self._get_event(event_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": event
                        }
                    ]
                }
            
            elif tool_name == "get_event_types":
                event_types = await self._get_event_types()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": event_types
                        }
                    ]
                }
            
            elif tool_name == "get_event_statistics":
                statistics = await self._get_event_statistics(arguments)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": statistics
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

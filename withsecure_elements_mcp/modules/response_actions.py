"""
MCP module for WithSecure Elements response actions management.
"""

import json
from typing import Any, Dict, List, Optional
from mcp.types import Resource, Tool, TextContent
from pydantic import BaseModel

from .base import BaseModule


class ResponseActionFilters(BaseModel):
    """Filters for response actions search."""
    
    organization_id: str
    order: Optional[str] = "desc"
    anchor: Optional[str] = None
    limit: Optional[int] = 100


class ResponseActionCreate(BaseModel):
    """Model for creating response actions."""
    
    targets: List[str]
    organization_id: str
    action_type: str
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
                "uri": "withsecure://response-actions",
                "name": "Response Actions",
                "description": "WithSecure Elements response actions list",
                "mimeType": "application/json"
            },
            {
                "uri": "withsecure://response-actions/responses",
                "name": "Response Actions Responses",
                "description": "WithSecure Elements response actions responses",
                "mimeType": "application/json"
            }
        ])
        
        @self.server.list_resources()
        async def list_response_actions() -> List[Resource]:
            """List available response action resources."""
            return [
                Resource(
                    uri="withsecure://response-actions",
                    name="Response Actions",
                    description="WithSecure Elements response actions list",
                    mimeType="application/json"
                ),
                Resource(
                    uri="withsecure://response-actions/responses",
                    name="Response Actions Responses",
                    description="WithSecure Elements response actions responses",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_response_action(uri: str) -> str:
            """Read a response action resource."""
            if uri == "withsecure://response-actions":
                # Get response actions list
                actions = await self._get_response_actions()
                return actions
            elif uri == "withsecure://response-actions/responses":
                # Get response actions responses
                responses = await self._get_response_actions_responses()
                return responses
            else:
                raise ValueError(f"Unrecognized resource URI: {uri}")
    
    def _register_tools(self) -> None:
        """Register tools for response actions."""
        
        # Add tools to the list for HTTP transport
        self._tools.extend([
            {
                "name": "list_response_actions_responses",
                "description": "List created response actions on RDR sensors",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "default": "desc",
                            "description": "Sorting order"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of responses to return",
                            "default": 100
                        },
                        "anchor": {
                            "type": "string",
                            "description": "Pagination anchor for next page"
                        }
                    },
                    "required": ["organization_id"]
                }
            },
            {
                "name": "create_response_action",
                "description": "Create new response action on target devices",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of device IDs to target"
                        },
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID"
                        },
                        "action_type": {
                            "type": "string",
                            "enum": [
                                "killThread",
                                "killProcess", 
                                "fullMemoryDump",
                                "collectFile",
                                "collectProcessMemory",
                                "runCommand",
                                "deleteFile",
                                "quarantineFile",
                                "unquarantineFile",
                                "isolateFromNetwork",
                                "releaseFromNetworkIsolation",
                                "restartAgent",
                                "shutdownDevice",
                                "restartDevice"
                            ],
                            "description": "Type of response action to execute"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Action-specific parameters",
                            "properties": {
                                "threadId": {
                                    "type": "string",
                                    "description": "Thread ID (for killThread)"
                                },
                                "match": {
                                    "type": "string",
                                    "description": "Process match pattern (for killProcess)"
                                },
                                "processMatchValues": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Process match values (for killProcess)"
                                },
                                "processMemoryDump": {
                                    "type": "boolean",
                                    "description": "Enable process memory dump (for killProcess)"
                                },
                                "memoryDumpFlag": {
                                    "type": "string",
                                    "description": "Memory dump flag (for killProcess)"
                                },
                                "winpmemVersion": {
                                    "type": "string",
                                    "description": "WinPmem version (for fullMemoryDump)"
                                },
                                "collectProfile": {
                                    "type": "string",
                                    "description": "Collect profile (for fullMemoryDump)"
                                },
                                "filePath": {
                                    "type": "string",
                                    "description": "File path (for collectFile, deleteFile, quarantineFile, unquarantineFile)"
                                },
                                "command": {
                                    "type": "string",
                                    "description": "Command to run (for runCommand)"
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Message to display (for isolateFromNetwork)"
                                }
                            }
                        }
                    },
                    "required": ["targets", "organization_id", "action_type"]
                }
            }
        ])
        
        @self.server.list_tools()
        async def list_response_action_tools() -> List[Tool]:
            """List available tools for response actions."""
            return [
                Tool(
                    name="list_response_actions_responses",
                    description="List created response actions on RDR sensors",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "string",
                                "description": "Organization ID"
                            },
                            "order": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "default": "desc",
                                "description": "Sorting order"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of responses to return",
                                "default": 100
                            },
                            "anchor": {
                                "type": "string",
                                "description": "Pagination anchor for next page"
                            }
                        },
                        "required": ["organization_id"]
                    }
                ),
                Tool(
                    name="create_response_action",
                    description="Create new response action on target devices",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "targets": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of device IDs to target"
                            },
                            "organization_id": {
                                "type": "string",
                                "description": "Organization ID"
                            },
                            "action_type": {
                                "type": "string",
                                "enum": [
                                    "killThread",
                                    "killProcess", 
                                    "fullMemoryDump",
                                    "collectFile",
                                    "collectProcessMemory",
                                    "runCommand",
                                    "deleteFile",
                                    "quarantineFile",
                                    "unquarantineFile",
                                    "isolateFromNetwork",
                                    "releaseFromNetworkIsolation",
                                    "restartAgent",
                                    "shutdownDevice",
                                    "restartDevice"
                                ],
                                "description": "Type of response action to execute"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Action-specific parameters"
                            }
                        },
                        "required": ["targets", "organization_id", "action_type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_response_action_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Call a response action tool."""
            if name == "list_response_actions_responses":
                filters = ResponseActionFilters(**arguments)
                responses = await self._get_response_actions_responses(filters)
                return [TextContent(type="text", text=responses)]
            
            elif name == "create_response_action":
                action_data = ResponseActionCreate(**arguments)
                result = await self._create_response_action(action_data)
                return [TextContent(type="text", text=result)]
            
            else:
                raise ValueError(f"Unrecognized tool: {name}")
    
    async def _get_response_actions_responses(self, filters: ResponseActionFilters) -> str:
        """Retrieve response actions responses list."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        params = {
            "organizationId": filters.organization_id,
            "order": filters.order,
            "limit": filters.limit
        }
        
        if filters.anchor:
            params["anchor"] = filters.anchor
        
        response = await self.auth._client.get(
            "/response-actions/v1/responses",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving response actions responses: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), ensure_ascii=False, separators=(",", ":"))
    
    async def _create_response_action(self, action_data: ResponseActionCreate) -> str:
        """Create a new response action."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "targets": action_data.targets,
            "organizationId": action_data.organization_id,
            "actionType": action_data.action_type
        }
        
        if action_data.parameters:
            data["parameters"] = action_data.parameters
        
        response = await self.auth._client.post(
            "/response-actions/v1/response-actions",
            headers=headers,
            json=data
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Error creating response action: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), ensure_ascii=False, separators=(",", ":"))
    
    async def _get_response_actions(self) -> str:
        """Retrieve response actions list (placeholder)."""
        return json.dumps({"message": "Response actions list not implemented yet"}, indent=2)

    async def read_resource(self, uri: str) -> Optional[str]:
        """Read a response action resource."""
        if uri == "withsecure://response-actions":
            return await self._get_response_actions()
        if uri == "withsecure://response-actions/responses":
            return await self._get_response_actions_responses(
                ResponseActionFilters(organization_id=self.config.organization_id or "")
            )
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

"""
MCP module for WithSecure Elements organizations management.
"""

from typing import Any, Dict, List, Optional
from mcp.types import Resource, Tool, TextContent

from .base import BaseModule


class OrganizationsModule(BaseModule):
    """Module for organizations management."""
    
    @property
    def name(self) -> str:
        return "organizations"
    
    @property
    def description(self) -> str:
        return "WithSecure Elements organizations management"
    
    def _register_resources(self) -> None:
        """Register resources for organizations."""
        
        # Add resources to the list for HTTP transport
        self._resources.extend([
            {
                "uri": "withsecure://organizations",
                "name": "Organizations",
                "description": "WithSecure Elements organizations list",
                "mimeType": "application/json"
            },
            {
                "uri": "withsecure://organizations/current",
                "name": "Current Organization",
                "description": "Current organization information",
                "mimeType": "application/json"
            }
        ])
        
        @self.server.list_resources()
        async def list_organizations() -> List[Resource]:
            """List available organization resources."""
            return [
                Resource(
                    uri="withsecure://organizations",
                    name="Organizations",
                    description="WithSecure Elements organizations list",
                    mimeType="application/json"
                ),
                Resource(
                    uri="withsecure://organizations/current",
                    name="Current Organization",
                    description="Current organization information",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_organization(uri: str) -> str:
            """Read an organization resource."""
            if uri == "withsecure://organizations":
                # Get organizations list
                organizations = await self._get_organizations()
                return organizations
            elif uri == "withsecure://organizations/current":
                # Get current organization
                current_org = await self._get_current_organization()
                return current_org
            elif uri.startswith("withsecure://organizations/"):
                # Get specific organization
                org_id = uri.split("/")[-1]
                organization = await self._get_organization(org_id)
                return organization
            else:
                raise ValueError(f"Unrecognized resource URI: {uri}")
    
    def _register_tools(self) -> None:
        """Register tools for organizations."""
        
        # Add tools to the list for HTTP transport
        self._tools.extend([
            {
                "name": "get_current_organization",
                "description": "Retrieve current organization information",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "list_organizations",
                "description": "List all accessible organizations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of organizations to return",
                            "default": 100
                        }
                    }
                }
            },
            {
                "name": "get_organization",
                "description": "Retrieve details of a specific organization",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID"
                        }
                    },
                    "required": ["organization_id"]
                }
            }
        ])
        
        @self.server.list_tools()
        async def list_organization_tools() -> List[Tool]:
            """List available tools for organizations."""
            return [
                Tool(
                    name="get_current_organization",
                    description="Retrieve current organization information",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="list_organizations",
                    description="List all accessible organizations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of organizations to return",
                                "default": 100
                            }
                        }
                    }
                ),
                Tool(
                    name="get_organization",
                    description="Retrieve details of a specific organization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "string",
                                "description": "Organization ID"
                            }
                        },
                        "required": ["organization_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_organization_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute an organization tool."""
            if name == "get_current_organization":
                current_org = await self._get_current_organization()
                return [TextContent(type="text", text=current_org)]
            
            elif name == "list_organizations":
                limit = arguments.get("limit", 100)
                organizations = await self._get_organizations(limit)
                return [TextContent(type="text", text=organizations)]
            
            elif name == "get_organization":
                organization_id = arguments["organization_id"]
                organization = await self._get_organization(organization_id)
                return [TextContent(type="text", text=organization)]

            else:
                raise ValueError(f"Unrecognized tool: {name}")
    
    async def _get_current_organization(self) -> str:
        """Retrieve current organization information."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.get(
            "/whoami/v1/whoami",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving user information: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_organizations(self, limit: int = 100) -> str:
        """Retrieve organizations list."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        params = {"limit": limit}
        
        response = await self.auth._client.get(
            "/organizations/v1/organizations",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving organizations: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_organization(self, organization_id: str) -> str:
        """Retrieve a specific organization.

        The Elements API exposes a single list endpoint; a specific organization
        is selected via the organizationId query parameter (there is no
        /organizations/{id} sub-resource, nor settings/statistics endpoints).
        """
        import json

        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        headers = await self.auth.get_headers()

        response = await self.auth._client.get(
            "/organizations/v1/organizations",
            headers=headers,
            params={"organizationId": organization_id}
        )

        if response.status_code != 200:
            raise Exception(f"Error retrieving organization: {response.status_code} - {response.text}")

        return json.dumps(response.json(), indent=2, ensure_ascii=False)

    async def read_resource(self, uri: str) -> Optional[str]:
        """Read an organization resource."""
        if uri == "withsecure://organizations":
            return await self._get_organizations()
        if uri == "withsecure://organizations/current":
            return await self._get_current_organization()
        if uri.startswith("withsecure://organizations/"):
            org_id = uri.split("/")[-1]
            return await self._get_organization(org_id)
        return None

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        try:
            if tool_name == "get_current_organization":
                current_org = await self._get_current_organization()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": current_org
                        }
                    ]
                }
            
            elif tool_name == "list_organizations":
                limit = arguments.get("limit", 100)
                organizations = await self._get_organizations(limit)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": organizations
                        }
                    ]
                }
            
            elif tool_name == "get_organization":
                organization_id = arguments["organization_id"]
                organization = await self._get_organization(organization_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": organization
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

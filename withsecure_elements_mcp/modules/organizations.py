"""
MCP module for WithSecure Elements organizations management.
"""

from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import BaseModel

from .base import BaseModule
from ..auth import WithSecureAuth
from ..config import WithSecureConfig


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
                ),
                Tool(
                    name="get_organization_settings",
                    description="Retrieve organization settings",
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
                ),
                Tool(
                    name="get_organization_statistics",
                    description="Retrieve organization statistics",
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
            
            elif name == "get_organization_settings":
                organization_id = arguments["organization_id"]
                settings = await self._get_organization_settings(organization_id)
                return [TextContent(type="text", text=settings)]
            
            elif name == "get_organization_statistics":
                organization_id = arguments["organization_id"]
                statistics = await self._get_organization_statistics(organization_id)
                return [TextContent(type="text", text=statistics)]
            
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
        """Retrieve details of a specific organization."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.get(
            f"/organizations/v1/organizations/{organization_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving organization: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_organization_settings(self, organization_id: str) -> str:
        """Retrieve organization settings."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.get(
            f"/organizations/v1/organizations/{organization_id}/settings",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving settings: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    
    async def _get_organization_statistics(self, organization_id: str) -> str:
        """Retrieve organization statistics."""
        import json
        
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = await self.auth.get_headers()
        
        response = await self.auth._client.get(
            f"/organizations/v1/organizations/{organization_id}/statistics",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error retrieving statistics: {response.status_code} - {response.text}")
        
        return json.dumps(response.json(), indent=2, ensure_ascii=False)

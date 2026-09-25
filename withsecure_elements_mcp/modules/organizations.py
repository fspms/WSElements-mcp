"""
MCP module for WithSecure Elements organizations management.
"""

from typing import Any, Dict, List, Optional

from .base import BaseModule


ORGANIZATIONS_PATH = "/organizations/v1/organizations"
WHOAMI_PATH = "/whoami/v1/whoami"

# `type` query parameter enum (API default: company)
ALLOWED_ORG_TYPES: List[str] = ["company", "partner"]

# `limit` query parameter bounds (API default: 200)
ORGANIZATIONS_LIMIT_MIN = 1
ORGANIZATIONS_LIMIT_MAX = 1000
ORGANIZATIONS_LIMIT_DEFAULT = 100



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
                "description": "Current API client and organization ID (whoami)",
                "mimeType": "application/json"
            }
        ])

    def _register_tools(self) -> None:
        """Register tools for organizations."""
        self._tools.extend([
            {
                "name": "get_current_organization",
                "description": "Get the authenticated API client ID and its organization ID (whoami)",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "list_organizations",
                "description": "List organizations of a type under an organization (including itself if the type matches)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Parent organization UUID (default: configured/own org)"
                        },
                        "type": {
                            "type": "string",
                            "enum": ALLOWED_ORG_TYPES,
                            "default": "company",
                            "description": "Organization type to list"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": ORGANIZATIONS_LIMIT_MIN,
                            "maximum": ORGANIZATIONS_LIMIT_MAX,
                            "default": ORGANIZATIONS_LIMIT_DEFAULT,
                            "description": "Page size"
                        },
                        "anchor": {
                            "type": "string",
                            "description": "nextAnchor from a previous response"
                        }
                    }
                }
            },
            {
                "name": "get_organization",
                "description": "Get a specific organization (id, name, type)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Organization UUID"
                        }
                    },
                    "required": ["organization_id"]
                }
            }
        ])

    async def _request(self, path: str, params: Dict[str, Any], what: str) -> Dict[str, Any]:
        """GET an endpoint and return the decoded JSON body."""
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        headers = await self.auth.get_headers()
        response = await self.auth._client.get(
            path,
            headers=headers,
            params={k: v for k, v in params.items() if v is not None}
        )

        if response.status_code != 200:
            raise Exception(f"Error retrieving {what}: {response.status_code} - {response.text}")

        return response.json()

    async def _get_current_organization(self) -> str:
        """Retrieve current client/organization information (whoami)."""
        return self._dump(await self._request(WHOAMI_PATH, {}, "user information"))

    async def _get_organizations(
        self,
        limit: Optional[int] = ORGANIZATIONS_LIMIT_DEFAULT,
        anchor: Optional[str] = None,
        organization_id: Optional[str] = None,
        org_type: Optional[str] = None,
    ) -> str:
        """Retrieve a page of organizations."""
        if org_type and org_type not in ALLOWED_ORG_TYPES:
            raise ValueError(
                f"Invalid type: {org_type}. Allowed: " + ", ".join(ALLOWED_ORG_TYPES)
            )
        limit = limit or ORGANIZATIONS_LIMIT_DEFAULT
        params = {
            "organizationId": organization_id or self.config.organization_id,
            "type": org_type,
            "limit": max(ORGANIZATIONS_LIMIT_MIN, min(int(limit), ORGANIZATIONS_LIMIT_MAX)),
            "anchor": anchor,
        }
        return self._dump(await self._request(ORGANIZATIONS_PATH, params, "organizations"))

    async def _get_organization(self, organization_id: str) -> str:
        """Retrieve a specific organization.

        The Elements API only exposes the list endpoint: with organizationId=X
        it returns organizations of the given type under X, including X itself
        when the type matches. There is no /organizations/{id} sub-resource, so
        both types are queried and the matching item is returned.
        """
        for org_type in ALLOWED_ORG_TYPES:
            data = await self._request(
                ORGANIZATIONS_PATH,
                {"organizationId": organization_id, "type": org_type, "limit": ORGANIZATIONS_LIMIT_MAX},
                "organization",
            )
            for item in data.get("items", []):
                if item.get("id") == organization_id:
                    return self._dump(item)

        raise ValueError(f"Organization {organization_id} not found")

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
        arguments = arguments or {}
        try:
            if tool_name == "get_current_organization":
                text = await self._get_current_organization()
            elif tool_name == "list_organizations":
                text = await self._get_organizations(
                    limit=arguments.get("limit", ORGANIZATIONS_LIMIT_DEFAULT),
                    anchor=arguments.get("anchor"),
                    organization_id=arguments.get("organization_id"),
                    org_type=arguments.get("type"),
                )
            elif tool_name == "get_organization":
                text = await self._get_organization(arguments["organization_id"])
            else:
                return None

            return {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }

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

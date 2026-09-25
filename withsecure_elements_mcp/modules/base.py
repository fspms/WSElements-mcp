"""
Base module for WithSecure Elements MCP modules.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from mcp.server import Server

from ..auth import WithSecureAuth
from ..config import WithSecureConfig


class BaseModule(ABC):
    """Base class for all MCP modules."""
    
    def __init__(self, server: Server, auth: WithSecureAuth, config: WithSecureConfig):
        self.server = server
        self.auth = auth
        self.config = config
        self._tools = []
        self._resources = []
        self._register_resources()
        self._register_tools()
    
    @abstractmethod
    def _register_resources(self) -> None:
        """Register module resources."""
        pass
    
    @abstractmethod
    def _register_tools(self) -> None:
        """Register module tools."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Module name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Module description."""
        pass
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get list of tools for HTTP transport."""
        return self._tools
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """Get list of resources for HTTP transport."""
        return self._resources
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        # This will be implemented by subclasses
        return None

    @staticmethod
    def _dump(data: Any) -> str:
        """Serialize API data as compact JSON (token-efficient)."""
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    def _org_id(self, organization_id: Optional[str] = None) -> Optional[str]:
        """Resolve the organization: explicit argument, else configured default."""
        return organization_id or self.config.organization_id

    async def _get_json(self, path: str, params: Dict[str, Any], what: str) -> Dict[str, Any]:
        """GET an API endpoint and return the decoded JSON body.

        ``None`` values in ``params`` are dropped; list values are sent as
        repeated query parameters (how the API expects multi-value filters).
        """
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        headers = await self.auth.get_headers()
        clean = {k: v for k, v in params.items() if v is not None}
        response = await self.auth._client.get(path, headers=headers, params=clean)
        if response.status_code != 200:
            raise Exception(f"Error retrieving {what}: {response.status_code} - {response.text}")
        return response.json()

    async def _send(
        self,
        method: str,
        path: str,
        what: str,
        ok: tuple = (200,),
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send a write request (POST/PATCH/PUT/DELETE) and return the JSON body.

        Returns an empty dict for bodiless success responses (e.g. 204).
        """
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        headers = await self.auth.get_headers()
        if body is not None:
            headers["Content-Type"] = "application/json"
        clean = {k: v for k, v in (params or {}).items() if v is not None}
        response = await self.auth._client.request(
            method, path, headers=headers, params=clean, json=body
        )
        if response.status_code not in ok:
            raise Exception(f"Error {what}: {response.status_code} - {response.text}")
        if not response.content:
            return {}
        return response.json()

    async def read_resource(self, uri: str) -> Optional[str]:
        """Read a resource by URI. Return None if this module does not handle it.

        Subclasses that expose resources override this. The central read_resource
        handler in the server dispatches to each module until one returns a value.
        """
        return None

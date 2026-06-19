"""
Base module for WithSecure Elements MCP modules.
"""

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

    async def read_resource(self, uri: str) -> Optional[str]:
        """Read a resource by URI. Return None if this module does not handle it.

        Subclasses that expose resources override this. The central read_resource
        handler in the server dispatches to each module until one returns a value.
        """
        return None

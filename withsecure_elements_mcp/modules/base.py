"""
Base module for WithSecure Elements MCP modules.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Resource, Tool

from ..auth import WithSecureAuth
from ..config import WithSecureConfig


class BaseModule(ABC):
    """Base class for all MCP modules."""
    
    def __init__(self, server: Server, auth: WithSecureAuth, config: WithSecureConfig):
        self.server = server
        self.auth = auth
        self.config = config
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

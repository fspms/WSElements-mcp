"""
Configuration for WithSecure Elements MCP Server.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field


class WithSecureConfig(BaseModel):
    """Configuration for WithSecure Elements API."""
    
    client_id: str = Field(..., description="WithSecure client ID")
    client_secret: str = Field(..., description="WithSecure client secret")
    base_url: str = Field(
        default="https://api.connect.withsecure.com",
        description="WithSecure API base URL"
    )
    organization_id: Optional[str] = Field(
        default=None,
        description="Organization ID (optional)"
    )
    user_agent: str = Field(
        default="WithSecure-Elements-MCP/0.1.0",
        description="User-Agent for API requests"
    )


class MCPConfig(BaseModel):
    """Configuration for MCP server."""
    
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")
    enabled_modules: List[str] = Field(
        default_factory=lambda: ["incidents", "events", "organizations", "devices"],
        description="Enabled modules"
    )


def load_config() -> tuple[WithSecureConfig, MCPConfig]:
    """Load configuration from environment variables."""
    
    # WithSecure configuration
    withsecure_config = WithSecureConfig(
        client_id=os.getenv("WITHSECURE_CLIENT_ID", ""),
        client_secret=os.getenv("WITHSECURE_CLIENT_SECRET", ""),
        base_url=os.getenv("WITHSECURE_BASE_URL", "https://api.connect.withsecure.com"),
        organization_id=os.getenv("WITHSECURE_ORGANIZATION_ID"),
        user_agent=os.getenv("WITHSECURE_USER_AGENT", "WithSecure-Elements-MCP/0.1.0")
    )
    
    # MCP configuration
    modules_str = os.getenv("WITHSECURE_MCP_MODULES", "incidents,events,organizations,devices")
    enabled_modules = [m.strip() for m in modules_str.split(",") if m.strip()]
    
    mcp_config = MCPConfig(
        debug=os.getenv("MCP_DEBUG", "false").lower() == "true",
        log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
        enabled_modules=enabled_modules
    )
    
    return withsecure_config, mcp_config

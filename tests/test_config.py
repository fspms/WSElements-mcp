"""
Tests for configuration.
"""

import os
import pytest
from withsecure_elements_mcp.config import load_config, WithSecureConfig, MCPConfig


def test_withsecure_config_defaults():
    """Test WithSecure configuration defaults."""
    config = WithSecureConfig(
        client_id="test_client",
        client_secret="test_secret"
    )
    
    assert config.client_id == "test_client"
    assert config.client_secret == "test_secret"
    assert config.base_url == "https://api.connect.withsecure.com"
    assert config.organization_id is None
    assert config.user_agent == "WithSecure-Elements-MCP/0.1.0"


def test_mcp_config_defaults():
    """Test MCP configuration defaults."""
    config = MCPConfig()
    
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.enabled_modules == ["incidents", "events", "organizations", "devices"]


def test_load_config_from_env():
    """Test loading configuration from environment variables."""
    # Save existing environment variables
    old_env = {}
    env_vars = [
        "WITHSECURE_CLIENT_ID",
        "WITHSECURE_CLIENT_SECRET", 
        "WITHSECURE_BASE_URL",
        "WITHSECURE_ORGANIZATION_ID",
        "MCP_DEBUG",
        "MCP_LOG_LEVEL",
        "WITHSECURE_MCP_MODULES"
    ]
    
    for var in env_vars:
        old_env[var] = os.environ.get(var)
    
    try:
        # Set test environment variables
        os.environ["WITHSECURE_CLIENT_ID"] = "test_client_id"
        os.environ["WITHSECURE_CLIENT_SECRET"] = "test_client_secret"
        os.environ["WITHSECURE_BASE_URL"] = "https://api.test.withsecure.com"
        os.environ["WITHSECURE_ORGANIZATION_ID"] = "test-org-id"
        os.environ["MCP_DEBUG"] = "true"
        os.environ["MCP_LOG_LEVEL"] = "DEBUG"
        os.environ["WITHSECURE_MCP_MODULES"] = "incidents,events"
        
        withsecure_config, mcp_config = load_config()
        
        assert withsecure_config.client_id == "test_client_id"
        assert withsecure_config.client_secret == "test_client_secret"
        assert withsecure_config.base_url == "https://api.test.withsecure.com"
        assert withsecure_config.organization_id == "test-org-id"
        
        assert mcp_config.debug is True
        assert mcp_config.log_level == "DEBUG"
        assert mcp_config.enabled_modules == ["incidents", "events"]
    
    finally:
        # Restore environment variables
        for var in env_vars:
            if old_env[var] is not None:
                os.environ[var] = old_env[var]
            elif var in os.environ:
                del os.environ[var]

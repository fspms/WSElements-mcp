"""
Tests for authentication.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from withsecure_elements_mcp.auth import WithSecureAuth, TokenResponse
from withsecure_elements_mcp.config import WithSecureConfig


@pytest.fixture
def config():
    """Test configuration."""
    return WithSecureConfig(
        client_id="test_client",
        client_secret="test_secret",
        base_url="https://api.test.withsecure.com"
    )


@pytest.fixture
def auth(config):
    """Test authenticator."""
    return WithSecureAuth(config)


@pytest.mark.asyncio
async def test_token_response():
    """Test token response validation."""
    token_data = {
        "access_token": "test_token",
        "token_type": "Bearer",
        "expires_in": 3600
    }
    
    token_response = TokenResponse.model_validate(token_data)
    
    assert token_response.access_token == "test_token"
    assert token_response.token_type == "Bearer"
    assert token_response.expires_in == 3600


@pytest.mark.asyncio
async def test_get_token_success(auth):
    """Test successful token retrieval."""
    mock_response = {
        "access_token": "test_token",
        "token_type": "Bearer", 
        "expires_in": 3600
    }
    
    mock_client = AsyncMock()
    mock_post_response = MagicMock(status_code=200)
    mock_post_response.json.return_value = mock_response
    mock_client.post.return_value = mock_post_response
    auth._client = mock_client

    token = await auth.get_token()

    assert token == "test_token"
    assert auth._token == "test_token"
    assert auth._token_expires_at is not None


@pytest.mark.asyncio
async def test_get_token_failure(auth):
    """Test token retrieval failure."""
    mock_client = AsyncMock()
    mock_post_response = MagicMock(status_code=401, text="Unauthorized")
    mock_client.post.return_value = mock_post_response
    auth._client = mock_client

    with pytest.raises(Exception, match="Authentication failed"):
        await auth.get_token()


@pytest.mark.asyncio
async def test_get_headers(auth):
    """Test authentication headers retrieval."""
    with patch.object(auth, 'get_token', return_value="test_token"):
        headers = await auth.get_headers()
        
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["User-Agent"] == auth.config.user_agent


@pytest.mark.asyncio
async def test_token_validity_check(auth):
    """Test token validity check."""
    import time
    
    # Valid token
    auth._token = "test_token"
    auth._token_expires_at = time.time() + 600  # 10 minutes in the future
    
    assert auth._is_token_valid() is True
    
    # Expired token
    auth._token_expires_at = time.time() - 600  # 10 minutes in the past
    
    assert auth._is_token_valid() is False
    
    # No token
    auth._token = None
    auth._token_expires_at = None
    
    assert auth._is_token_valid() is False

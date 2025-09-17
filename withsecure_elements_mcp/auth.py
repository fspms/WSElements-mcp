"""
OAuth2 authentication for WithSecure Elements API.
"""

import asyncio
import time
from typing import Optional
import httpx
from pydantic import BaseModel

from .config import WithSecureConfig


class TokenResponse(BaseModel):
    """OAuth2 authentication response."""
    
    access_token: str
    token_type: str
    expires_in: int


class WithSecureAuth:
    """Authentication manager for WithSecure Elements API."""
    
    def __init__(self, config: WithSecureConfig):
        self.config = config
        self._token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager to initialize HTTP client."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={"User-Agent": self.config.user_agent},
            timeout=30.0
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up HTTP client."""
        if self._client:
            await self._client.aclose()
    
    async def get_token(self) -> str:
        """
        Get a valid access token.
        
        Returns:
            str: Access token
        """
        if self._is_token_valid():
            return self._token
        
        await self._refresh_token()
        return self._token
    
    def _is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        if not self._token or not self._token_expires_at:
            return False
        
        # Renew token 5 minutes before expiration
        return time.time() < (self._token_expires_at - 300)
    
    async def _refresh_token(self) -> None:
        """Refresh access token."""
        if not self._client:
            raise RuntimeError("HTTP client not initialized")
        
        auth_data = {
            "grant_type": "client_credentials",
            "scope": "connect.api.read connect.api.write"
        }
        
        response = await self._client.post(
            "/as/token.oauth2",
            data=auth_data,
            auth=(self.config.client_id, self.config.client_secret)
        )
        
        if response.status_code != 200:
            raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
        
        token_data = TokenResponse.model_validate(response.json())
        
        self._token = token_data.access_token
        self._token_expires_at = time.time() + token_data.expires_in
    
    async def get_headers(self) -> dict[str, str]:
        """
        Get HTTP headers with authentication token.
        
        Returns:
            dict: HTTP headers with authorization
        """
        token = await self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "User-Agent": self.config.user_agent
        }

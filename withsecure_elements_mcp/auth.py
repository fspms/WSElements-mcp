"""
OAuth2 authentication for WithSecure Elements API.
"""

import asyncio
import logging
import time
from typing import Optional
import httpx
from pydantic import BaseModel

from .config import WithSecureConfig

logger = logging.getLogger("withsecure-elements-mcp")

# HTTP status codes that warrant a retry with backoff.
_RETRY_STATUS = {429, 500, 502, 503, 504}


class _RetryTransport(httpx.AsyncBaseTransport):
    """Transport wrapper that retries transient failures (429/5xx).

    Honors the ``Retry-After`` header when present, otherwise uses capped
    exponential backoff. Applied to every request made through the client.
    """

    def __init__(self, wrapped: httpx.AsyncBaseTransport, max_retries: int = 3):
        self._wrapped = wrapped
        self._max_retries = max_retries

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        attempt = 0
        while True:
            response = await self._wrapped.handle_async_request(request)
            if response.status_code in _RETRY_STATUS and attempt < self._max_retries:
                retry_after = response.headers.get("retry-after", "")
                if retry_after.isdigit():
                    delay = float(retry_after)
                else:
                    delay = min(2 ** attempt, 8)
                await response.aclose()
                logger.warning(
                    "WithSecure API returned %s; retrying in %.1fs (attempt %d/%d)",
                    response.status_code, delay, attempt + 1, self._max_retries,
                )
                await asyncio.sleep(delay)
                attempt += 1
                continue
            return response

    async def aclose(self) -> None:
        await self._wrapped.aclose()


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
        self._refresh_lock = asyncio.Lock()

    async def __aenter__(self):
        """Async context manager to initialize HTTP client."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={"User-Agent": self.config.user_agent},
            timeout=self.config.timeout,
            transport=_RetryTransport(httpx.AsyncHTTPTransport()),
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

        async with self._refresh_lock:
            # Re-check inside the lock: another coroutine may have refreshed it.
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
        
        # Determine scope based on configuration
        if self.config.api_scope == "read_only":
            scope = "connect.api.read"
        elif self.config.api_scope == "read_write":
            scope = "connect.api.read connect.api.write"
        else:
            raise ValueError(f"Invalid API scope: {self.config.api_scope}. Must be 'read_only' or 'read_write'")
        
        auth_data = {
            "grant_type": "client_credentials",
            "scope": scope
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

"""
HTTP transport usage example for WithSecure Elements MCP server.
"""

import asyncio
import os
from withsecure_elements_mcp.server import WithSecureElementsMCPServer


async def main():
    """HTTP transport usage example."""
    
    # Configuration via environment variables
    # Make sure you have defined:
    # - WITHSECURE_CLIENT_ID
    # - WITHSECURE_CLIENT_SECRET
    # - WITHSECURE_ORGANIZATION_ID (optional)
    
    # Create server
    server = WithSecureElementsMCPServer(
        debug=True,
        enabled_modules=["incidents", "events", "organizations", "devices"]
    )
    
    # Run with HTTP transport on localhost:8080
    print("Starting WithSecure Elements MCP server with HTTP transport...")
    print("Server will be accessible at http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    
    await server.run("streamable-http", host="0.0.0.0", port=8080)


if __name__ == "__main__":
    asyncio.run(main())

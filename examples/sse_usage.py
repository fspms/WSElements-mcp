"""
SSE transport usage example for WithSecure Elements MCP server.
"""

import asyncio
import os
from withsecure_elements_mcp.server import WithSecureElementsMCPServer


async def main():
    """SSE transport usage example."""
    
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
    
    # Run with SSE transport on localhost:8000
    print("Starting WithSecure Elements MCP server with SSE transport...")
    print("Server will be accessible at http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    await server.run("sse", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    asyncio.run(main())

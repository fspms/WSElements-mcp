"""
Basic usage example for WithSecure Elements MCP server.
"""

import asyncio
import os
from withsecure_elements_mcp.server import WithSecureElementsMCPServer


async def main():
    """Basic usage example."""
    
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
    
    # Run with stdio transport
    await server.run("stdio")


if __name__ == "__main__":
    asyncio.run(main())

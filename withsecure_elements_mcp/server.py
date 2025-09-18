"""
Main MCP server for WithSecure Elements.
"""

import asyncio
import logging
import sys
from typing import List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import load_config, WithSecureConfig, MCPConfig
from .auth import WithSecureAuth
from .modules import IncidentsModule, EventsModule, OrganizationsModule, DevicesModule, ResponseActionsModule


class WithSecureElementsMCPServer:
    """MCP server for WithSecure Elements."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        debug: bool = False,
        enabled_modules: Optional[List[str]] = None
    ):
        """Initialize MCP server."""
        self.withsecure_config, self.mcp_config = load_config()
        
        # Override with provided parameters
        if base_url:
            self.withsecure_config.base_url = base_url
        if debug is not None:
            self.mcp_config.debug = debug
        if enabled_modules:
            self.mcp_config.enabled_modules = enabled_modules
        
        # Logging configuration
        self._setup_logging()
        
        # MCP server initialization
        self.server = Server("withsecure-elements-mcp")
        self.auth = None
        self.modules = []
    
    def _setup_logging(self) -> None:
        """Configure logging system."""
        level = logging.DEBUG if self.mcp_config.debug else getattr(logging, self.mcp_config.log_level.upper())
        
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stderr)]
        )
        
        self.logger = logging.getLogger("withsecure-elements-mcp")
    
    async def _initialize_modules(self) -> None:
        """Initialize enabled modules."""
        if not self.auth:
            raise RuntimeError("Authentication not initialized")
        
        available_modules = {
            "incidents": IncidentsModule,
            "events": EventsModule,
            "organizations": OrganizationsModule,
            "devices": DevicesModule,
            "response_actions": ResponseActionsModule
        }
        
        for module_name in self.mcp_config.enabled_modules:
            if module_name in available_modules:
                module_class = available_modules[module_name]
                module = module_class(self.server, self.auth, self.withsecure_config)
                self.modules.append(module)
                self.logger.info(f"Module '{module_name}' initialized")
            else:
                self.logger.warning(f"Module '{module_name}' not recognized, ignored")
    
    async def run(self, transport: str = "stdio", host: str = "localhost", port: int = 8000) -> None:
        """Run MCP server."""
        try:
            # Configuration validation
            if not self.withsecure_config.client_id or not self.withsecure_config.client_secret:
                raise ValueError("WITHSECURE_CLIENT_ID and WITHSECURE_CLIENT_SECRET must be defined")
            
            self.logger.info("Initializing WithSecure Elements MCP server...")
            self.logger.info(f"Base URL: {self.withsecure_config.base_url}")
            self.logger.info(f"Enabled modules: {', '.join(self.mcp_config.enabled_modules)}")
            
            # Authentication initialization
            async with WithSecureAuth(self.withsecure_config) as auth:
                self.auth = auth
                
                # Test authentication
                try:
                    await auth.get_token()
                    self.logger.info("Authentication successful")
                except Exception as e:
                    self.logger.error(f"Authentication failed: {e}")
                    raise
                
                # Initialize modules
                await self._initialize_modules()
                
                # Transport configuration
                if transport == "stdio":
                    self.logger.info("Starting server with stdio transport")
                    async with stdio_server() as (read_stream, write_stream):
                        await self.server.run(
                            read_stream,
                            write_stream,
                            self.server.create_initialization_options()
                        )
                
                elif transport == "sse":
                    self.logger.info(f"Starting server with SSE transport on {host}:{port}")
                    from mcp.server.sse import sse_server
                    async with sse_server(host, port) as server:
                        await server.serve_forever()
                
                elif transport == "streamable-http":
                    self.logger.info(f"Starting server with HTTP transport on {host}:{port}")
                    # Create a proper MCP HTTP server
                    from aiohttp import web
                    import json
                    
                    async def handle_mcp_request(request):
                        """Handle MCP requests via HTTP."""
                        try:
                            data = await request.json()
                            method = data.get('method', '')
                            request_id = data.get('id')
                            
                            self.logger.info(f"Received MCP request: {method}")
                            
                            # Handle different MCP methods
                            if method == "initialize":
                                return web.json_response({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": {
                                        "protocolVersion": "2024-11-05",
                                        "capabilities": {
                                            "tools": {
                                                "listChanged": True
                                            },
                                            "resources": {
                                                "subscribe": True,
                                                "listChanged": True
                                            },
                                            "prompts": {
                                                "listChanged": True
                                            },
                                            "logging": {}
                                        },
                                        "serverInfo": {
                                            "name": "withsecure-elements-mcp",
                                            "version": "0.1.0"
                                        }
                                    }
                                })
                            
                            elif method == "tools/list":
                                # Collect all tools from modules
                                tools = []
                                for module in self.modules:
                                    if hasattr(module, 'get_tools'):
                                        tools.extend(module.get_tools())
                                
                                return web.json_response({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": {
                                        "tools": tools
                                    }
                                })
                            
                            elif method == "tools/call":
                                tool_name = data.get('params', {}).get('name', '')
                                arguments = data.get('params', {}).get('arguments', {})
                                
                                # Find and call the tool
                                for module in self.modules:
                                    if hasattr(module, 'call_tool'):
                                        result = await module.call_tool(tool_name, arguments)
                                        if result is not None:
                                            return web.json_response({
                                                "jsonrpc": "2.0",
                                                "id": request_id,
                                                "result": result
                                            })
                                
                                return web.json_response({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "error": {
                                        "code": -32601,
                                        "message": f"Tool '{tool_name}' not found"
                                    }
                                })
                            
                            elif method == "resources/list":
                                # Collect all resources from modules
                                resources = []
                                for module in self.modules:
                                    if hasattr(module, 'get_resources'):
                                        resources.extend(module.get_resources())
                                
                                return web.json_response({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": {
                                        "resources": resources
                                    }
                                })
                            
                            elif method == "notifications/initialized":
                                # Acknowledge initialization
                                return web.json_response({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": {}
                                })
                            
                            else:
                                return web.json_response({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "error": {
                                        "code": -32601,
                                        "message": f"Method '{method}' not found"
                                    }
                                })
                                
                        except Exception as e:
                            self.logger.error(f"Error handling MCP request: {e}")
                            return web.json_response({
                                "jsonrpc": "2.0",
                                "id": data.get("id") if 'data' in locals() else None,
                                "error": {
                                    "code": -32603,
                                    "message": str(e)
                                }
                            }, status=500)
                    
                    # Create HTTP app
                    app = web.Application()
                    app.router.add_post("/", handle_mcp_request)
                    app.router.add_get("/health", lambda r: web.json_response({"status": "ok"}))
                    
                    # Add CORS headers for n8n compatibility
                    @web.middleware
                    async def cors_handler(request, handler):
                        response = await handler(request)
                        response.headers['Access-Control-Allow-Origin'] = '*'
                        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                        return response
                    
                    app.middlewares.append(cors_handler)
                    
                    # Handle OPTIONS requests for CORS
                    async def options_handler(request):
                        return web.Response(
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    
                    app.router.add_options("/", options_handler)
                    
                    # Start server
                    runner = web.AppRunner(app)
                    await runner.setup()
                    site = web.TCPSite(runner, host, port)
                    await site.start()
                    
                    self.logger.info(f"Server running on http://{host}:{port}")
                    
                    # Keep server running
                    try:
                        while True:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        pass
                    finally:
                        await runner.cleanup()
                
                else:
                    raise ValueError(f"Unsupported transport: {transport}")
        
        except Exception as e:
            self.logger.error(f"Error running server: {e}")
            raise


def main() -> None:
    """Main server entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="WithSecure Elements MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport type to use"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="IP address for HTTP transports (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transports (default: 8000)"
    )
    parser.add_argument(
        "--modules",
        help="Modules to enable (comma-separated)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--base-url",
        help="WithSecure Elements API base URL"
    )
    
    args = parser.parse_args()
    
    # Parse modules
    enabled_modules = None
    if args.modules:
        enabled_modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    
    # Create and run server
    server = WithSecureElementsMCPServer(
        base_url=args.base_url,
        debug=args.debug,
        enabled_modules=enabled_modules
    )
    
    try:
        asyncio.run(server.run(args.transport, args.host, args.port))
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

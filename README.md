# WithSecure Elements MCP Server

An MCP (Model Context Protocol) server to connect AI agents to WithSecure Elements for automated security analysis and threat hunting.

## Features

- **Incidents (BCDs)** : Access and manage Broad Context Detections (BCDs)
- **Security Events** : Retrieve and analyze security events
- **Organizations** : Manage organization information
- **Devices** : Monitor and perform actions on devices
- **Response Actions** : Execute security response actions on devices
- **OAuth2 Authentication** : Secure integration with WithSecure Elements API

## Prerequisites

- Python 3.10 or higher
- WithSecure Elements API credentials (Client ID, Client Secret)
- Organization ID (optional, can be retrieved via API)
- Docker (for containerized deployment)

## Installation

### Using Docker (Recommended)

The easiest way to run the WithSecure Elements MCP Server is using Docker:

```bash
# Pull the latest image
docker pull ghcr.io/fspms/wselements-mcp:latest

# Run with environment variables
docker run --rm \
  -e WITHSECURE_CLIENT_ID=your_client_id \
  -e WITHSECURE_CLIENT_SECRET=your_client_secret \
  -e WITHSECURE_BASE_URL=https://api.connect.withsecure.com \
  -e WITHSECURE_ORGANIZATION_ID=your_organization_id \
  -p 8000:8000 \
  ghcr.io/fspms/wselements-mcp:latest \
  --transport streamable-http --host 0.0.0.0 --port 8000
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  withsecure-elements-mcp:
    image: ghcr.io/fspms/wselements-mcp:latest
    container_name: withsecure-elements-mcp
    ports:
      - "8000:8000"
    environment:
      - WITHSECURE_CLIENT_ID=your_client_id
      - WITHSECURE_CLIENT_SECRET=your_client_secret
      - WITHSECURE_BASE_URL=https://api.connect.withsecure.com
      - WITHSECURE_ORGANIZATION_ID=your_organization_id
      - MCP_DEBUG=false
      - MCP_LOG_LEVEL=INFO
      - WITHSECURE_MCP_MODULES=incidents,events,organizations,devices,response_actions
    command: ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Then run:

```bash
docker-compose up -d
```

### Install using uv

```bash
uv tool install withsecure-elements-mcp
```

### Install using pip

```bash
pip install withsecure-elements-mcp
```

## Configuration

### Environment Variables

Create a `.env` file with the following information:

```env
# WithSecure Elements API Configuration
WITHSECURE_CLIENT_ID=your_client_id
WITHSECURE_CLIENT_SECRET=your_client_secret
WITHSECURE_BASE_URL=https://api.connect.withsecure.com
WITHSECURE_ORGANIZATION_ID=your_organization_id
WITHSECURE_API_SCOPE=read_write

# MCP Server Configuration
MCP_DEBUG=false
MCP_LOG_LEVEL=INFO
WITHSECURE_MCP_MODULES=incidents,events,organizations,devices,response_actions
```

### Available Environments

- **Production** : `https://api.connect.withsecure.com`
- **Staging** : `https://api.connect-stg.fsapi.com`
- **CI** : `https://api.connect-ci.fsapi.com`

### API Scope Configuration

The `WITHSECURE_API_SCOPE` environment variable controls the level of access to the WithSecure Elements API:

- **`read_only`** : Read-only access only (scope: `connect.api.read`)
  - Use this option if your WithSecure client is configured for read-only access
  - Allows data retrieval but not modification
  - Resolves the "Scope not allowed for the client" error for read-only clients

- **`read_write`** : Full read and write access (scopes: `connect.api.read connect.api.write`)
  - Use this option if your WithSecure client has full access
  - Allows all read and write operations
  - Default option

**Example configuration for a read-only client:**
```env
WITHSECURE_API_SCOPE=read_only
```

### Module Configuration

The server supports 5 main modules that can be enabled/disabled:

- **`incidents`** : Broad Context Detections (BCDs) management
- **`events`** : Security events analysis and monitoring
- **`organizations`** : Organization information and settings
- **`devices`** : Device monitoring and management
- **`response_actions`** : Security response actions execution

## Usage

### Command Line

Run the server with default settings (stdio transport):

```bash
withsecure-elements-mcp
```

Run with SSE transport:

```bash
withsecure-elements-mcp --transport sse
```

Run with streamable-http transport:

```bash
withsecure-elements-mcp --transport streamable-http
```

Run with streamable-http transport on custom port:

```bash
withsecure-elements-mcp --transport streamable-http --host 0.0.0.0 --port 8080
```

### Module Configuration

The WithSecure Elements MCP Server supports multiple ways to specify which modules to enable:

#### 1. Command Line Arguments (highest priority)

```bash
# Enable specific modules
withsecure-elements-mcp --modules incidents,events,organizations,devices,response_actions

# Enable only one module
withsecure-elements-mcp --modules incidents
```

#### 2. Environment Variable (fallback)

```bash
# Export environment variable
export WITHSECURE_MCP_MODULES=incidents,events,organizations,devices,response_actions
withsecure-elements-mcp
```

#### 3. Default Behavior (all modules)

If no modules are specified, all available modules are enabled by default.

### As a Library

```python
from withsecure_elements_mcp.server import WithSecureElementsMCPServer

# Create and run the server
server = WithSecureElementsMCPServer(
    base_url="https://api.connect.withsecure.com",
    debug=True,
    enabled_modules=["incidents", "events", "organizations", "devices", "response_actions"]
)

# Run with stdio transport (default)
server.run()

# Or run with SSE transport
server.run("sse")

# Or run with streamable-http transport
server.run("streamable-http", host="0.0.0.0", port=8080)
```

## Editor/Assistant Integration

### MCP Configuration

#### Using Docker

```json
{
  "mcpServers": {
    "withsecure-elements-mcp": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-p",
        "8000:8000",
        "-e",
        "WITHSECURE_CLIENT_ID=your_client_id",
        "-e",
        "WITHSECURE_CLIENT_SECRET=your_client_secret",
        "-e",
        "WITHSECURE_BASE_URL=https://api.connect.withsecure.com",
        "-e",
        "WITHSECURE_ORGANIZATION_ID=your_organization_id",
        "-e",
        "MCP_DEBUG=false",
        "-e",
        "MCP_LOG_LEVEL=INFO",
        "-e",
        "WITHSECURE_MCP_MODULES=incidents,events,organizations,devices,response_actions",
        "ghcr.io/fspms/wselements-mcp:latest",
        "--transport",
        "streamable-http",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ]
    }
  }
}
```

#### Using HTTP Transport (when server is already running)

```json
{
  "mcpServers": {
    "withsecure-elements-mcp": {
      "url": "http://localhost:8000",
      "transport": "http"
    }
  }
}
```

#### Using uvx (for local development)

```json
{
  "mcpServers": {
    "withsecure-elements-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "/path/to/.env",
        "withsecure-elements-mcp"
      ]
    }
  }
}
```

### With Module Selection

```json
{
  "mcpServers": {
    "withsecure-elements-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "/path/to/.env",
        "withsecure-elements-mcp",
        "--modules",
        "incidents,events,response_actions"
      ]
    }
  }
}
```

## Available Modules

### Incidents (BCDs)
- List incidents
- Retrieve incident details
- Archive/unarchive incidents
- Update incident status

### Security Events
- List security events
- Retrieve event details
- Filter events by criteria

### Organizations
- Retrieve organization information
- List accessible organizations

### Devices
- List devices
- Retrieve device details
- Perform actions on devices

### Response Actions
- List response actions responses
- Create response actions on devices
- Execute security actions including:
  - **Process Management**: Kill threads, kill processes, collect process memory
  - **Memory Analysis**: Full memory dumps, process memory collection
  - **File Operations**: Collect files, delete files, quarantine/unquarantine files
  - **System Control**: Run commands, restart/shutdown devices
  - **Network Isolation**: Isolate devices from network, release from isolation
  - **Agent Management**: Restart security agents

## Examples

The project includes several usage examples in the `examples/` directory:

- **`basic_usage.py`** : Basic server setup and configuration
- **`sse_usage.py`** : Server-Sent Events transport example
- **`streamable_http_usage.py`** : HTTP transport example

### Quick Start Example

```python
import asyncio
from withsecure_elements_mcp.server import WithSecureElementsMCPServer

async def main():
    # Create server with all modules enabled
    server = WithSecureElementsMCPServer(
        debug=True,
        enabled_modules=["incidents", "events", "organizations", "devices", "response_actions"]
    )
    
    # Run with stdio transport
    await server.run("stdio")

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

### Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/withsecure/elements-mcp.git
cd elements-mcp

# Create virtual environment and install dependencies
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or use the provided startup scripts
# On Windows:
.\scripts\start.ps1

# On Linux/macOS:
./scripts/start.sh
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with detailed output
pytest -v -s
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Considerations

- **API Credentials** : Store your WithSecure API credentials securely using environment variables or secret management systems
- **Network Security** : Use HTTPS in production environments
- **Access Control** : Limit access to the MCP server to authorized users only
- **Logging** : Monitor and audit all API calls and response actions
- **Response Actions** : Use response actions carefully as they can affect system operations

## Troubleshooting

### Common Issues

1. **Authentication Errors** : Verify your API credentials and organization ID
2. **Module Not Found** : Ensure the module is included in `WITHSECURE_MCP_MODULES`
3. **Connection Issues** : Check network connectivity and API endpoint URLs
4. **Permission Errors** : Verify your API credentials have the necessary permissions

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Environment variable
export MCP_DEBUG=true

# Command line
withsecure-elements-mcp --debug
```

## Support

This is a community-driven open source project. For more information, see our SUPPORT file.

## About

Connect AI agents to WithSecure Elements for automated security analysis and threat hunting.
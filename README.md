# MCP server for WithSecure Elements

An MCP (Model Context Protocol) server to connect AI agents to WithSecure Elements for automated security analysis and threat hunting.

## Features

- **Incidents (BCDs)** : Access and manage Broad Context Detections (BCDs)
- **Security Events** : Retrieve and analyze security events
- **Organizations** : Manage organization information
- **Devices** : Monitor and perform actions on devices
- **Response Actions** : Execute security response actions on devices
- **Software Updates** : Install software updates and manage missing updates on devices
- **OAuth2 Authentication** : Secure integration with WithSecure Elements API (lazy, non-blocking startup)
- **Safe by default** : `read_only` scope by default; destructive tools flagged with the MCP `destructiveHint`
- **Resilient & efficient** : automatic retry/backoff on `429`/`5xx` (honoring `Retry-After`), compact JSON responses, and cursor pagination via `anchor`

## Prerequisites

- Python 3.10 or higher
- WithSecure Elements API credentials (Client ID, Client Secret)
- Organization ID (optional, can be retrieved via API)
- Docker (for containerized deployment)

## Installation

### Using Docker (Recommended)

The easiest way to run the WithSecure Elements MCP Server is using Docker:

```bash
# Pull the image (pin a version for reproducibility, e.g. :0.1.2)
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
      - WITHSECURE_MCP_MODULES=incidents,events,organizations,devices,response_actions,software_updates
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
WITHSECURE_API_SCOPE=read_only
WITHSECURE_TIMEOUT=30

# MCP Server Configuration
MCP_DEBUG=false
MCP_LOG_LEVEL=INFO
WITHSECURE_MCP_MODULES=incidents,events,organizations,devices,response_actions,software_updates
```

| Variable | Description | Default |
|----------|-------------|---------|
| `WITHSECURE_CLIENT_ID` / `WITHSECURE_CLIENT_SECRET` | API credentials (required) | — |
| `WITHSECURE_ORGANIZATION_ID` | Default organization (optional) | — |
| `WITHSECURE_API_SCOPE` | `read_only` or `read_write` | `read_only` |
| `WITHSECURE_TIMEOUT` | HTTP request timeout (seconds) | `30` |
| `WITHSECURE_BASE_URL` | API endpoint | production |
| `WITHSECURE_MCP_MODULES` | Enabled modules (CSV) | all six |

### Available Environments

- **Production** : `https://api.connect.withsecure.com`
- **Staging** : `https://api.connect-stg.fsapi.com`
- **CI** : `https://api.connect-ci.fsapi.com`

### API Scope Configuration

The `WITHSECURE_API_SCOPE` environment variable controls the level of access to the WithSecure Elements API:

- **`read_only`** : Read-only access only (scope: `connect.api.read`) — **default**
  - Allows data retrieval but not modification (least privilege)
  - Resolves the "Scope not allowed for the client" error for read-only clients

- **`read_write`** : Full read and write access (scopes: `connect.api.read connect.api.write`)
  - Required for write/response actions (isolate, scan, restart, install updates, response actions)
  - Use only if your WithSecure client has full access

**Example configuration for a read-only client:**
```env
WITHSECURE_API_SCOPE=read_only
```

### Module Configuration

The server supports 6 main modules that can be enabled/disabled:

- **`incidents`** : Broad Context Detections (BCDs) management
- **`events`** : Security events analysis and monitoring
- **`organizations`** : Organization information and settings
- **`devices`** : Device monitoring and management
- **`response_actions`** : Security response actions execution
- **`software_updates`** : Software updates installation, management, and scanning

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
export WITHSECURE_MCP_MODULES=incidents,events,organizations,devices,response_actions,software_updates
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
    enabled_modules=["incidents", "events", "organizations", "devices", "response_actions", "software_updates"]
)

# Run with stdio transport (default)
server.run()

# Or run with SSE transport
server.run("sse")

# Or run with streamable-http transport
server.run("streamable-http", host="0.0.0.0", port=8080)
```

## Editor/Assistant Integration

### Using with Claude

The package is published on PyPI, so `uvx` fetches it automatically — no clone needed.

**Claude Desktop** — edit the config file
(`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS,
`%APPDATA%\Claude\claude_desktop_config.json` on Windows), then restart Claude:

```json
{
  "mcpServers": {
    "withsecure-elements": {
      "command": "uvx",
      "args": ["withsecure-elements-mcp"],
      "env": {
        "WITHSECURE_CLIENT_ID": "your_client_id",
        "WITHSECURE_CLIENT_SECRET": "your_client_secret",
        "WITHSECURE_ORGANIZATION_ID": "your_organization_id",
        "WITHSECURE_API_SCOPE": "read_only"
      }
    }
  }
}
```

**Claude Code** — one command (user scope makes it available in every project):

```bash
claude mcp add withsecure-elements -s user \
  --env WITHSECURE_CLIENT_ID=your_client_id \
  --env WITHSECURE_CLIENT_SECRET=your_client_secret \
  --env WITHSECURE_ORGANIZATION_ID=your_organization_id \
  --env WITHSECURE_API_SCOPE=read_only \
  -- uvx withsecure-elements-mcp
```

Then ask Claude in natural language, e.g. *"List my WithSecure organizations"*,
*"Show the latest incidents"*, *"Which devices are offline?"*. Keep
`read_only` unless you need write/response actions; destructive tools require
`read_write` and Claude will ask for confirmation before running them.

> Authentication is lazy: the server starts even if credentials are wrong or the
> API is temporarily unreachable, so the tools always appear and you get a clear
> error on the first call rather than a silent connection failure.

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
        "WITHSECURE_MCP_MODULES=incidents,events,organizations,devices,response_actions,software_updates",
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
- `list_incidents` — list incidents (filters: severity, status, time range, pagination)
- `get_incident` — retrieve a specific incident
- `update_incident_status` — update status (`resolution` required when closing)
- `add_incident_comment` — add a comment to one or more incidents
- `list_incident_detections` — list detections for an incident

### Security Events
- `list_events` — list security events (filter by engine, engine group, severity, device, time range)
- `get_event` — retrieve event details
- `get_event_types` — list allowed engines/severities and other filter values
- `get_event_statistics` — aggregated event statistics

### Organizations
- `get_current_organization` — current authenticated organization (whoami)
- `list_organizations` — list accessible organizations
- `get_organization` — retrieve a specific organization

### Devices
- `list_devices` — list devices (filters + pagination)
- `get_device` — retrieve a specific device
- `get_device_statistics` / `get_device_histogram` — aggregated device data
- `get_device_operations` / `get_device_operation_status` — track remote operations
- `show_message` / `assign_profile` — non-destructive device operations
- `isolate_device` / `unisolate_device` / `scan_device` — network isolation and malware scan ⚠️
- **`send_full_status`** — request complete status from devices (1-5 per operation)
- **`restart_system`** — restart devices, Windows only, optional message (1-5 per operation) ⚠️

### Response Actions
- `list_response_actions_responses` — list response action responses
- `create_response_action` — create a response action on devices. The action performed is
  controlled by `action_type` and the WithSecure Elements API supports a wide catalog
  (process/thread termination, memory dumps, file collection/deletion, network isolation,
  registry/services operations, etc.) ⚠️

> ⚠️ Tools marked above perform write/disruptive operations. They require
> `WITHSECURE_API_SCOPE=read_write` and are flagged with the MCP `destructiveHint`,
> so MCP clients (e.g. Claude) will ask for confirmation before running them.

### Software Updates
- **Install software updates**: Install specific updates or updates by severity on devices
  - Install specific bulletin IDs
  - Install updates by severity (critical, important, everything)
  - Force close applications during upgrade
- **Get missing updates**: Retrieve list of missing software updates for a device
  - Filter by severity (critical, important, moderate, low, unclassified)
  - Filter by category (security, nonSecurity, servicePack, securityTool, none)
  - Limit results (1-200)
- **Scan for updates**: Trigger manual scan for software updates on devices
  - Force devices to check for available updates
  - Supports 1-5 devices per operation

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
        enabled_modules=["incidents", "events", "organizations", "devices", "response_actions", "software_updates"]
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
git clone https://github.com/fspms/WSElements-mcp.git
cd WSElements-mcp

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

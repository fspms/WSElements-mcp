# WithSecure Elements MCP Server

An MCP (Model Context Protocol) server to connect AI agents to WithSecure Elements for automated security analysis and threat hunting.

## Features

- **Incidents (BCDs)** : Access and manage Broad Context Detections (BCDs)
- **Security Events** : Retrieve and analyze security events
- **Organizations** : Manage organization information
- **Devices** : Monitor and perform actions on devices
- **OAuth2 Authentication** : Secure integration with WithSecure Elements API

## Installation

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

# MCP Server Configuration
MCP_DEBUG=false
MCP_LOG_LEVEL=INFO
WITHSECURE_MCP_MODULES=incidents,events,organizations,devices
```

### Available Environments

- **Production** : `https://api.connect.withsecure.com`
- **Staging** : `https://api.connect-stg.fsapi.com`
- **CI** : `https://api.connect-ci.fsapi.com`

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
withsecure-elements-mcp --modules incidents,events,organizations,devices

# Enable only one module
withsecure-elements-mcp --modules incidents
```

#### 2. Environment Variable (fallback)

```bash
# Export environment variable
export WITHSECURE_MCP_MODULES=incidents,events,organizations,devices
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
    enabled_modules=["incidents", "events", "organizations", "devices"]
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
        "incidents,events"
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

## Support

This is a community-driven open source project. For more information, see our SUPPORT file.

## About

Connect AI agents to WithSecure Elements for automated security analysis and threat hunting.
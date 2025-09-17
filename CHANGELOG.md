# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-19

### Added
- MCP server for WithSecure Elements
- OAuth2 authentication with WithSecure Elements API
- Incidents management module (BCDs)
  - List incidents
  - Retrieve incident details
  - Update incident status
  - Archive/unarchive incidents
- Security events management module
  - List security events
  - Retrieve event details
  - Get event types
  - Retrieve event statistics
- Organizations management module
  - Retrieve current organization information
  - List accessible organizations
  - Retrieve organization details
  - Get organization settings and statistics
- Devices management module
  - List devices
  - Retrieve device details
  - Get device events
  - Retrieve device statistics
  - Isolate/unisolate devices
  - Launch scans on devices
- Multiple transport support (stdio, SSE, HTTP)
- Flexible module configuration
- Complete documentation
- Usage examples
- Unit tests
- Docker support
- Startup scripts (Bash and PowerShell)
- MCP configuration for editor integration

### Technical
- Modular architecture based on CrowdStrike Falcon MCP model
- Robust error handling
- Configurable logging
- Complete type hints
- Tests with pytest
- Automatic formatting with black and isort
- Linting with ruff and mypy

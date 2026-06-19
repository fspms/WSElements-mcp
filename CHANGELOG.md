# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-06-19

### Fixed
- **Multi-module support on stdio transport.** Each module registered its own
  `@server.list_tools()`/`call_tool()`/resource handlers on the shared MCP
  `Server`; since the low-level server keeps a single handler per request type,
  only the last module was exposed. Tool/resource handlers are now registered
  centrally in `server.py` and aggregate every enabled module, so all tools are
  available on every transport.
- `NameError` in `devices` `send_full_status` / `restart_system` (missing
  module-level `json` import).
- Duplicate `DevicesModule._get_device_statistics` definition (the second
  shadowed the first).
- `IndexError` in `get_missing_updates` when a device has no missing updates.
- SSE transport crashed on startup (`mcp.server.sse.sse_server` does not exist);
  now implemented with `SseServerTransport` over Starlette/uvicorn.
- Concurrent token refreshes could race; `get_token` now uses an `asyncio.Lock`.

### Changed (API conformance with the WithSecure Elements OpenAPI spec)
- Incident status update now uses `PATCH /incidents/v1/incidents` with
  `{targets, status, resolution}` (resolution required when closing) instead of
  the non-existent `PUT /incidents/v1/incidents/{id}/status`.
- Removed `archive_incident` / `unarchive_incident` tools (no such endpoints).
- Removed `get_organization_settings` / `get_organization_statistics` (no such
  endpoints); `get_organization` now queries `GET /organizations/v1/organizations?organizationId=`.
- `get_device` uses `GET /devices/v1/devices?deviceId=`; device events use the
  `security-events` endpoint; isolate/unisolate/scan and operation-status now go
  through `POST`/`GET /devices/v1/operations` with the documented operation names.
- Added `starlette` and `uvicorn` runtime dependencies (SSE transport).

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

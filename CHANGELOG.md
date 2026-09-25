# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-25

### Added
- `list_incident_detections`: `fetch_all` to retrieve every detection of a BCD in one
  call (bounded by `max_items`), created-time filters and `include_activity_context`.
- `get_incident_updates` tool (`GET /incidents/v1/updates`).
- `list_incidents`: `resolution`, `risk_level`, `source`, `order`, `updated_*`,
  `exclusive_start` filters; multi-value filters accepted as arrays.
- HTTP transport: `ping` and `resources/read` methods.
- Optional HTTP access token: `MCP_AUTH_TOKEN` makes HTTP transports (streamable-http and
  SSE) require `Authorization: Bearer <token>`; unset keeps the previous open behavior.
- Optional official MCP SDK streamable-HTTP transport on `/mcp` with `MCP_HTTP_MODE=sdk`
  (stateless); the legacy JSON-RPC endpoint on `/` is always kept.
- Devices: `update_devices` (state/subscription/alias/importance/business context/labels)
  and `delete_devices` — flagged destructive.
- `get_response_action_tasks` (`GET /response-actions/v1/responses/tasks`) and
  `get_software_update_installations` (`GET /software-updates/v1/installations`).
- New `management` module: `list_audit_logs`, `list_invitations`, `create_invitation`,
  `delete_invitations`, `renew_invitations` (write tools flagged destructive),
  `list_profiles`, `list_exposure_identities`. Enabled by default; deployments that set
  `WITHSECURE_MCP_MODULES` explicitly must add `management` to get it.

### Changed
- `create_response_action` now uses the non-deprecated
  `POST /response-actions/v1/execute/{action}` endpoint with the real action catalog.
- `get_incident` returns the incident object instead of a one-item list.
- Breaking tool-schema changes (aligned with the API): `list_incidents` `status` is now
  an array (`severity` kept as a deprecated alias of `risk_level`); `scan_device` no
  longer takes `scan_type`; `list_devices` drops `status`/`last_seen_*` (use `state`);
  `get_device_operations` drops `limit`/`anchor`; `isolate_device` `reason` is optional.
- Removed the dead per-module MCP handler registrations (~40% less code).
- The streamable-http transport now runs on Starlette/uvicorn (like SSE) instead of
  aiohttp; same endpoints and responses. `aiohttp` is no longer a dependency.

### Fixed
- All modules checked against the official API reference: wrong parameter names
  (e.g. `severity` → `riskLevel` for incidents, `deviceName` → `name` for devices),
  invented enum values, and page sizes above the API maximum (400 errors).
- Module errors are now reported with `isError: true` on every transport.
- 5xx responses to non-idempotent requests (device operations, response actions) are
  no longer retried, which could run an action twice; `Retry-After` is capped at 30s.
- Missing `Content-Type` on POST device operations; per-target failures of a 207
  multi-status response are surfaced as errors.
- HTTP transport: notifications get `202` with no body; capabilities no longer
  advertise unsupported features.

## [0.1.2] - 2026-06-19

### Added
- Retry with backoff on transient API errors (429/5xx), honoring `Retry-After`.
- MCP tool annotations: read tools flagged `readOnlyHint`; `isolate_device`,
  `restart_system`, `scan_device`, `install_software_updates` and
  `create_response_action` flagged `destructiveHint` so clients can confirm.
- `anchor` pagination parameter exposed in the schema of all list tools.
- Configurable HTTP timeout via `WITHSECURE_TIMEOUT` (default 30s).
- PyPI publishing on tag via Trusted Publishing (`pypi-publish` job).

### Changed
- **Default API scope is now `read_only`** (was `read_write`) — least privilege.
  Set `WITHSECURE_API_SCOPE=read_write` to enable write/response actions.
- Authentication is no longer blocking at startup: the server starts even if the
  initial token probe fails and authenticates lazily on the first tool call, so
  clients can always list tools and get a clear error.
- API responses are serialized as compact JSON (no indentation) to cut token use.

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

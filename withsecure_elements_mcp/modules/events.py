"""
MCP module for WithSecure Elements security events management.

All queries use ``POST /security-events/v1/security-events`` (form-urlencoded
body, ``Accept: application/json`` or ``application/vnd.withsecure.aggr+json``
for aggregations). The deprecated GET variant is not used.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from .base import BaseModule


# ===== ALLOWED VALUES (from the official Elements API OpenAPI spec) =====

SECURITY_EVENTS_PATH = "/security-events/v1/security-events"

# Request enum of the `engine` filter (queryEvents requestBody).
ALLOWED_ENGINES: List[str] = [
    "AMSI",
    "activityMonitor",
    "activityMonitorClientProtection",
    "applicationControl",
    "browsingProtection",
    "cloudIdentityAzure",
    "cloudWorkloadAzure",
    "connectionControl",
    "connector",
    "dataGuard",
    "deepGuard",
    "deviceControl",
    "edr",
    "emailBreach",
    "emailScan",
    "fileScanning",
    "firewall",
    "inboxRuleScan",
    "integrityChecker",
    "oneDriveScan",
    "product",
    "realtimeScanning",
    "reputationBasedBrowsing",
    "setting",
    "sharePointScan",
    "systemEventsLog",
    "tamperProtection",
    "teamsScan",
    "webContentControl",
    "webTrafficScanning",
    "xFence",
    "xmRecommendation",
]

# epp: Endpoint Protection, edr: Detection and Response,
# ecp: Collaboration Protection, xm: Exposure Management
ALLOWED_ENGINE_GROUPS: List[str] = ["epp", "edr", "ecp", "xm"]

ALLOWED_SEVERITIES: List[str] = ["critical", "warning", "info"]

# Aggregation property (`count`), used with Accept: application/vnd.withsecure.aggr+json
ALLOWED_COUNT_VALUES: List[str] = [
    "engine",
    "url",
    "alertType",
    "deviceId",
    "infectionName",
    "categories",
    "appliedRule",
    "filePath",
    "description",
]

ALLOWED_ORDER_VALUES: List[str] = ["asc", "desc"]

# Language of `message` and `description` fields (default: en)
ALLOWED_LANGUAGES: List[str] = [
    "en", "de", "es-MX", "fi", "fr", "it", "ja", "pl", "pt-BR", "sv", "zh-TW",
]

# Values of the event `action` response field (informational, not a filter).
KNOWN_ACTIONS: List[str] = [
    "none",
    "allow",
    "blocked",
    "disinfected",
    "quarantined",
    "renamed",
    "deleted",
    "trashed",
    "reported",
    "reportedToUser",
    "unspecified",
    "merged",
    "closed",
    "created",
]

# Limits
SECURITY_EVENTS_LIMIT_MIN = 1
SECURITY_EVENTS_LIMIT_MAX = 200
SECURITY_EVENTS_LIMIT_DEFAULT = 100
# The API rejects ranges wider than 30 days.
MAX_RANGE_DAYS = 30
DEFAULT_RANGE = timedelta(days=1)
# get_event has no id filter in the API: pages are scanned up to this bound.
GET_EVENT_MAX_PAGES = 10



def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _enum_array(values: List[str], description: str) -> Dict[str, Any]:
    return {
        "type": "array",
        "items": {"type": "string", "enum": values},
        "description": description,
    }


class EventFilters(BaseModel):
    """Filters for event search."""

    organization_id: Optional[str] = None
    created_timestamp_start: Optional[str] = None
    created_timestamp_end: Optional[str] = None
    device_id: Optional[str] = None
    # Accept single or multiple engines/severities/engine groups
    event_type: Optional[Union[str, List[str]]] = None
    engine_group: Optional[Union[str, List[str]]] = None
    severity: Optional[Union[str, List[str]]] = None
    acknowledged: Optional[bool] = None
    order: Optional[str] = None
    language: Optional[str] = None
    limit: Optional[int] = SECURITY_EVENTS_LIMIT_DEFAULT
    anchor: Optional[str] = None


# Shared inputSchema properties for filters common to list/statistics tools.
_FILTER_PROPERTIES: Dict[str, Any] = {
    "organization_id": {
        "type": "string",
        "description": "Organization UUID (default: configured/own org; partner orgs include child companies)"
    },
    "device_id": {
        "type": "string",
        "description": "Target ID: device UUID or email address (targetId)"
    },
    "event_type": _enum_array(
        ALLOWED_ENGINES,
        "Engine(s). Mutually exclusive with engine_group. Connection issues: systemEventsLog, edr"
    ),
    "engine_group": _enum_array(
        ALLOWED_ENGINE_GROUPS,
        "Engine group(s): epp=Endpoint Protection, edr, ecp=Collaboration Protection, xm=Exposure Mgmt. "
        "Default: all groups when no engine given"
    ),
    "severity": _enum_array(ALLOWED_SEVERITIES, "Severity filter"),
    "acknowledged": {
        "type": "boolean",
        "description": "Filter by acknowledgement status (default: all)"
    },
    "created_timestamp_start": {
        "type": "string",
        "format": "date-time",
        "description": "persistenceTimestampStart, inclusive (default: 24h before end). Range max 30 days"
    },
    "created_timestamp_end": {
        "type": "string",
        "format": "date-time",
        "description": "persistenceTimestampEnd, exclusive (default: now)"
    },
}


class EventsModule(BaseModule):
    """Module for security events management."""

    @property
    def name(self) -> str:
        return "events"

    @property
    def description(self) -> str:
        return "WithSecure Elements security events management"

    def _register_resources(self) -> None:
        """Register resources for events."""
        self._resources.append({
            "uri": "withsecure://events",
            "name": "Security Events",
            "description": "WithSecure Elements security events (last 24h)",
            "mimeType": "application/json"
        })

    def _register_tools(self) -> None:
        """Register tools for events."""
        self._tools.extend([
            {
                "name": "list_events",
                "description": "Query security events (max 30-day range). Paginate with anchor=nextAnchor.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        **_FILTER_PROPERTIES,
                        "order": {
                            "type": "string",
                            "enum": ALLOWED_ORDER_VALUES,
                            "default": "desc",
                            "description": "Sort order by persistence time"
                        },
                        "language": {
                            "type": "string",
                            "enum": ALLOWED_LANGUAGES,
                            "description": "Language of message/description (default: en)"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": SECURITY_EVENTS_LIMIT_MIN,
                            "maximum": SECURITY_EVENTS_LIMIT_MAX,
                            "default": SECURITY_EVENTS_LIMIT_DEFAULT,
                            "description": "Page size"
                        },
                        "anchor": {
                            "type": "string",
                            "description": "nextAnchor from a previous response"
                        }
                    }
                }
            },
            {
                "name": "get_event",
                "description": "Find one security event by ID (scans the last 30 days; narrow with filters for speed)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "Event ID"
                        },
                        "organization_id": _FILTER_PROPERTIES["organization_id"],
                        "device_id": _FILTER_PROPERTIES["device_id"],
                        "engine_group": _FILTER_PROPERTIES["engine_group"],
                        "created_timestamp_start": {
                            "type": "string",
                            "format": "date-time",
                            "description": "persistenceTimestampStart (default: 30 days ago)"
                        },
                        "created_timestamp_end": _FILTER_PROPERTIES["created_timestamp_end"]
                    },
                    "required": ["event_id"]
                }
            },
            {
                "name": "get_event_types",
                "description": "List allowed filter values (engines, groups, severities, count properties, languages)",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_event_statistics",
                "description": "Count security events grouped by a property (aggregation, max 30-day range)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "string",
                            "enum": ALLOWED_COUNT_VALUES,
                            "default": "engine",
                            "description": "Property to group by"
                        },
                        **_FILTER_PROPERTIES
                    }
                }
            }
        ])

    # ----- helpers -----

    @staticmethod
    def _ensure_list(value: Optional[Union[str, List[str]]]) -> Optional[List[str]]:
        if value is None or value == "" or value == []:
            return None
        if isinstance(value, list):
            return value
        # Tolerate comma-separated strings ("epp,edr")
        return [v.strip() for v in value.split(",") if v.strip()]

    @staticmethod
    def _validate(values: Optional[List[str]], allowed: List[str], label: str) -> None:
        if values:
            invalid = [v for v in values if v not in allowed]
            if invalid:
                raise ValueError(
                    f"Invalid {label}: " + ", ".join(invalid) + ". Allowed: " + ", ".join(allowed)
                )

    @staticmethod
    def _time_range(start: Optional[str], end: Optional[str],
                    default_span: timedelta = DEFAULT_RANGE) -> Dict[str, str]:
        """Build persistenceTimestamp bounds.

        The API rejects requests without a start (including end-only requests),
        so a start is always derived when missing.
        """
        params: Dict[str, str] = {}
        if end:
            params["persistenceTimestampEnd"] = end
        if start:
            params["persistenceTimestampStart"] = start
        else:
            end_dt = _parse_ts(end) if end else datetime.now(timezone.utc)
            params["persistenceTimestampStart"] = _iso(end_dt - default_span)
        return params

    def _build_query(self, args: Dict[str, Any], default_span: timedelta = DEFAULT_RANGE) -> Dict[str, Any]:
        """Map common tool arguments to API form fields (with validation)."""
        params: Dict[str, Any] = {}

        org_id = args.get("organization_id") or self.config.organization_id
        if org_id:
            params["organizationId"] = org_id

        params.update(self._time_range(
            args.get("created_timestamp_start"), args.get("created_timestamp_end"), default_span
        ))

        if args.get("device_id"):
            params["targetId"] = args["device_id"]

        engines = self._ensure_list(args.get("event_type"))
        groups = self._ensure_list(args.get("engine_group"))
        severities = self._ensure_list(args.get("severity"))
        self._validate(engines, ALLOWED_ENGINES, "engine(s)")
        self._validate(groups, ALLOWED_ENGINE_GROUPS, "engine_group(s)")
        self._validate(severities, ALLOWED_SEVERITIES, "severity(ies)")
        if engines and groups:
            raise ValueError("event_type (engine) and engine_group are mutually exclusive")
        if engines:
            params["engine"] = engines
        else:
            # One of engine/engineGroup is required by the API.
            params["engineGroup"] = groups or list(ALLOWED_ENGINE_GROUPS)
        if severities:
            params["severity"] = severities

        if args.get("acknowledged") is not None:
            params["acknowledged"] = "true" if args["acknowledged"] else "false"
        return params

    async def _post(self, params: Dict[str, Any], what: str, aggregate: bool = False) -> Dict[str, Any]:
        """POST a security events query (form-urlencoded) and return the JSON body."""
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Accept"] = "application/vnd.withsecure.aggr+json" if aggregate else "application/json"

        response = await self.auth._client.post(SECURITY_EVENTS_PATH, headers=headers, data=params)
        if response.status_code != 200:
            raise Exception(f"Error retrieving {what}: {response.status_code} - {response.text}")
        return response.json()

    # ----- operations -----

    async def _get_events(self, filters: Optional[EventFilters] = None) -> str:
        """Retrieve a page of security events."""
        filters = filters or EventFilters()
        params = self._build_query(filters.model_dump())

        if filters.order:
            self._validate([filters.order], ALLOWED_ORDER_VALUES, "order")
            params["order"] = filters.order
        if filters.language:
            self._validate([filters.language], ALLOWED_LANGUAGES, "language")
            params["language"] = filters.language
        limit = filters.limit or SECURITY_EVENTS_LIMIT_DEFAULT
        params["limit"] = max(SECURITY_EVENTS_LIMIT_MIN, min(int(limit), SECURITY_EVENTS_LIMIT_MAX))
        if filters.anchor:
            params["anchor"] = filters.anchor

        return self._dump(await self._post(params, "events"))

    async def _get_event(self, event_id: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Find a specific event by ID.

        The API has no event-ID filter, so pages of the (optionally narrowed)
        query are scanned until the event is found.
        """
        args = dict(arguments or {})
        args.pop("event_id", None)
        # Stay just inside the API's 30-day window when no start is given.
        span = timedelta(days=MAX_RANGE_DAYS) - timedelta(minutes=5)
        params = self._build_query(args, default_span=span)
        params["limit"] = SECURITY_EVENTS_LIMIT_MAX

        scanned = 0
        for _ in range(GET_EVENT_MAX_PAGES):
            data = await self._post(params, "event")
            items = data.get("items", [])
            scanned += len(items)
            for item in items:
                if item.get("id") == event_id:
                    return self._dump(item)
            anchor = data.get("nextAnchor")
            if not anchor:
                break
            params["anchor"] = anchor

        raise ValueError(
            f"Event {event_id} not found (scanned {scanned} events). "
            "Narrow with device_id, engine_group or created_timestamp_start."
        )

    async def _get_event_types(self) -> str:
        """Return allowed filter values from the API spec (no API call)."""
        return self._dump({
            "engines": ALLOWED_ENGINES,
            "engineGroups": ALLOWED_ENGINE_GROUPS,
            "severities": ALLOWED_SEVERITIES,
            "countValues": ALLOWED_COUNT_VALUES,
            "orderValues": ALLOWED_ORDER_VALUES,
            "languages": ALLOWED_LANGUAGES,
            "actions": KNOWN_ACTIONS,
            "limits": {
                "min": SECURITY_EVENTS_LIMIT_MIN,
                "max": SECURITY_EVENTS_LIMIT_MAX
            },
            "maxRangeDays": MAX_RANGE_DAYS
        })

    async def _get_event_statistics(self, filters: Dict[str, Any]) -> str:
        """Aggregate events (grouped and counted by the `count` property)."""
        count = filters.get("count") or "engine"
        self._validate([count], ALLOWED_COUNT_VALUES, "count")
        params = self._build_query(filters)
        params["count"] = count
        return self._dump(await self._post(params, "statistics", aggregate=True))

    async def read_resource(self, uri: str) -> Optional[str]:
        """Read an event resource."""
        if uri == "withsecure://events":
            return await self._get_events()
        if uri.startswith("withsecure://events/"):
            event_id = uri.split("/")[-1]
            return await self._get_event(event_id)
        return None

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        arguments = arguments or {}
        try:
            if tool_name == "list_events":
                text = await self._get_events(EventFilters(**arguments))
            elif tool_name == "get_event":
                text = await self._get_event(arguments["event_id"], arguments)
            elif tool_name == "get_event_types":
                text = await self._get_event_types()
            elif tool_name == "get_event_statistics":
                text = await self._get_event_statistics(arguments)
            else:
                return None

            return {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }

        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }

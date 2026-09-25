"""
MCP module for WithSecure Elements incidents (BCDs) management.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from .base import BaseModule


INCIDENT_STATUSES = ["new", "acknowledged", "inProgress", "monitoring", "closed", "waitingForCustomer"]
INCIDENT_RESOLUTIONS = [
    "unconfirmed", "incident", "falsePositive", "merged", "autoUnconfirmed", "autoFalsePositive",
    "securityTest", "acceptedRisk", "acceptedBehavior", "inconclusive", "confirmed",
]
RISK_LEVELS = ["info", "low", "medium", "high", "severe"]
INCIDENT_SOURCES = [
    "endpoint", "cloud", "customer", "endpointExpert", "identityAzure", "workloadAzure", "workloadAws",
]
UPDATE_TYPES = [
    "capabilityNeeds", "categories", "closeElevationMessage", "comment", "detection",
    "elevateIncidentMessage", "elevationMessage", "merge", "patch", "responseAction", "risk",
    "threatInvestigationResult", "threatValidationResult",
]

# API page-size limits (see API reference).
INCIDENTS_MAX_LIMIT = 50
DETECTIONS_MAX_LIMIT = 100
UPDATES_MAX_LIMIT = 100
# Safety cap for fetch_all so a huge BCD cannot flood the model context.
DETECTIONS_FETCH_ALL_CAP = 5000


def _as_list(value: Any) -> Optional[List[str]]:
    """Accept a single value or a list for multi-value query filters."""
    if value is None or value == "" or value == []:
        return None
    return value if isinstance(value, list) else [value]


def _clamp(value: Optional[int], default: int, maximum: int) -> int:
    return max(1, min(int(value or default), maximum))


class IncidentFilters(BaseModel):
    """Filters for incident search (GET /incidents/v1/incidents)."""

    organization_id: Optional[str] = None
    incident_id: Optional[str] = None
    created_timestamp_start: Optional[str] = None
    created_timestamp_end: Optional[str] = None
    updated_timestamp_start: Optional[str] = None
    updated_timestamp_end: Optional[str] = None
    exclusive_start: Optional[bool] = None
    archived: Optional[bool] = None
    status: Optional[Any] = None
    resolution: Optional[Any] = None
    risk_level: Optional[Any] = None
    # Deprecated alias kept for backward compatibility: the API filters on riskLevel.
    severity: Optional[Any] = None
    source: Optional[Any] = None
    order: Optional[str] = None
    limit: Optional[int] = 20
    anchor: Optional[str] = None


def _time_range_props(prefix: str, label: str) -> Dict[str, Any]:
    return {
        f"{prefix}_timestamp_start": {
            "type": "string", "format": "date-time",
            "description": f"{label} lower bound (inclusive), ISO 8601",
        },
        f"{prefix}_timestamp_end": {
            "type": "string", "format": "date-time",
            "description": f"{label} upper bound (exclusive), ISO 8601",
        },
    }


ORG_PROP = {"organization_id": {"type": "string", "description": "Organization UUID (defaults to configured/own org)"}}
ANCHOR_PROP = {"anchor": {"type": "string", "description": "nextAnchor from a previous response, to fetch the next page"}}


class IncidentsModule(BaseModule):
    """Module for incidents (Broad Context Detections) management."""

    @property
    def name(self) -> str:
        return "incidents"

    @property
    def description(self) -> str:
        return "WithSecure Elements incidents (Broad Context Detections) management"

    def _register_resources(self) -> None:
        """Register resources for incidents."""
        self._resources.append({
            "uri": "withsecure://incidents",
            "name": "Incidents",
            "description": "WithSecure Elements incidents list",
            "mimeType": "application/json"
        })

    def _register_tools(self) -> None:
        """Register tools for incidents."""
        self._tools.extend([
            {
                "name": "list_incidents",
                "description": "List WithSecure Elements incidents (BCDs), newest first by default. "
                               "Paginate with anchor/nextAnchor.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        **ORG_PROP,
                        "status": {
                            "type": "array", "items": {"type": "string", "enum": INCIDENT_STATUSES},
                            "description": "Filter by one or more statuses"
                        },
                        "resolution": {
                            "type": "array", "items": {"type": "string", "enum": INCIDENT_RESOLUTIONS},
                            "description": "Filter by one or more resolutions"
                        },
                        "risk_level": {
                            "type": "array", "items": {"type": "string", "enum": RISK_LEVELS},
                            "description": "Filter by one or more risk levels"
                        },
                        "source": {
                            "type": "array", "items": {"type": "string", "enum": INCIDENT_SOURCES},
                            "description": "Filter by one or more incident sources"
                        },
                        "archived": {
                            "type": "boolean",
                            "description": "Include archived incidents (false recommended)"
                        },
                        **_time_range_props("created", "Creation time"),
                        **_time_range_props("updated", "Last update time (not combinable with created_*)"),
                        "exclusive_start": {
                            "type": "boolean",
                            "description": "Treat *_timestamp_start as exclusive"
                        },
                        "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
                        "limit": {
                            "type": "integer", "minimum": 1, "maximum": INCIDENTS_MAX_LIMIT, "default": 20,
                            "description": "Page size"
                        },
                        **ANCHOR_PROP,
                    }
                }
            },
            {
                "name": "get_incident",
                "description": "Retrieve details of a specific incident (BCD)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {"type": "string", "description": "Incident UUID"},
                        **ORG_PROP,
                    },
                    "required": ["incident_id"]
                }
            },
            {
                "name": "update_incident_status",
                "description": "Update an incident (BCD) status. A 'resolution' is required when status is 'closed'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {"type": "string", "description": "Incident UUID"},
                        "status": {"type": "string", "enum": INCIDENT_STATUSES, "description": "New status"},
                        "resolution": {
                            "type": "string", "enum": INCIDENT_RESOLUTIONS,
                            "description": "Resolution, required when status is 'closed'"
                        }
                    },
                    "required": ["incident_id", "status"]
                }
            },
            {
                "name": "add_incident_comment",
                "description": "Add a comment to one or more incidents (BCDs)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "targets": {
                            "type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 10,
                            "description": "Incident UUIDs (1-10)"
                        },
                        "comment": {"type": "string", "description": "Comment text"}
                    },
                    "required": ["targets", "comment"]
                }
            },
            {
                "name": "list_incident_detections",
                "description": "List the detections of a given incident (BCD). Set fetch_all=true to "
                               "retrieve every detection across all pages in one call.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {"type": "string", "description": "Incident UUID"},
                        **ORG_PROP,
                        **_time_range_props("created", "Detection creation time"),
                        "fetch_all": {
                            "type": "boolean", "default": False,
                            "description": "Follow pagination and return all detections (up to max_items)"
                        },
                        "max_items": {
                            "type": "integer", "minimum": 1, "maximum": DETECTIONS_FETCH_ALL_CAP, "default": 1000,
                            "description": "Upper bound on detections returned when fetch_all=true"
                        },
                        "include_activity_context": {
                            "type": "boolean", "default": True,
                            "description": "Include the verbose activityContext of each detection; "
                                           "set false for a lighter overview"
                        },
                        "limit": {
                            "type": "integer", "minimum": 1, "maximum": DETECTIONS_MAX_LIMIT, "default": 100,
                            "description": "Page size (single-page mode)"
                        },
                        **ANCHOR_PROP,
                    },
                    "required": ["incident_id"]
                }
            },
            {
                "name": "get_incident_updates",
                "description": "Get the update history of an incident (BCD): status changes, comments, "
                               "added detections, risk changes, response actions...",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {"type": "string", "description": "Incident UUID"},
                        **ORG_PROP,
                        "type": {"type": "string", "enum": UPDATE_TYPES, "description": "Filter by update type"},
                        "limit": {
                            "type": "integer", "minimum": 1, "maximum": UPDATES_MAX_LIMIT, "default": 50,
                            "description": "Page size"
                        },
                        **ANCHOR_PROP,
                    },
                    "required": ["incident_id"]
                }
            },
        ])

    async def _get_incidents(self, filters: Optional[IncidentFilters] = None) -> str:
        """Retrieve incidents list."""
        filters = filters or IncidentFilters()
        risk_level = _as_list(filters.risk_level)
        if risk_level is None and filters.severity:
            # Map the legacy 'severity' argument onto the API's riskLevel filter.
            risk_level = ["severe" if s == "critical" else s for s in _as_list(filters.severity)]

        params: Dict[str, Any] = {
            "organizationId": self._org_id(filters.organization_id),
            "incidentId": filters.incident_id,
            "createdTimestampStart": filters.created_timestamp_start,
            "createdTimestampEnd": filters.created_timestamp_end,
            "updatedTimestampStart": filters.updated_timestamp_start,
            "updatedTimestampEnd": filters.updated_timestamp_end,
            "status": _as_list(filters.status),
            "resolution": _as_list(filters.resolution),
            "riskLevel": risk_level,
            "order": filters.order,
            "limit": _clamp(filters.limit, 20, INCIDENTS_MAX_LIMIT),
            "anchor": filters.anchor,
        }
        if filters.archived is not None:
            params["archived"] = str(filters.archived).lower()
        if filters.exclusive_start is not None:
            params["exclusiveStart"] = str(filters.exclusive_start).lower()
        source = _as_list(filters.source)
        if source:
            # The API expects sources as a single comma-separated value.
            params["source"] = ",".join(source)

        data = await self._get_json("/incidents/v1/incidents", params, "incidents")
        return self._dump(data)

    async def _get_incident(self, incident_id: str, organization_id: Optional[str] = None) -> str:
        """Retrieve details of a specific incident."""
        params = {"incidentId": incident_id, "organizationId": self._org_id(organization_id)}
        data = await self._get_json("/incidents/v1/incidents", params, "incident")
        items = data.get("items") or []
        if not items:
            raise Exception(f"Incident {incident_id} not found")
        return self._dump(items[0])

    async def _update_incident_status(self, incident_id: str, status: str, resolution: Optional[str] = None) -> str:
        """Update incident (BCD) status via PATCH /incidents/v1/incidents.

        The API updates status by sending the target incident id(s), the new
        status and, when closing, a resolution in the request body. It answers
        207 Multi-Status with a per-target result.
        """
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")

        if status == "closed" and not resolution:
            raise ValueError("A 'resolution' is required when setting status to 'closed'.")

        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"

        data: Dict[str, Any] = {
            "targets": [incident_id],
            "status": status,
        }
        if resolution:
            data["resolution"] = resolution

        response = await self.auth._client.patch(
            "/incidents/v1/incidents",
            headers=headers,
            json=data
        )

        if response.status_code not in [200, 204, 207]:
            raise Exception(f"Error updating status: {response.status_code} - {response.text}")

        try:
            body = response.json()
        except Exception:
            body = {"success": True, "message": f"Incident {incident_id} status updated to {status}"}

        # A 207 can hide a per-target failure; surface it as an error.
        failures = [
            r for r in (body.get("multistatus") or [])
            if isinstance(r, dict) and not 200 <= int(r.get("status", 200)) < 300
        ]
        if failures:
            raise Exception(f"Error updating status: {self._dump(failures)}")
        return self._dump(body)

    async def _add_incident_comment(self, targets: List[str], comment: str) -> str:
        """Add comment to incidents."""
        if not self.auth._client:
            raise RuntimeError("HTTP client not initialized")
        if not 1 <= len(targets) <= 10:
            raise ValueError("'targets' must contain between 1 and 10 incident IDs.")

        headers = await self.auth.get_headers()
        headers["Content-Type"] = "application/json"

        response = await self.auth._client.post(
            "/incidents/v1/comments",
            headers=headers,
            json={"targets": targets, "comment": comment}
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Error adding comment: {response.status_code} - {response.text}")

        try:
            return self._dump(response.json())
        except Exception:
            return self._dump({"success": True, "message": f"Comment added to {len(targets)} incident(s)"})

    async def _get_incident_detections(
        self,
        incident_id: str,
        organization_id: Optional[str] = None,
        limit: int = DETECTIONS_MAX_LIMIT,
        anchor: Optional[str] = None,
        created_timestamp_start: Optional[str] = None,
        created_timestamp_end: Optional[str] = None,
        fetch_all: bool = False,
        max_items: int = 1000,
        include_activity_context: bool = True,
    ) -> str:
        """Retrieve detections for a specific incident (GET /incidents/v1/detections).

        In fetch_all mode, pages of the maximum size are followed via nextAnchor
        until exhausted or max_items is reached; the remaining anchor is returned
        so the caller can resume.
        """
        params: Dict[str, Any] = {
            "incidentId": incident_id,
            "organizationId": self._org_id(organization_id),
            "createdTimestampStart": created_timestamp_start,
            "createdTimestampEnd": created_timestamp_end,
            "anchor": anchor,
        }

        if not fetch_all:
            params["limit"] = _clamp(limit, DETECTIONS_MAX_LIMIT, DETECTIONS_MAX_LIMIT)
            data = await self._get_json("/incidents/v1/detections", params, "detections")
            items = data.get("items") or []
            result: Dict[str, Any] = {"items": items, "count": len(items)}
            if data.get("nextAnchor"):
                result["nextAnchor"] = data["nextAnchor"]
        else:
            max_items = _clamp(max_items, 1000, DETECTIONS_FETCH_ALL_CAP)
            items = []
            next_anchor: Optional[str] = anchor
            while True:
                params["anchor"] = next_anchor
                params["limit"] = min(DETECTIONS_MAX_LIMIT, max_items - len(items))
                data = await self._get_json("/incidents/v1/detections", params, "detections")
                items.extend(data.get("items") or [])
                next_anchor = data.get("nextAnchor")
                if not next_anchor or not data.get("items") or len(items) >= max_items:
                    break
            result = {"items": items, "count": len(items), "complete": not next_anchor}
            if next_anchor:
                result["nextAnchor"] = next_anchor

        if not include_activity_context:
            for item in result["items"]:
                item.pop("activityContext", None)
        return self._dump(result)

    async def _get_incident_updates(
        self,
        incident_id: str,
        organization_id: Optional[str] = None,
        update_type: Optional[str] = None,
        limit: int = 50,
        anchor: Optional[str] = None,
    ) -> str:
        """Retrieve an incident's update history (GET /incidents/v1/updates)."""
        params = {
            "incidentId": incident_id,
            "organizationId": self._org_id(organization_id),
            "type": update_type,
            "limit": _clamp(limit, 50, UPDATES_MAX_LIMIT),
            "anchor": anchor,
        }
        data = await self._get_json("/incidents/v1/updates", params, "incident updates")
        return self._dump(data)

    async def read_resource(self, uri: str) -> Optional[str]:
        """Read an incident resource."""
        if uri == "withsecure://incidents":
            return await self._get_incidents()
        if uri.startswith("withsecure://incidents/"):
            incident_id = uri.split("/")[-1]
            return await self._get_incident(incident_id)
        return None

    async def _dispatch(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Run a tool and return its text result, or None if not handled here."""
        if tool_name == "list_incidents":
            return await self._get_incidents(IncidentFilters(**arguments))

        if tool_name == "get_incident":
            return await self._get_incident(arguments["incident_id"], arguments.get("organization_id"))

        if tool_name == "update_incident_status":
            return await self._update_incident_status(
                arguments["incident_id"], arguments["status"], arguments.get("resolution")
            )

        if tool_name == "add_incident_comment":
            targets = _as_list(arguments["targets"]) or []
            return await self._add_incident_comment(targets, arguments["comment"])

        if tool_name == "list_incident_detections":
            return await self._get_incident_detections(
                arguments["incident_id"],
                organization_id=arguments.get("organization_id"),
                limit=arguments.get("limit", DETECTIONS_MAX_LIMIT),
                anchor=arguments.get("anchor"),
                created_timestamp_start=arguments.get("created_timestamp_start"),
                created_timestamp_end=arguments.get("created_timestamp_end"),
                fetch_all=bool(arguments.get("fetch_all", False)),
                max_items=arguments.get("max_items", 1000),
                include_activity_context=arguments.get("include_activity_context", True),
            )

        if tool_name == "get_incident_updates":
            return await self._get_incident_updates(
                arguments["incident_id"],
                organization_id=arguments.get("organization_id"),
                update_type=arguments.get("type"),
                limit=arguments.get("limit", 50),
                anchor=arguments.get("anchor"),
            )

        return None

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        try:
            text = await self._dispatch(tool_name, arguments or {})
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }
        if text is None:
            return None
        return {"content": [{"type": "text", "text": text}]}

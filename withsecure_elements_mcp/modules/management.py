"""
MCP module for WithSecure Elements administration: audit logs, device invitations,
security profiles and identity exposure findings.
"""

from typing import Any, Dict, List, Optional

from .base import BaseModule


AUDIT_LOGS_MAX_LIMIT = 200
AUDIT_LOGS_MAX_ACTIONS = 20
AUDIT_LOG_LANGUAGES = ["en", "de", "es-MX", "fi", "fr", "it", "ja", "pl", "pt-BR", "sv", "zh-TW"]

INVITATION_STATES = ["expired", "pending"]
INVITATION_LANGUAGES = [
    "cs_CZ", "da_DK", "de_DE", "en_US", "el_GR", "es_ES", "es_MX", "et_EE", "fi_FI", "fr_FR",
    "fr_CA", "hu_HU", "it_IT", "ja_JP", "lt_LT", "nl_NL", "no_NO", "pl_PL", "pt_PT", "pt_BR",
    "ro_RO", "ru_RU", "sl_SI", "sv_SE", "tr_TR", "vi_VN", "zh_HK", "zh_TW", "zh_CN",
]
DELETE_INVITATIONS_MAX = 20
RENEW_INVITATIONS_MAX = 50

PROFILE_TYPES = ["windows", "windowsServer", "mac", "linuxServer", "connector", "mobile"]
PROFILES_MAX_LIMIT = 200

IDENTITY_TYPES = ["member", "guest"]
IDENTITIES_MAX_LIMIT = 200

ORG_PROP = {"organization_id": {"type": "string", "description": "Organization UUID (defaults to configured/own org)"}}
ANCHOR_PROP = {"anchor": {"type": "string", "description": "nextAnchor from a previous response, to fetch the next page"}}
ORDER_PROP = {"order": {"type": "string", "enum": ["asc", "desc"]}}


def _clamp(value: Optional[int], default: int, maximum: int) -> int:
    return max(1, min(int(value or default), maximum))


def _as_list(value: Any) -> List[str]:
    if value is None or value == "":
        return []
    return value if isinstance(value, list) else [value]


def _bool(value: Optional[bool]) -> Optional[str]:
    return None if value is None else str(bool(value)).lower()


class ManagementModule(BaseModule):
    """Audit logs, invitations, profiles and identity exposure."""

    @property
    def name(self) -> str:
        return "management"

    @property
    def description(self) -> str:
        return "WithSecure Elements audit logs, device invitations, profiles and identity exposure"

    def _register_resources(self) -> None:
        """No resources for this module."""

    def _register_tools(self) -> None:
        """Register management tools."""
        self._tools.extend([
            {
                "name": "list_audit_logs",
                "description": "List audit log entries (who did what in Elements). Max range 30 days; "
                               "defaults to the last 30 days.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        **ORG_PROP,
                        "server_timestamp_start": {
                            "type": "string", "format": "date-time",
                            "description": "Lower bound, ISO 8601 (within the last 30 days)"
                        },
                        "server_timestamp_end": {
                            "type": "string", "format": "date-time",
                            "description": "Upper bound, ISO 8601 (requires server_timestamp_start)"
                        },
                        "action": {
                            "type": "array", "items": {"type": "string"}, "maxItems": AUDIT_LOGS_MAX_ACTIONS,
                            "description": "Public action names, e.g. login, assignProfile, isolateFromNetwork, "
                                           "incidentStatusChanged, deleteDevice, responseActionExecuted"
                        },
                        "username": {"type": "string", "description": "Username or email of the actor"},
                        "organization_name": {"type": "string"},
                        "exclusive_start": {"type": "boolean"},
                        "language": {"type": "string", "enum": AUDIT_LOG_LANGUAGES, "default": "en"},
                        **ORDER_PROP,
                        "limit": {"type": "integer", "minimum": 1, "maximum": AUDIT_LOGS_MAX_LIMIT, "default": 100},
                        **ANCHOR_PROP,
                    }
                }
            },
            {
                "name": "list_invitations",
                "description": "List device invitations of a company",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        **ORG_PROP,
                        "state": {"type": "string", "enum": INVITATION_STATES, "default": "pending"},
                        **ANCHOR_PROP,
                    }
                }
            },
            {
                "name": "create_invitation",
                "description": "Send a device installation invitation by email (valid 30 days)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Recipient email"},
                        "subscription_key": {"type": "string", "description": "Subscription the device will use"},
                        **ORG_PROP,
                        "alias": {"type": "string", "description": "Device display name"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "language": {"type": "string", "enum": INVITATION_LANGUAGES, "default": "en_US"},
                        "timezone": {"type": "string", "description": "e.g. UTC, Europe/Paris", "default": "UTC"},
                    },
                    "required": ["email", "subscription_key"]
                }
            },
            {
                "name": "delete_invitations",
                "description": "Delete device invitations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "invitation_ids": {
                            "type": "array", "items": {"type": "string"},
                            "minItems": 1, "maxItems": DELETE_INVITATIONS_MAX,
                            "description": "Invitation IDs (1-20)"
                        },
                        **ORG_PROP,
                    },
                    "required": ["invitation_ids"]
                }
            },
            {
                "name": "renew_invitations",
                "description": "Renew expired invitations (operation=renew) or resend the email of "
                               "pending ones (operation=resend)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "invitation_ids": {
                            "type": "array", "items": {"type": "string"},
                            "minItems": 1, "maxItems": RENEW_INVITATIONS_MAX,
                            "description": "Invitation IDs (1-50)"
                        },
                        "operation": {"type": "string", "enum": ["renew", "resend"]},
                        **ORG_PROP,
                    },
                    "required": ["invitation_ids", "operation"]
                }
            },
            {
                "name": "list_profiles",
                "description": "List security profiles of a product type (metadata only, not settings). "
                               "Profile IDs can be used with assign_profile.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": PROFILE_TYPES},
                        **ORG_PROP,
                        "subaccounts": {"type": "boolean", "description": "Include child organizations' profiles"},
                        **ORDER_PROP,
                        "limit": {"type": "integer", "minimum": 1, "maximum": PROFILES_MAX_LIMIT, "default": 200},
                        **ANCHOR_PROP,
                    },
                    "required": ["type"]
                }
            },
            {
                "name": "list_exposure_identities",
                "description": "List Exposure Management findings on Microsoft Entra ID identities "
                               "(e.g. breached credentials, no MFA)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        **ORG_PROP,
                        "type": {"type": "string", "enum": IDENTITY_TYPES},
                        **ORDER_PROP,
                        "limit": {"type": "integer", "minimum": 1, "maximum": IDENTITIES_MAX_LIMIT, "default": 50},
                        **ANCHOR_PROP,
                    }
                }
            },
        ])

    async def _list_audit_logs(self, args: Dict[str, Any]) -> Any:
        if args.get("server_timestamp_end") and not args.get("server_timestamp_start"):
            raise ValueError("server_timestamp_end requires server_timestamp_start")
        actions = _as_list(args.get("action"))
        if len(actions) > AUDIT_LOGS_MAX_ACTIONS:
            raise ValueError(f"At most {AUDIT_LOGS_MAX_ACTIONS} actions per request")
        params = {
            "organizationId": self._org_id(args.get("organization_id")),
            "serverTimestampStart": args.get("server_timestamp_start"),
            "serverTimestampEnd": args.get("server_timestamp_end"),
            "action": actions or None,
            "username": args.get("username"),
            "organizationName": args.get("organization_name"),
            "exclusiveStart": _bool(args.get("exclusive_start")),
            "language": args.get("language"),
            "order": args.get("order"),
            "limit": _clamp(args.get("limit"), 100, AUDIT_LOGS_MAX_LIMIT),
            "anchor": args.get("anchor"),
        }
        return await self._get_json("/audit-logs/v1/audit-logs", params, "audit logs")

    async def _list_invitations(self, args: Dict[str, Any]) -> Any:
        params = {
            "organizationId": self._org_id(args.get("organization_id")),
            "state": args.get("state"),
            "anchor": args.get("anchor"),
        }
        return await self._get_json("/invitations/v1/invitations", params, "invitations")

    async def _create_invitation(self, args: Dict[str, Any]) -> Any:
        invitation = {
            "email": args["email"],
            "subscriptionKey": args["subscription_key"],
            "alias": args.get("alias"),
            "firstName": args.get("first_name"),
            "lastName": args.get("last_name"),
            "language": args.get("language"),
            "timezone": args.get("timezone"),
        }
        body: Dict[str, Any] = {"invitations": [{k: v for k, v in invitation.items() if v is not None}]}
        organization_id = self._org_id(args.get("organization_id"))
        if organization_id:
            body["organizationId"] = organization_id
        return await self._send("POST", "/invitations/v1/invitations", "creating invitation", body=body)

    async def _delete_invitations(self, args: Dict[str, Any]) -> Any:
        ids = _as_list(args.get("invitation_ids"))
        if not 1 <= len(ids) <= DELETE_INVITATIONS_MAX:
            raise ValueError(f"invitation_ids must contain 1-{DELETE_INVITATIONS_MAX} IDs")
        params = {"organizationId": self._org_id(args.get("organization_id")), "invitationId": ids}
        return await self._send("DELETE", "/invitations/v1/invitations", "deleting invitations", params=params)

    async def _renew_invitations(self, args: Dict[str, Any]) -> Any:
        ids = _as_list(args.get("invitation_ids"))
        if not 1 <= len(ids) <= RENEW_INVITATIONS_MAX:
            raise ValueError(f"invitation_ids must contain 1-{RENEW_INVITATIONS_MAX} IDs")
        organization_id = self._org_id(args.get("organization_id"))
        if not organization_id:
            raise ValueError("organization_id is required")
        body = {"organizationId": organization_id, "operation": args["operation"], "invitations": ids}
        await self._send("PUT", "/invitations/v1/invitations", "renewing invitations", ok=(200, 204), body=body)
        return {"success": True, "operation": args["operation"], "invitations": len(ids)}

    async def _list_profiles(self, args: Dict[str, Any]) -> Any:
        params = {
            "organizationId": self._org_id(args.get("organization_id")),
            "type": args["type"],
            "subaccounts": _bool(args.get("subaccounts")),
            "order": args.get("order"),
            "limit": _clamp(args.get("limit"), 200, PROFILES_MAX_LIMIT),
            "anchor": args.get("anchor"),
        }
        return await self._get_json("/profiles/v1/profiles", params, "profiles")

    async def _list_exposure_identities(self, args: Dict[str, Any]) -> Any:
        params = {
            "organizationId": self._org_id(args.get("organization_id")),
            "type": args.get("type"),
            "order": args.get("order"),
            "limit": _clamp(args.get("limit"), 50, IDENTITIES_MAX_LIMIT),
            "anchor": args.get("anchor"),
        }
        return await self._get_json("/identities/v1/exposure-identities", params, "exposure identities")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool by name with arguments."""
        handlers = {
            "list_audit_logs": self._list_audit_logs,
            "list_invitations": self._list_invitations,
            "create_invitation": self._create_invitation,
            "delete_invitations": self._delete_invitations,
            "renew_invitations": self._renew_invitations,
            "list_profiles": self._list_profiles,
            "list_exposure_identities": self._list_exposure_identities,
        }
        handler = handlers.get(tool_name)
        if handler is None:
            return None
        try:
            data = await handler(arguments or {})
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
        return {"content": [{"type": "text", "text": self._dump(data)}]}

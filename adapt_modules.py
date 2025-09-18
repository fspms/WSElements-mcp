#!/usr/bin/env python3
"""
Script to adapt all MCP modules for HTTP transport.
"""

def create_http_tools_for_events():
    """Create HTTP tools list for events module."""
    return [
        {
            "name": "list_events",
            "description": "List WithSecure Elements security events",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID (optional)"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Filter by device ID"
                    },
                    "event_type": {
                        "type": "string",
                        "description": "Filter by event type"
                    },
                    "severity": {
                        "type": "string",
                        "description": "Filter by severity level"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of events to return",
                        "default": 100
                    },
                    "created_timestamp_start": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Start of creation time range"
                    },
                    "created_timestamp_end": {
                        "type": "string",
                        "format": "date-time",
                        "description": "End of creation time range"
                    }
                }
            }
        },
        {
            "name": "get_event",
            "description": "Retrieve details of a specific event",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID"
                    }
                },
                "required": ["event_id"]
            }
        },
        {
            "name": "get_event_types",
            "description": "Retrieve list of available event types",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_event_statistics",
            "description": "Retrieve event statistics",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID (optional)"
                    },
                    "created_timestamp_start": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Start of time range"
                    },
                    "created_timestamp_end": {
                        "type": "string",
                        "format": "date-time",
                        "description": "End of time range"
                    }
                }
            }
        }
    ]

def create_http_tools_for_organizations():
    """Create HTTP tools list for organizations module."""
    return [
        {
            "name": "list_organizations",
            "description": "List accessible organizations",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_organization",
            "description": "Retrieve details of a specific organization",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID"
                    }
                },
                "required": ["organization_id"]
            }
        }
    ]

def create_http_tools_for_devices():
    """Create HTTP tools list for devices module."""
    return [
        {
            "name": "list_devices",
            "description": "List devices in the organization",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of devices to return",
                        "default": 100
                    }
                }
            }
        },
        {
            "name": "get_device",
            "description": "Retrieve details of a specific device",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID"
                    }
                },
                "required": ["device_id"]
            }
        },
        {
            "name": "isolate_device",
            "description": "Isolate a device from the network",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for isolation"
                    }
                },
                "required": ["device_id", "reason"]
            }
        },
        {
            "name": "unisolate_device",
            "description": "Unisolate a device from the network",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID"
                    }
                },
                "required": ["device_id"]
            }
        },
        {
            "name": "scan_device",
            "description": "Launch a scan on a device",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID"
                    },
                    "scan_type": {
                        "type": "string",
                        "description": "Type of scan to perform"
                    }
                },
                "required": ["device_id", "scan_type"]
            }
        }
    ]

if __name__ == "__main__":
    print("HTTP tools definitions created for all modules")

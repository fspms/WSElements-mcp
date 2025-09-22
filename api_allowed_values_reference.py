# -*- coding: utf-8 -*-
"""
Référence complète des valeurs autorisées dans les API WithSecure Elements
Extraites des spécifications OpenAPI (api-spec 1.yaml et api-spec 2.yaml)
"""

# ===== SECURITY EVENTS =====

# Engines (moteurs de sécurité)
ALLOWED_ENGINES = [
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
    # Engines supplémentaires de la spec 2
    "manualScanning",
    "cloud"  # deprecated mais encore présent
]

# Engine Groups (groupes de moteurs)
ALLOWED_ENGINE_GROUPS = [
    "epp",  # Endpoint Protection
    "edr",  # Detection and Response  
    "ecp",  # Collaboration Protection
    "xm"    # Exposure Management
]

# Severities (niveaux de gravité)
ALLOWED_SEVERITIES = [
    "critical",
    "warning", 
    "info"
]

# Count values (pour l'agrégation)
ALLOWED_COUNT_VALUES = [
    "engine",
    "url",
    "alertType", 
    "deviceId",
    "infectionName",
    "categories",
    "appliedRule",
    "filePath",
    "description"
]

# Order (ordre de tri)
ALLOWED_ORDER_VALUES = [
    "asc",
    "desc"
]

# Language (langues supportées)
ALLOWED_LANGUAGES = [
    "en",      # English
    "de",      # German
    "es-MX",   # Spanish (Mexico)
    "fi",      # Finnish
    "fr",      # French
    "it",      # Italian
    "ja",      # Japanese
    "pl",      # Polish
    "pt-BR",   # Portuguese (Brazil)
    "sv",      # Swedish
    "zh-TW"    # Chinese (Taiwan)
]

# Actions (actions effectuées)
ALLOWED_ACTIONS = [
    "none",
    "blocked",
    "renamed", 
    "deleted",
    "disinfected",
    "quarantined",
    "created",
    "closed",
    "merged",
    "updated",
    "reported"
]

# Infection Types (types d'infection)
ALLOWED_INFECTION_TYPES = [
    "virus",
    "spyware",
    "riskware"
]

# Access Operations (opérations d'accès)
ALLOWED_ACCESS_OPERATIONS = [
    "open-read",
    "open-write", 
    "close",
    "rename",
    "delete"
]

# Alert Types (types d'alertes)
ALLOWED_ALERT_TYPES = [
    # File Scanning
    "on_access_scanner.file_infection.nothing",
    "on_access_scanner.file_infection.none",
    "on_access_scanner.file_infection.blocked",
    "on_access_scanner.file_infection.renamed",
    "on_access_scanner.file_infection.deleted", 
    "on_access_scanner.file_infection.disinfected",
    "on_access_scanner.file_infection.quarantined",
    "on_demand_scanner.file_infection.nothing",
    # DataGuard
    "access_control.file.reported",
    "access_control.file.block",
    # Activity Monitor / Server Share Protection
    "activity_monitor.server_share_protection.backup_folder_error",
    "activity_monitor.server_share_protection.detected",
    "activity_monitor.server_share_protection.restored",
    "activity_monitor.server_share_protection.restored_from_quarantine"
]

# Risk Levels (niveaux de risque)
ALLOWED_RISK_LEVELS = [
    "medium",
    "high", 
    "critical"
]

# Cloud Providers (fournisseurs cloud)
ALLOWED_CLOUD_PROVIDERS = [
    "AWS",
    "AZURE"
]

# ===== INCIDENTS =====

# Incident Status (statuts d'incident)
ALLOWED_INCIDENT_STATUS = [
    "new",
    "acknowledged",
    "inProgress",
    "monitoring",
    "closed",
    "waitingForCustomer"
]

# Incident Resolution (résolutions d'incident)
ALLOWED_INCIDENT_RESOLUTIONS = [
    "unconfirmed",
    "confirmed", 
    "falsePositive",
    "merged",
    "autoUnconfirmed",
    "autoFalsePositive",
    "securityTest",
    "acceptedRisk",
    "acceptedBehavior"
]

# Incident Risk Levels (niveaux de risque d'incident)
ALLOWED_INCIDENT_RISK_LEVELS = [
    "info",
    "low",
    "medium",
    "high",
    "severe"
]

# Incident Sources (sources d'incident)
ALLOWED_INCIDENT_SOURCES = [
    "endpoint",
    "cloud",           # deprecated
    "customer",
    "endpointExpert",
    "identityAzure",
    "workloadAzure",
    "workloadAws"
]

# ===== DEVICES =====

# Device Types (types d'appareils)
ALLOWED_DEVICE_TYPES = [
    "computer",
    "mobile",
    "connector"
]

# Device States (états d'appareils)
ALLOWED_DEVICE_STATES = [
    "active",
    "blocked",
    "inactive"
]

# Protection Status (statuts de protection)
ALLOWED_PROTECTION_STATUS = [
    "protected",
    "notConnected"
]

# ===== RESPONSE ACTIONS =====

# Operation Types (types d'opérations)
ALLOWED_RESPONSE_OPERATIONS = [
    "isolateFromNetwork",
    "releaseFromNetworkIsolation",
    "assignProfile",
    "scanForMalware",
    "showMessage",
    "turnOnFeature",
    "collectDiagnosticFile",
    # Response Actions supplémentaires
    "fullMemoryDump",
    "enumerateProcesses",
    "netstat"
]

# Features (fonctionnalités)
ALLOWED_FEATURES = [
    "debugLogging"
]

# ===== INVITATIONS =====

# Invitation Operations (opérations d'invitation)
ALLOWED_INVITATION_OPERATIONS = [
    "resend",
    "renew"
]

# ===== CONTENT TYPES ET HEADERS =====

# Content Types (types de contenu)
ALLOWED_CONTENT_TYPES = [
    "application/x-www-form-urlencoded",
    "application/json"
]

# Accept Headers (en-têtes Accept)
ALLOWED_ACCEPT_HEADERS = [
    "application/json",
    "application/vnd.withsecure.aggr+json"
]

# ===== LIMITES ET CONTRAINTES =====

# Security Events Limits
SECURITY_EVENTS_LIMIT_MIN = 1
SECURITY_EVENTS_LIMIT_MAX = 200

# Response Actions Limits
RESPONSE_ACTIONS_TARGETS_MIN = 1
RESPONSE_ACTIONS_TARGETS_MAX = 5

# Device Operations Limits
DEVICE_OPERATIONS_TARGETS_MIN = 1
DEVICE_OPERATIONS_TARGETS_MAX = 5

# Delete Devices Limits
DELETE_DEVICES_MIN = 1
DELETE_DEVICES_MAX = 20

# Invitations Limits
INVITATIONS_MIN = 1
INVITATIONS_MAX = 50

# Incidents Limits
INCIDENTS_LIMIT_MIN = 1
INCIDENTS_LIMIT_MAX = 50
INCIDENTS_LIMIT_DEFAULT = 20

# Turn On Feature Timeout
TURN_ON_FEATURE_TIMEOUT_MIN = 5      # minutes
TURN_ON_FEATURE_TIMEOUT_MAX = 1440   # minutes (24 hours)

# Message Lengths
MESSAGE_MAX_LENGTH = 512
CONSENT_MESSAGE_MAX_LENGTH = 512
COMMENT_MAX_LENGTH = 1000

# ===== MAPPINGS UTILES =====

# Mapping des engines vers leurs groupes
ENGINE_TO_GROUP_MAPPING = {
    # EPP (Endpoint Protection)
    "AMSI": "epp",
    "activityMonitor": "epp", 
    "activityMonitorClientProtection": "epp",
    "applicationControl": "epp",
    "browsingProtection": "epp",
    "connectionControl": "epp",
    "dataGuard": "epp",
    "deepGuard": "epp", 
    "deviceControl": "epp",
    "fileScanning": "epp",
    "firewall": "epp",
    "integrityChecker": "epp",
    "manualScanning": "epp",
    "realtimeScanning": "epp",
    "reputationBasedBrowsing": "epp",
    "setting": "epp",
    "systemEventsLog": "epp",
    "tamperProtection": "epp",
    "webContentControl": "epp",
    "webTrafficScanning": "epp",
    "xFence": "epp",
    
    # EDR (Detection and Response)
    "edr": "edr",
    
    # ECP (Collaboration Protection)
    "emailBreach": "ecp",
    "emailScan": "ecp",
    "inboxRuleScan": "ecp",
    "oneDriveScan": "ecp",
    "sharePointScan": "ecp",
    "teamsScan": "ecp",
    
    # XM (Exposure Management)
    "xmRecommendation": "xm",
    
    # Cloud
    "cloudIdentityAzure": "ecp",  # ou pourrait être "xm"
    "cloudWorkloadAzure": "ecp",  # ou pourrait être "xm"
    "cloud": "ecp",  # deprecated
    
    # Connector
    "connector": "epp"  # ou pourrait être séparé
}

# Mapping des severities vers des codes numériques (pour tri)
SEVERITY_PRIORITY = {
    "critical": 3,
    "warning": 2,
    "info": 1
}

# Mapping des risk levels vers des codes numériques (pour tri)
RISK_LEVEL_PRIORITY = {
    "severe": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1
}

# ===== FONCTIONS UTILITAIRES =====

def validate_engine(engine):
    """Valide qu'un engine est autorisé."""
    if isinstance(engine, str):
        return engine in ALLOWED_ENGINES
    elif isinstance(engine, list):
        return all(e in ALLOWED_ENGINES for e in engine)
    return False

def validate_engine_group(engine_group):
    """Valide qu'un engine group est autorisé."""
    if isinstance(engine_group, str):
        return engine_group in ALLOWED_ENGINE_GROUPS
    elif isinstance(engine_group, list):
        return all(eg in ALLOWED_ENGINE_GROUPS for eg in engine_group)
    return False

def validate_severity(severity):
    """Valide qu'une severity est autorisée."""
    if isinstance(severity, str):
        return severity in ALLOWED_SEVERITIES
    elif isinstance(severity, list):
        return all(s in ALLOWED_SEVERITIES for s in severity)
    return False

def get_engine_group_for_engine(engine):
    """Retourne le groupe d'un engine donné."""
    return ENGINE_TO_GROUP_MAPPING.get(engine)

def validate_limit(limit, min_val, max_val):
    """Valide qu'une limite est dans la plage autorisée."""
    if not isinstance(limit, int):
        return False
    return min_val <= limit <= max_val

# ===== VALIDATION COMPLÈTE =====

def validate_security_events_params(params):
    """Valide tous les paramètres d'une requête security events."""
    errors = []
    
    # Validation engine
    if 'engine' in params:
        if not validate_engine(params['engine']):
            errors.append(f"Engine non valide: {params['engine']}")
    
    # Validation engineGroup
    if 'engineGroup' in params:
        if not validate_engine_group(params['engineGroup']):
            errors.append(f"EngineGroup non valide: {params['engineGroup']}")
    
    # Validation severity
    if 'severity' in params:
        if not validate_severity(params['severity']):
            errors.append(f"Severity non valide: {params['severity']}")
    
    # Validation limit
    if 'limit' in params:
        if not validate_limit(params['limit'], SECURITY_EVENTS_LIMIT_MIN, SECURITY_EVENTS_LIMIT_MAX):
            errors.append(f"Limit doit être entre {SECURITY_EVENTS_LIMIT_MIN} et {SECURITY_EVENTS_LIMIT_MAX}")
    
    # Validation order
    if 'order' in params:
        if params['order'] not in ALLOWED_ORDER_VALUES:
            errors.append(f"Order non valide: {params['order']}")
    
    # Validation count
    if 'count' in params:
        if params['count'] not in ALLOWED_COUNT_VALUES:
            errors.append(f"Count non valide: {params['count']}")
    
    # Validation language
    if 'language' in params:
        if params['language'] not in ALLOWED_LANGUAGES:
            errors.append(f"Language non valide: {params['language']}")
    
    return errors

if __name__ == "__main__":
    # Tests de validation
    print("=== TESTS DE VALIDATION ===")
    
    # Test engines
    print("Engines valides:", validate_engine(["edr", "firewall", "deepGuard"]))
    print("Engine invalide:", validate_engine("moteur_inexistant"))
    
    # Test severities
    print("Severities valides:", validate_severity(["critical", "warning"]))
    print("Severity invalide:", validate_severity("urgent"))
    
    # Test limit
    print("Limit valide:", validate_limit(50, SECURITY_EVENTS_LIMIT_MIN, SECURITY_EVENTS_LIMIT_MAX))
    print("Limit invalide:", validate_limit(500, SECURITY_EVENTS_LIMIT_MIN, SECURITY_EVENTS_LIMIT_MAX))
    
    # Test complet
    test_params = {
        'engine': ['edr', 'firewall'],
        'severity': ['critical'],
        'limit': 100,
        'order': 'desc'
    }
    
    errors = validate_security_events_params(test_params)
    if errors:
        print("Erreurs de validation:", errors)
    else:
        print("Paramètres valides!")

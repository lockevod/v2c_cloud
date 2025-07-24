"""Constants for the V2C Cloud integration."""

DOMAIN = "v2c_cloud"

# Configuration keys
CONF_TOKEN = "token"
CONF_DEVICE_ID = "device_id"

# API endpoints
API_BASE_URL = "https://api.v2c.cloud"

# Default values
DEFAULT_NAME = "V2C Trydan"
DEFAULT_SCAN_INTERVAL = 30

# Charge states
CHARGE_STATE_DISCONNECTED = 0
CHARGE_STATE_CONNECTED_NOT_CHARGING = 1
CHARGE_STATE_CONNECTED_CHARGING = 2

CHARGE_STATE_NAMES = {
    0: "Manguera no conectada",
    1: "Manguera conectada (NO CARGA)",
    2: "Manguera conectada (CARGANDO)"
}

# Dynamic power modes
DYNAMIC_POWER_MODE_NAMES = {
    0: "Timed Power enabled",
    1: "Timed Power Disabled",
    2: "Timed Power Disabled and Exclusive Mode setted",
    3: "Timed Power Disabled and Min Power Mode setted",
    4: "Timed Power Disabled and Grid+FV mode setted",
    5: "Timed Power Disabled and Stop Mode setted"
}

# Error states
SLAVE_ERROR_NAMES = {
    0: "No error",
    1: "Error message",
    2: "Communication error"
}

# Events
EVENT_CHARGING_COMPLETE = "v2c_cloud.charging_complete"
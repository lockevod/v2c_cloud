"""Constants for V2C Cloud integration."""

DOMAIN = "v2c_cloud"

# Configuration
CONF_API_TOKEN = "api_token"
CONF_DEVICE_ID = "device_id"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_NAME = "V2C Cloud"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_TIMEOUT = 10

# API Configuration - Kong Gateway endpoints
API_BASE_URL = "https://v2c.cloud/kong/v2c_service"
API_TIMEOUT = 10
API_RETRIES = 3

# Device States
CHARGE_STATES = {
    0: "disconnected",
    1: "connected_not_charging", 
    2: "connected_charging",
    3: "error",
    4: "paused",
    99: "unknown"
}

# CRITICAL: Entity names that match EMHASS integration expectations
SENSOR_TYPES = {
    "charge_power": {
        "key": "charge_power",
        "translation_key": "charge_power",
        "icon": "mdi:flash",
        "device_class": "power",
        "unit": "W",
        "state_class": "measurement",
    },
    "charge_energy": {
        "key": "charge_energy",
        "translation_key": "charge_energy",
        "icon": "mdi:battery-charging",
        "device_class": "energy",
        "unit": "kWh",
        "state_class": "total_increasing",
    },
    "charge_state": {
        "key": "charge_state",
        "translation_key": "charge_state",
        "icon": "mdi:ev-station",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "charge_current": {
        "key": "charge_current",
        "translation_key": "charge_current",
        "icon": "mdi:current-ac",
        "device_class": "current", 
        "unit": "A",
        "state_class": "measurement",
    },
    "voltage": {
        "key": "voltage",
        "translation_key": "voltage",
        "icon": "mdi:sine-wave",
        "device_class": "voltage",
        "unit": "V", 
        "state_class": "measurement",
    },
    "temperature": {
        "key": "temperature",
        "translation_key": "temperature",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "unit": "°C",
        "state_class": "measurement",
    },
    "session_energy": {
        "key": "session_energy",
        "translation_key": "session_energy",
        "icon": "mdi:battery-plus",
        "device_class": "energy",
        "unit": "kWh",
        "state_class": "total_increasing",
    },
    "session_time": {
        "key": "session_time",
        "translation_key": "session_time",
        "icon": "mdi:timer",
        "device_class": "duration",
        "unit": "min",
        "state_class": "measurement",
    },
    "total_energy": {
        "key": "total_energy",
        "translation_key": "total_energy",
        "icon": "mdi:counter",
        "device_class": "energy",
        "unit": "kWh",
        "state_class": "total_increasing",
    },
    "wifi_signal": {
        "key": "wifi_signal",
        "translation_key": "wifi_signal",
        "icon": "mdi:wifi",
        "device_class": "signal_strength",
        "unit": "dBm",
        "state_class": "measurement",
    },
    "firmware_version": {
        "key": "firmware_version",
        "translation_key": "firmware_version",
        "icon": "mdi:chip",
        "device_class": None,
        "unit": None,
        "state_class": None,
    }
}

# CRITICAL: Switch names that match EMHASS integration expectations
SWITCH_TYPES = {
    "dynamic": {
        "key": "dynamic",
        "translation_key": "dynamic_power",
        "icon": "mdi:auto-fix",
    },
    "paused": {
        "key": "paused",
        "translation_key": "paused",
        "icon": "mdi:pause",
    },
    "locked": {
        "key": "locked",
        "translation_key": "locked",
        "icon": "mdi:lock",
    }
}

# CRITICAL: Number names that match EMHASS integration expectations  
NUMBER_TYPES = {
    "intensity": {
        "key": "intensity",
        "translation_key": "intensity",
        "icon": "mdi:current-ac",
        "min_value": 6,
        "max_value": 32,
        "step": 1,
        "unit": "A",
        "mode": "slider",
    },
    "max_intensity": {
        "key": "max_intensity",
        "translation_key": "max_intensity",
        "icon": "mdi:speedometer",
        "min_value": 6,
        "max_value": 32,
        "step": 1,
        "unit": "A",
        "mode": "box",
    },
    "min_intensity": {
        "key": "min_intensity",
        "translation_key": "min_intensity",
        "icon": "mdi:speedometer-slow",
        "min_value": 6,
        "max_value": 32,
        "step": 1,
        "unit": "A",
        "mode": "box",
    }
}

# CRITICAL: Button names that match EMHASS integration expectations
BUTTON_TYPES = {
    "start_charge": {
        "key": "start_charge",
        "translation_key": "start_charge",
        "icon": "mdi:play",
    },
    "stop_charge": {
        "key": "stop_charge",
        "translation_key": "stop_charge",
        "icon": "mdi:stop",
    },
    "restart_device": {
        "key": "restart_device",
        "translation_key": "restart_device",
        "icon": "mdi:restart",
    },
    "reset_session": {
        "key": "reset_session",
        "translation_key": "reset_session",
        "icon": "mdi:counter",
    }
}
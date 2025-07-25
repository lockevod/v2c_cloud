"""V2C Cloud sensor platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_TYPES, CHARGE_STATES
from .entity import V2CCloudEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up V2C Cloud sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    for sensor_type, sensor_info in SENSOR_TYPES.items():
        entities.append(V2CCloudSensor(coordinator, sensor_type, sensor_info))
    
    async_add_entities(entities)


class V2CCloudSensor(V2CCloudEntity, SensorEntity):
    """V2C Cloud sensor entity."""

    def __init__(self, coordinator, sensor_type: str, sensor_info: dict[str, Any]):
        """Initialize the sensor."""
        super().__init__(coordinator, sensor_type)
        self._sensor_info = sensor_info
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_state_class = sensor_info.get("state_class")
        self._attr_icon = sensor_info.get("icon")
        
        # Use translation key for name
        self._attr_translation_key = sensor_info.get("translation_key")
        self._attr_has_entity_name = True

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert any value to float."""
        try:
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert any value to int."""
        try:
            if value is None:
                return default
            return int(float(value))
        except (ValueError, TypeError):
            return default

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        data = self.coordinator.data
        
        if self._type == "charge_state":
            state_value = self._safe_int(data.get("charge_state", 99))
            return CHARGE_STATES.get(state_value, "unknown")
        elif self._type == "charge_power":
            return self._safe_float(data.get("charge_power", 0))
        elif self._type == "charge_energy":
            # Convert Wh to kWh for display
            return round(self._safe_float(data.get("charge_energy", 0)) / 1000, 2)
        elif self._type == "charge_current":
            return self._safe_float(data.get("charge_current", 0))
        elif self._type == "voltage":
            return self._safe_float(data.get("voltage", 0))
        elif self._type == "temperature":
            return self._safe_float(data.get("temperature", 0))
        elif self._type == "session_energy":
            # Convert Wh to kWh for display
            return round(self._safe_float(data.get("session_energy", 0)) / 1000, 2)
        elif self._type == "session_time":
            return self._safe_float(data.get("session_time", 0))
        elif self._type == "total_energy":
            # Convert Wh to kWh for display
            return round(self._safe_float(data.get("total_energy", 0)) / 1000, 2)
        elif self._type == "wifi_signal":
            return self._safe_int(data.get("wifi_signal", 0))
        elif self._type == "firmware_version":
            firmware = data.get("firmware_version", "Unknown")
            return str(firmware) if firmware is not None else "Unknown"
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None
            
        data = self.coordinator.data
        attributes = {}
        
        if self._type == "charge_state":
            attributes.update({
                "last_updated": data.get("last_updated", ""),
                "raw_state": data.get("charge_state"),
                "connection_time": data.get("connection_time", ""),
            })
        elif self._type == "charge_power":
            # FIXED: Safe conversion to avoid string/int errors
            current_intensity = self._safe_float(data.get("intensity", 0))
            voltage = self._safe_float(data.get("voltage", 230))
            
            attributes.update({
                "max_power": 7400,  # V2C Trydan max power (32A * 230V)
                "min_power": 1380,  # 6A * 230V
                "current_intensity": current_intensity,
                "voltage": voltage,
                "efficiency": "95%",  # Typical EV charger efficiency
            })
        elif self._type in ["charge_energy", "session_energy", "total_energy"]:
            # Additional energy-related attributes - FIXED: Safe conversion
            energy_wh = self._safe_float(data.get(self._type, 0))
            attributes.update({
                "energy_wh": energy_wh,
                "cost_estimate": round(energy_wh * 0.15 / 1000, 2),  # Rough cost estimate
            })
        elif self._type == "charge_current":
            # FIXED: Safe conversion
            max_intensity = self._safe_float(data.get("max_intensity", 32))
            min_intensity = self._safe_float(data.get("min_intensity", 6))
            current_limit = self._safe_float(data.get("intensity", 6))
            
            attributes.update({
                "max_current": max_intensity,
                "min_current": min_intensity,
                "current_limit": current_limit,
            })
        elif self._type == "wifi_signal":
            # FIXED: Safe conversion
            signal = self._safe_int(data.get("wifi_signal", -50))
            if signal > -30:
                quality = "Excellent"
            elif signal > -50:
                quality = "Good"
            elif signal > -70:
                quality = "Fair"
            else:
                quality = "Poor"
            attributes.update({
                "signal_quality": quality,
                "signal_bars": min(4, max(0, int((signal + 100) / 12.5))),
            })
        
        return attributes if attributes else None
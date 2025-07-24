"""V2C Cloud number platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, NUMBER_TYPES
from .entity import V2CCloudEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up V2C Cloud number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    for number_type, number_info in NUMBER_TYPES.items():
        entities.append(V2CCloudNumber(coordinator, number_type, number_info))
    
    async_add_entities(entities)


class V2CCloudNumber(V2CCloudEntity, NumberEntity):
    """V2C Cloud number entity."""

    def __init__(self, coordinator, number_type: str, number_info: dict[str, Any]):
        """Initialize the number entity."""
        super().__init__(coordinator, number_type)
        self._number_info = number_info
        self._attr_icon = number_info.get("icon")
        self._attr_native_min_value = number_info.get("min_value", 0)
        self._attr_native_max_value = number_info.get("max_value", 100)
        self._attr_native_step = number_info.get("step", 1)
        self._attr_native_unit_of_measurement = number_info.get("unit")
        self._attr_mode = NumberMode(number_info.get("mode", "slider"))
        
        # Use translation key for name
        self._attr_translation_key = number_info.get("translation_key")
        self._attr_has_entity_name = True

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if not self.coordinator.data:
            return None
            
        data = self.coordinator.data
        
        if self._type == "intensity":
            return float(data.get("intensity", 6))
        elif self._type == "max_intensity":
            return float(data.get("max_intensity", 32))
        elif self._type == "min_intensity":
            return float(data.get("min_intensity", 6))
        
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            int_value = int(value)
            
            if self._type == "intensity":
                success = await self.coordinator.api.set_intensity(int_value)
                if success:
                    await self.coordinator.async_request_refresh()
                    _LOGGER.info("Successfully set charging intensity to %s A", int_value)
                else:
                    _LOGGER.error("Failed to set charging intensity to %s A", int_value)
            else:
                # max_intensity and min_intensity are typically read-only
                # but we'll log the attempt
                _LOGGER.warning(
                    "Cannot set %s - this is typically a read-only value configured on the device",
                    self._type
                )
                
        except Exception as err:
            _LOGGER.error("Error setting %s to %s: %s", self._type, value, err)
            raise

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None
            
        data = self.coordinator.data
        attributes = {}
        
        if self._type == "intensity":
            # Calculate power based on intensity (single phase)
            current_intensity = data.get("intensity", 6)
            voltage = data.get("voltage", 230)
            calculated_power = current_intensity * voltage
            
            attributes.update({
                "calculated_power_w": calculated_power,
                "calculated_power_kw": round(calculated_power / 1000, 2),
                "voltage": voltage,
                "power_factor": "1.0",  # Assume unity power factor for EV charging
                "charging_phases": 1,    # V2C Trydan is typically single-phase
                "emhass_compatible": True,
                "description": "Primary control for EMHASS optimization",
            })
        elif self._type == "max_intensity":
            attributes.update({
                "description": "Maximum allowed charging current (hardware/installation limit)",
                "configured_by": "installer_or_device_settings",
                "safety_limit": True,
            })
        elif self._type == "min_intensity":
            attributes.update({
                "description": "Minimum charging current (technical minimum for stable charging)",
                "iec_standard": "6A minimum per IEC 61851",
                "technical_limit": True,
            })
        
        return attributes if attributes else None

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        # Only enable intensity by default, others are more for information
        return self._type == "intensity"
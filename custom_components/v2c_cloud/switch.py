"""V2C Cloud switch platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SWITCH_TYPES
from .entity import V2CCloudEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up V2C Cloud switches."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    for switch_type, switch_info in SWITCH_TYPES.items():
        entities.append(V2CCloudSwitch(coordinator, switch_type, switch_info))
    
    async_add_entities(entities)


class V2CCloudSwitch(V2CCloudEntity, SwitchEntity):
    """V2C Cloud switch entity."""

    def __init__(self, coordinator, switch_type: str, switch_info: dict[str, Any]):
        """Initialize the switch."""
        super().__init__(coordinator, switch_type)
        self._switch_info = switch_info
        self._attr_icon = switch_info.get("icon")
        
        # Use translation key for name
        self._attr_translation_key = switch_info.get("translation_key")
        self._attr_has_entity_name = True

    def _safe_bool(self, value: Any, default: bool = False) -> bool:
        """Safely convert any value to bool."""
        try:
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("1", "true", "yes", "on")
            if isinstance(value, (int, float)):
                return value != 0
            return default
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
    def is_on(self) -> bool | None:
        """Return True if the switch is on."""
        if not self.coordinator.data:
            return None
            
        data = self.coordinator.data
        
        if self._type == "dynamic":
            return self._safe_bool(data.get("dynamic_power", False))
        elif self._type == "paused":
            return self._safe_bool(data.get("paused", False))
        elif self._type == "locked":
            return self._safe_bool(data.get("locked", False))
        
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            success = False
            if self._type == "dynamic":
                success = await self.coordinator.api.set_dynamic_power(True)
            elif self._type == "paused":
                success = await self.coordinator.api.set_paused(True)
            elif self._type == "locked":
                success = await self.coordinator.api.set_locked(True)
            
            if success:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to turn on %s", self._type)
        except Exception as err:
            _LOGGER.error("Error turning on %s: %s", self._type, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            success = False
            if self._type == "dynamic":
                success = await self.coordinator.api.set_dynamic_power(False)
            elif self._type == "paused":
                success = await self.coordinator.api.set_paused(False)
            elif self._type == "locked":
                success = await self.coordinator.api.set_locked(False)
            
            if success:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to turn off %s", self._type)
        except Exception as err:
            _LOGGER.error("Error turning off %s: %s", self._type, err)
            raise

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None
            
        data = self.coordinator.data
        attributes = {}
        
        if self._type == "dynamic":
            attributes.update({
                "description": "Enables automatic power adjustment based on available solar power",
                "requires_solar": True,
                "compatible_with_emhass": True,
            })
        elif self._type == "paused":
            # FIXED: Safe conversion for charge_state
            charge_state = self._safe_int(data.get("charge_state", 99))
            attributes.update({
                "description": "Temporarily pauses charging without disconnecting",
                "charge_state": charge_state,
                "can_resume": charge_state in [1, 4],  # connected_not_charging or paused
            })
        elif self._type == "locked":
            attributes.update({
                "description": "Prevents unauthorized use of the charger",
                "security_feature": True,
                "requires_unlock_to_charge": True,
            })
        
        return attributes if attributes else None
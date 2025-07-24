"""V2C Cloud button platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, BUTTON_TYPES
from .entity import V2CCloudEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up V2C Cloud button entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    for button_type, button_info in BUTTON_TYPES.items():
        entities.append(V2CCloudButton(coordinator, button_type, button_info))
    
    async_add_entities(entities)


class V2CCloudButton(V2CCloudEntity, ButtonEntity):
    """V2C Cloud button entity."""

    def __init__(self, coordinator, button_type: str, button_info: dict[str, Any]):
        """Initialize the button."""
        super().__init__(coordinator, button_type)
        self._button_info = button_info
        self._attr_icon = button_info.get("icon")
        
        # Use translation key for name
        self._attr_translation_key = button_info.get("translation_key")
        self._attr_has_entity_name = True

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            success = False
            action_description = ""
            
            if self._type == "start_charge":
                success = await self.coordinator.api.start_charging()
                action_description = "start charging"
            elif self._type == "stop_charge":
                success = await self.coordinator.api.stop_charging()
                action_description = "stop charging"
            elif self._type == "restart_device":
                success = await self.coordinator.api.restart_device()
                action_description = "restart device"
            elif self._type == "reset_session":
                success = await self.coordinator.api.reset_session()
                action_description = "reset session"
            
            if success:
                _LOGGER.info("Successfully executed: %s", action_description)
                # Request refresh after action
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to execute: %s", action_description)
                
        except Exception as err:
            _LOGGER.error("Error pressing button %s: %s", self._type, err)
            raise

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None
            
        data = self.coordinator.data
        attributes = {}
        
        if self._type == "start_charge":
            charge_state = data.get("charge_state", 99)
            attributes.update({
                "description": "Start EV charging session",
                "requires_cable_connected": True,
                "current_state": charge_state,
                "can_start": charge_state in [1, 4],  # connected_not_charging or paused
                "emhass_controlled": True,
            })
        elif self._type == "stop_charge":
            charge_state = data.get("charge_state", 99)
            attributes.update({
                "description": "Stop current EV charging session",
                "current_state": charge_state,
                "can_stop": charge_state == 2,  # connected_charging
                "preserves_connection": True,
                "emhass_controlled": True,
            })
        elif self._type == "restart_device":
            attributes.update({
                "description": "Restart the V2C Trydan device",
                "warning": "Will temporarily interrupt charging if active",
                "use_case": "troubleshooting_connectivity_issues",
                "restart_duration": "30-60 seconds",
            })
        elif self._type == "reset_session":
            session_energy = data.get("session_energy", 0)
            session_time = data.get("session_time", 0)
            attributes.update({
                "description": "Reset current charging session counters",
                "current_session_energy": f"{session_energy/1000:.2f} kWh",
                "current_session_time": f"{session_time} minutes",
                "resets_counters": ["session_energy", "session_time"],
            })
        
        return attributes if attributes else None

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        # Enable start/stop by default as they're commonly used
        # Disable restart/reset by default as they're more administrative
        return self._type in ["start_charge", "stop_charge"]
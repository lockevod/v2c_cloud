"""Support for V2C Cloud button entities."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up V2C Cloud button entities based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    buttons = [
        V2CStartChargeButton(coordinator, config_entry),
        V2CStopChargeButton(coordinator, config_entry),
    ]

    async_add_entities(buttons)


class V2CBaseButton(CoordinatorEntity, ButtonEntity):
    """Base class for V2C button entities."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.data["device_id"])},
            "name": "V2C Trydan",
            "manufacturer": "V2C",
            "model": "Trydan",
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None


class V2CStartChargeButton(V2CBaseButton):
    """Button entity for starting charge."""

    _attr_name = "V2C Start Charge"
    _attr_unique_id = "v2c_start_charge_button"
    _attr_icon = "mdi:play"

    async def async_press(self) -> None:
        """Handle the button press."""
        success = await self.coordinator.api.start_charge()
        if success:
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Charge started successfully")
        else:
            _LOGGER.error("Failed to start charge")


class V2CStopChargeButton(V2CBaseButton):
    """Button entity for stopping charge."""

    _attr_name = "V2C Stop Charge"
    _attr_unique_id = "v2c_stop_charge_button"
    _attr_icon = "mdi:stop"

    async def async_press(self) -> None:
        """Handle the button press."""
        success = await self.coordinator.api.stop_charge()
        if success:
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Charge stopped successfully")
        else:
            _LOGGER.error("Failed to stop charge")
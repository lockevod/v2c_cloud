"""Support for V2C Cloud switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up V2C Cloud switches based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    switches = [
        V2CDynamicSwitch(coordinator, config_entry),
        V2CPausedSwitch(coordinator, config_entry),
        V2CLockedSwitch(coordinator, config_entry),
    ]

    async_add_entities(switches)


class V2CBaseSwitch(CoordinatorEntity, SwitchEntity):
    """Base class for V2C switches."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the switch."""
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


class V2CDynamicSwitch(V2CBaseSwitch):
    """Switch for dynamic charging control."""

    _attr_name = "V2C Dynamic"
    _attr_unique_id = "vc2_trydan_switch_dynamic"
    _attr_icon = "mdi:flash-auto"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data:
            return bool(self.coordinator.data.get("dynamic_enabled"))
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        success = await self.coordinator.api.set_dynamic_power(True)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn on dynamic charging")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        success = await self.coordinator.api.set_dynamic_power(False)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn off dynamic charging")


class V2CPausedSwitch(V2CBaseSwitch):
    """Switch for pause charging control."""

    _attr_name = "V2C Paused"
    _attr_unique_id = "v2c_trydan_switch_paused"
    _attr_icon = "mdi:pause"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on (paused)."""
        if self.coordinator.data:
            return bool(self.coordinator.data.get("paused"))
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on (pause charging)."""
        success = await self.coordinator.api.set_pause_charge(True)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to pause charging")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off (resume charging)."""
        success = await self.coordinator.api.set_pause_charge(False)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to resume charging")


class V2CLockedSwitch(V2CBaseSwitch):
    """Switch for charger lock control."""

    _attr_name = "V2C Locked"
    _attr_unique_id = "v2c_trydan_switch_locked"
    _attr_icon = "mdi:lock"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on (locked)."""
        if self.coordinator.data:
            return bool(self.coordinator.data.get("locked"))
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on (lock charger)."""
        success = await self.coordinator.api.set_lock_charger(True)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to lock charger")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off (unlock charger)."""
        success = await self.coordinator.api.set_lock_charger(False)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to unlock charger")
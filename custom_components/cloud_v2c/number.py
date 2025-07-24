"""Support for V2C Cloud number entities."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfLength
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
    """Set up V2C Cloud number entities based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    numbers = [
        V2CIntensityNumber(coordinator, config_entry),
        V2CMaxIntensityNumber(coordinator, config_entry),
        V2CMinIntensityNumber(coordinator, config_entry),
        V2CKmToChargeNumber(coordinator, config_entry),
    ]

    async_add_entities(numbers)


class V2CBaseNumber(CoordinatorEntity, NumberEntity):
    """Base class for V2C number entities."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the number entity."""
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


class V2CIntensityNumber(V2CBaseNumber):
    """Number entity for charging intensity control."""

    _attr_name = "V2C Intensity"
    _attr_unique_id = "v2c_intensity"
    _attr_native_min_value = 6
    _attr_native_max_value = 32
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_icon = "mdi:current-ac"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data:
            return self.coordinator.data.get("intensity")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        success = await self.coordinator.api.set_charge_current(int(value))
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set charge intensity to %s", value)


class V2CMaxIntensityNumber(V2CBaseNumber):
    """Number entity for maximum charging intensity control."""

    _attr_name = "V2C Max Intensity"
    _attr_unique_id = "v2c_max_intensity"
    _attr_native_min_value = 6
    _attr_native_max_value = 32
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_icon = "mdi:current-ac"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data:
            return self.coordinator.data.get("max_intensity")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        success = await self.coordinator.api.set_max_current(int(value))
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set max intensity to %s", value)


class V2CMinIntensityNumber(V2CBaseNumber):
    """Number entity for minimum charging intensity control."""

    _attr_name = "V2C Min Intensity"
    _attr_unique_id = "v2c_min_intensity"
    _attr_native_min_value = 6
    _attr_native_max_value = 32
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_icon = "mdi:current-ac"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data:
            return self.coordinator.data.get("min_intensity")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        success = await self.coordinator.api.set_min_current(int(value))
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set min intensity to %s", value)


class V2CKmToChargeNumber(V2CBaseNumber):
    """Number entity for kilometers to charge control."""

    _attr_name = "V2C Km to Charge"
    _attr_unique_id = "v2c_km_to_charge"
    _attr_native_min_value = 0
    _attr_native_max_value = 1000
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:car-electric"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data:
            return self.coordinator.data.get("km_to_charge")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        success = await self.coordinator.api.set_km_to_charge(int(value))
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set km to charge to %s", value)
"""Base entity for V2C Cloud integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class V2CCloudEntity(CoordinatorEntity):
    """Base V2C Cloud entity."""

    def __init__(self, coordinator, entity_type: str):
        """Initialize the entity."""
        super().__init__(coordinator)
        self._type = entity_type
        self._attr_unique_id = f"{coordinator.api._device_id}_{entity_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.api._device_id)},
            name="V2C Trydan",
            manufacturer="V2C",
            model="Trydan",
            sw_version=self.coordinator.data.get("firmware_version", "Unknown") if self.coordinator.data else "Unknown",
            configuration_url="https://v2c.cloud",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
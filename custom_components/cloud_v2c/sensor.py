"""Support for V2C Cloud sensors."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfElectricCurrent,
    UnitOfTime,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CHARGE_STATE_NAMES, DYNAMIC_POWER_MODE_NAMES, SLAVE_ERROR_NAMES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up V2C Cloud sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        V2CChargeEnergySensor(coordinator, config_entry),
        V2CChargeKmSensor(coordinator, config_entry),
        V2CChargePowerSensor(coordinator, config_entry),
        V2CChargeStateSensor(coordinator, config_entry),
        V2CNumericalStatusSensor(coordinator, config_entry),
        V2CChargeTimeSensor(coordinator, config_entry),
        V2CContractedPowerSensor(coordinator, config_entry),
        V2CDynamicSensor(coordinator, config_entry),
        V2CDynamicPowerModeSensor(coordinator, config_entry),
        V2CFVPowerSensor(coordinator, config_entry),
        V2CHousePowerSensor(coordinator, config_entry),
        V2CIntensitySensor(coordinator, config_entry),
        V2CLockedSensor(coordinator, config_entry),
        V2CMaxIntensitySensor(coordinator, config_entry),
        V2CMinIntensitySensor(coordinator, config_entry),
        V2CPausedSensor(coordinator, config_entry),
        V2CPauseDynamicSensor(coordinator, config_entry),
        V2CSlaveErrorSensor(coordinator, config_entry),
        V2CTimerSensor(coordinator, config_entry),
    ]

    async_add_entities(sensors)


class V2CBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for V2C sensors."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
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


class V2CChargeEnergySensor(V2CBaseSensor):
    """Sensor for charge energy."""

    _attr_name = "V2C Charge Energy"
    _attr_unique_id = "v2c_trydan_sensor_chargeenergy"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("charge_energy")
        return None


class V2CChargeKmSensor(V2CBaseSensor):
    """Sensor for charge kilometers."""

    _attr_name = "V2C Charge Km"
    _attr_unique_id = "v2c_trydan_sensor_chargekm"
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:car-electric"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("charge_km")
        return None


class V2CChargePowerSensor(V2CBaseSensor):
    """Sensor for charge power."""

    _attr_name = "V2C Charge Power"
    _attr_unique_id = "v2c_trydan_sensor_chargepower"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("charge_power")
        return None


class V2CChargeStateSensor(V2CBaseSensor):
    """Sensor for charge state."""

    _attr_name = "V2C Charge State"
    _attr_unique_id = "v2c_trydan_sensor_chargestate"
    _attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            state_num = self.coordinator.data.get("charge_state")
            if state_num is not None:
                return CHARGE_STATE_NAMES.get(state_num, f"Unknown ({state_num})")
        return None


class V2CNumericalStatusSensor(V2CBaseSensor):
    """Sensor for numerical status."""

    _attr_name = "V2C Numerical Status"
    _attr_unique_id = "v2c_trydan_numericalstatus"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("charge_state")
        return None


class V2CChargeTimeSensor(V2CBaseSensor):
    """Sensor for charge time."""

    _attr_name = "V2C Charge Time"
    _attr_unique_id = "v2c_trydan_sensor_chargetime"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("charge_time")
        return None


class V2CContractedPowerSensor(V2CBaseSensor):
    """Sensor for contracted power."""

    _attr_name = "V2C Contracted Power"
    _attr_unique_id = "v2c_trydan_sensor_contractedpower"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            power = self.coordinator.data.get("contracted_power")
            return power if power != -1 else None
        return None


class V2CDynamicSensor(V2CBaseSensor):
    """Sensor for dynamic state."""

    _attr_name = "V2C Dynamic"
    _attr_unique_id = "vc2_trydan_sensor_dynamic"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("dynamic_enabled")
        return None


class V2CDynamicPowerModeSensor(V2CBaseSensor):
    """Sensor for dynamic power mode."""

    _attr_name = "V2C Dynamic Power Mode"
    _attr_unique_id = "vc2_trydan_sensor_dynamicpowermode"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            mode_num = self.coordinator.data.get("dynamic_power_mode")
            if mode_num is not None:
                return DYNAMIC_POWER_MODE_NAMES.get(mode_num, f"Unknown ({mode_num})")
        return None


class V2CFVPowerSensor(V2CBaseSensor):
    """Sensor for photovoltaic power."""

    _attr_name = "V2C FV Power"
    _attr_unique_id = "vc2_trydan_sensor_fvpower"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("fv_power")
        return None


class V2CHousePowerSensor(V2CBaseSensor):
    """Sensor for house power consumption."""

    _attr_name = "V2C House Power"
    _attr_unique_id = "vc2_trydan_sensor_housepower"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("house_power")
        return None


class V2CIntensitySensor(V2CBaseSensor):
    """Sensor for intensity."""

    _attr_name = "V2C Intensity"
    _attr_unique_id = "v2c_trydan_sensor_intensity"
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("intensity")
        return None


class V2CLockedSensor(V2CBaseSensor):
    """Sensor for locked state."""

    _attr_name = "V2C Locked"
    _attr_unique_id = "v2c_trydan_sensor_locked"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("locked")
        return None


class V2CMaxIntensitySensor(V2CBaseSensor):
    """Sensor for max intensity."""

    _attr_name = "V2C Max Intensity"
    _attr_unique_id = "v2c_trydan_sensor_maxintensity"
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("max_intensity")
        return None


class V2CMinIntensitySensor(V2CBaseSensor):
    """Sensor for min intensity."""

    _attr_name = "V2C Min Intensity"
    _attr_unique_id = "v2c_trydan_sensor_minintensity"
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("min_intensity")
        return None


class V2CPausedSensor(V2CBaseSensor):
    """Sensor for paused state."""

    _attr_name = "V2C Paused"
    _attr_unique_id = "v2c_trydan_sensor_paused"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("paused")
        return None


class V2CPauseDynamicSensor(V2CBaseSensor):
    """Sensor for pause dynamic state."""

    _attr_name = "V2C Pause Dynamic"
    _attr_unique_id = "v2c_trydan_sensor_pausedynamic"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("pause_dynamic")
        return None


class V2CSlaveErrorSensor(V2CBaseSensor):
    """Sensor for slave error state."""

    _attr_name = "V2C Slave Error"
    _attr_unique_id = "v2c_trydan_sensor_slaveerror"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            error_num = self.coordinator.data.get("slave_error")
            if error_num is not None:
                return SLAVE_ERROR_NAMES.get(error_num, f"Unknown ({error_num})")
        return None


class V2CTimerSensor(V2CBaseSensor):
    """Sensor for timer state."""

    _attr_name = "V2C Timer"
    _attr_unique_id = "v2c_trydan_sensor_timer"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("timer")
        return None
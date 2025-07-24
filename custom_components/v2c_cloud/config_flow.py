"""Config flow for V2C Cloud integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
)
from .v2c_api import V2CCloudAPI

_LOGGER = logging.getLogger(__name__)


class V2CCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for V2C Cloud."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate the API token and device ID
                session = async_get_clientsession(self.hass)
                api = V2CCloudAPI(
                    session=session,
                    api_token=user_input[CONF_API_TOKEN],
                    device_id=user_input[CONF_DEVICE_ID],
                )
                
                # Test connection
                device_info = await api.get_device_info()
                if not device_info:
                    errors["base"] = "invalid_device"
                else:
                    # Check if already configured
                    await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME, DEFAULT_NAME),
                        data=user_input,
                    )
                    
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except TimeoutError:
                errors["base"] = "timeout"
            except Exception as ex:
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"

        # Schema for configuration
        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=30, max=300)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Handle reauthorization."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reauthorization confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Test new token
                session = async_get_clientsession(self.hass)
                api = V2CCloudAPI(
                    session=session,
                    api_token=user_input[CONF_API_TOKEN],
                    device_id=self.reauth_entry.data[CONF_DEVICE_ID],
                )
                
                device_info = await api.get_device_info()
                if device_info:
                    # Update the entry
                    new_data = {**self.reauth_entry.data}
                    new_data[CONF_API_TOKEN] = user_input[CONF_API_TOKEN]
                    
                    self.hass.config_entries.async_update_entry(
                        self.reauth_entry, data=new_data
                    )
                    
                    return self.async_abort(reason="reauth_successful")
                else:
                    errors["base"] = "invalid_auth"
                    
            except Exception as ex:
                _LOGGER.exception("Reauth exception: %s", ex)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_TOKEN): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> V2CCloudOptionsFlowHandler:
        """Get the options flow for this handler."""
        return V2CCloudOptionsFlowHandler(config_entry)


class V2CCloudOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle V2C Cloud options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=300)),
                vol.Optional(
                    "enable_debug",
                    default=self.config_entry.options.get("enable_debug", False),
                ): bool,
                vol.Optional(
                    "power_detection_threshold",
                    default=self.config_entry.options.get("power_detection_threshold", 100),
                ): vol.All(vol.Coerce(int), vol.Range(min=50, max=1000)),
                vol.Optional(
                    "connection_timeout",
                    default=self.config_entry.options.get("connection_timeout", 10),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=30)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )
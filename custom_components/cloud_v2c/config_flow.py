"""Config flow for V2C Cloud integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_TOKEN, CONF_DEVICE_ID
from .v2c_api import V2CCloudAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
        vol.Required(CONF_DEVICE_ID): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    api = V2CCloudAPI(
        token=data[CONF_TOKEN],
        device_id=data[CONF_DEVICE_ID]
    )
    
    try:
        # Test the connection by getting device info
        device_info = await api.get_device_info()
        
        # Return info that you want to store in the config entry.
        return {
            "title": f"V2C {device_info.get('name', 'Trydan')}",
            "device_name": device_info.get('name', 'V2C Trydan'),
            "serial_number": device_info.get('serial_number', 'Unknown')
        }
    except Exception as err:
        _LOGGER.error("Error validating input: %s", err)
        raise CannotConnect from err
    finally:
        await api.close()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for V2C Cloud."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", 
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "url_token": "https://v2c.cloud (sección API)",
                    "url_docs": "https://v2c.docs.apiary.io/"
                }
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Create a unique ID for this integration instance
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors,
            description_placeholders={
                "url_token": "https://v2c.cloud (sección API)",
                "url_docs": "https://v2c.docs.apiary.io/"
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
"""V2C Cloud API client - Based on official Swagger documentation."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp
import async_timeout

from .const import API_BASE_URL, API_TIMEOUT, API_RETRIES

_LOGGER = logging.getLogger(__name__)


class V2CCloudAPI:
    """V2C Cloud API client using official Swagger endpoints."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_token: str,
        device_id: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._api_token = api_token
        self._device_id = device_id
        # CORRECT: apikey header as per Swagger documentation
        self._headers = {
            "apikey": api_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "HomeAssistant/V2C-Cloud-Integration",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Make a request to the V2C Cloud API."""
        url = f"{API_BASE_URL}{endpoint}"
        
        _LOGGER.debug("Making %s request to %s", method, url)
        _LOGGER.debug("Params: %s", params)
        
        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with self._session.request(
                    method, url, headers=self._headers, params=params, json=data
                ) as response:
                    _LOGGER.debug("Response status: %s", response.status)
                    
                    # Get response text first
                    response_text = await response.text()
                    _LOGGER.debug("Response text (first 300 chars): %s", response_text[:300])
                    
                    if response.status == 200:
                        # V2C API sometimes returns plain text, sometimes JSON
                        content_type = response.headers.get('content-type', '')
                        _LOGGER.debug("Content-Type: %s", content_type)
                        
                        if 'json' in content_type:
                            try:
                                response_data = json.loads(response_text)
                                return response_data
                            except json.JSONDecodeError:
                                # If JSON parsing fails, return as text
                                return {"response": response_text}
                        else:
                            # V2C often returns plain text responses
                            return {"response": response_text, "status": "success"}
                    else:
                        _LOGGER.error("Request failed with status %s: %s", response.status, response_text[:300])
                        return None
                        
        except Exception as err:
            _LOGGER.error("Request error: %s", err)
            return None

    async def get_device_info(self) -> dict[str, Any] | None:
        """Get device information using /pairings/me endpoint."""
        # First check if device exists in our pairings
        endpoint = "/pairings/me"
        response = await self._request("GET", endpoint)
        
        if response and isinstance(response, list):
            # Find our device in the pairings list
            for device in response:
                if device.get("deviceId") == self._device_id:
                    _LOGGER.debug("Found device in pairings: %s", device)
                    return device
        elif response and "response" in response:
            # If it's a text response, try to parse it
            _LOGGER.debug("Got text response for pairings: %s", response["response"])
            return {"status": "connected", "deviceId": self._device_id}
        
        return None

    async def get_device_status(self) -> dict[str, Any] | None:
        """Get current device status using /device/reported endpoint."""
        # CORRECT: Use /device/reported to get all device values
        endpoint = "/device/reported"
        params = {"deviceId": self._device_id}
        response = await self._request("GET", endpoint, params=params)
        
        if response:
            _LOGGER.debug("Raw device status response: %s", response)
            
            # Parse the response - V2C returns different formats
            if isinstance(response, dict) and "response" in response:
                # Try to parse the text response
                response_text = response["response"]
                
                # V2C often returns key-value pairs in text format
                # Example: "intensity:16,dynamic:1,connected:1,state:2"
                parsed_data = {}
                if ":" in response_text:
                    try:
                        # Parse comma-separated key:value pairs
                        pairs = response_text.split(",")
                        for pair in pairs:
                            if ":" in pair:
                                key, value = pair.split(":", 1)
                                parsed_data[key.strip()] = value.strip()
                    except Exception as e:
                        _LOGGER.debug("Could not parse response text: %s", e)
                        parsed_data = {"raw_response": response_text}
                else:
                    parsed_data = {"raw_response": response_text}
                
                # Transform to expected format for EMHASS compatibility
                return {
                    "charge_power": self._safe_int(parsed_data.get("power", "0")),
                    "charge_energy": self._safe_int(parsed_data.get("energy", "0")),
                    "charge_state": self._safe_int(parsed_data.get("state", "99")),
                    "charge_current": self._safe_int(parsed_data.get("intensity", "0")),
                    "voltage": self._safe_int(parsed_data.get("voltage", "230")),
                    "temperature": self._safe_int(parsed_data.get("temperature", "0")),
                    "session_energy": self._safe_int(parsed_data.get("session_energy", "0")),
                    "session_time": self._safe_int(parsed_data.get("session_time", "0")),
                    "total_energy": self._safe_int(parsed_data.get("total_energy", "0")),
                    "wifi_signal": self._safe_int(parsed_data.get("wifi_signal", "-50")),
                    "firmware_version": parsed_data.get("firmware", "Unknown"),
                    "intensity": self._safe_int(parsed_data.get("intensity", "6")),
                    "max_intensity": self._safe_int(parsed_data.get("max_intensity", "32")),
                    "min_intensity": self._safe_int(parsed_data.get("min_intensity", "6")),
                    "dynamic_power": parsed_data.get("dynamic", "0") == "1",
                    "paused": parsed_data.get("paused", "0") == "1",
                    "locked": parsed_data.get("locked", "0") == "1",
                    "last_updated": "",
                    "raw_data": parsed_data,  # For debugging
                }
            else:
                # If it's already a dict, use it directly
                return response
        
        return None

    def _safe_int(self, value: str) -> int:
        """Safely convert string to int."""
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    async def set_intensity(self, intensity: int) -> bool:
        """Set charging intensity using /device/intensity endpoint."""
        endpoint = "/device/intensity"
        params = {
            "deviceId": self._device_id,
            "value": str(intensity)
        }
        response = await self._request("POST", endpoint, params=params)
        return response is not None

    async def start_charging(self) -> bool:
        """Start charging using /device/startcharge endpoint."""
        endpoint = "/device/startcharge"
        params = {"deviceId": self._device_id}
        response = await self._request("POST", endpoint, params=params)
        return response is not None

    async def stop_charging(self) -> bool:
        """Stop charging using /device/pausecharge endpoint."""
        endpoint = "/device/pausecharge"
        params = {"deviceId": self._device_id}
        response = await self._request("POST", endpoint, params=params)
        return response is not None

    async def set_dynamic_power(self, enabled: bool) -> bool:
        """Enable/disable dynamic power using /device/dynamic endpoint."""
        endpoint = "/device/dynamic"
        params = {
            "deviceId": self._device_id,
            "value": "1" if enabled else "0"
        }
        response = await self._request("POST", endpoint, params=params)
        return response is not None

    async def set_paused(self, paused: bool) -> bool:
        """Pause/unpause charging using /device/pausecharge endpoint."""
        endpoint = "/device/pausecharge"
        params = {"deviceId": self._device_id}
        # Note: V2C pausecharge appears to toggle, not set specific state
        response = await self._request("POST", endpoint, params=params)
        return response is not None

    async def set_locked(self, locked: bool) -> bool:
        """Lock/unlock charger using /device/locked endpoint."""
        endpoint = "/device/locked"
        params = {
            "deviceId": self._device_id,
            "value": "1" if locked else "0"
        }
        response = await self._request("POST", endpoint, params=params)
        return response is not None

    async def restart_device(self) -> bool:
        """Restart the device using /device/reboot endpoint."""
        endpoint = "/device/reboot"
        params = {"deviceId": self._device_id}
        response = await self._request("POST", endpoint, params=params)
        return response is not None

    async def reset_session(self) -> bool:
        """Reset current session - V2C doesn't have a direct endpoint for this."""
        # V2C doesn't appear to have a session reset endpoint in the Swagger
        # This might need to be implemented differently or might not be available
        _LOGGER.warning("Session reset not available in V2C API")
        return False
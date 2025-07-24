"""V2C Cloud API client with Kong Gateway support."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from .const import API_BASE_URL, API_TIMEOUT, API_RETRIES

_LOGGER = logging.getLogger(__name__)


class V2CCloudAPI:
    """V2C Cloud API client using Kong Gateway."""

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
        self._headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "HomeAssistant/V2C-Cloud-Integration",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Make a request to the V2C Cloud API via Kong Gateway."""
        url = f"{API_BASE_URL}{endpoint}"
        
        _LOGGER.debug("Making %s request to %s", method, url)
        
        for attempt in range(API_RETRIES):
            try:
                async with async_timeout.timeout(API_TIMEOUT):
                    async with self._session.request(
                        method, url, headers=self._headers, json=data
                    ) as response:
                        _LOGGER.debug("Response status: %s", response.status)
                        
                        if response.status == 200:
                            response_data = await response.json()
                            return response_data
                        elif response.status == 401:
                            _LOGGER.error("Authentication failed - invalid token")
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=401,
                                message="Invalid API token",
                            )
                        elif response.status == 404:
                            _LOGGER.error("Device not found: %s", self._device_id)
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=404,
                                message="Device not found",
                            )
                        elif response.status == 429:
                            _LOGGER.warning("Rate limit exceeded, attempt %s", attempt + 1)
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        else:
                            response_text = await response.text()
                            _LOGGER.warning(
                                "API request failed with status %s: %s", 
                                response.status, response_text
                            )
                            
            except asyncio.TimeoutError:
                _LOGGER.warning("Timeout on attempt %s", attempt + 1)
                if attempt == API_RETRIES - 1:
                    raise
                await asyncio.sleep(1 * (attempt + 1))
            except aiohttp.ClientError as err:
                _LOGGER.error("Client error: %s", err)
                if attempt == API_RETRIES - 1:
                    raise
                await asyncio.sleep(1 * (attempt + 1))

        return None

    async def get_device_info(self) -> dict[str, Any] | None:
        """Get device information."""
        endpoint = f"/devices/{self._device_id}"
        return await self._request("GET", endpoint)

    async def get_device_status(self) -> dict[str, Any] | None:
        """Get current device status."""
        endpoint = f"/devices/{self._device_id}/status"
        response = await self._request("GET", endpoint)
        
        if response:
            # Transform API response to expected format for EMHASS compatibility
            return {
                # CRITICAL: Names must match EMHASS expectations
                "charge_power": response.get("ev_power", 0),          # EV charging power
                "charge_energy": response.get("ev_energy", 0),        # EV energy (Wh)
                "charge_state": response.get("status", 99),           # Connection state
                "charge_current": response.get("current", 0),         # Charging current
                "voltage": response.get("voltage", 230),              # Voltage
                "temperature": response.get("temperature", 0),        # Temperature
                "session_energy": response.get("session_energy", 0),  # Session energy
                "session_time": response.get("session_time", 0),      # Session time
                "total_energy": response.get("total_energy", 0),      # Total energy
                "wifi_signal": response.get("wifi_rssi", -50),        # WiFi signal
                "firmware_version": response.get("fw_version", "Unknown"), # Firmware
                "intensity": response.get("max_current", 6),          # Current intensity
                "max_intensity": response.get("max_current_limit", 32), # Max current
                "min_intensity": response.get("min_current_limit", 6),  # Min current
                "dynamic_power": response.get("dynamic_enabled", False), # Dynamic mode
                "paused": response.get("charge_paused", False),       # Paused state
                "locked": response.get("locked", False),              # Locked state
                "last_updated": response.get("timestamp", ""),       # Last update
            }
        
        return None

    async def set_intensity(self, intensity: int) -> bool:
        """Set charging intensity."""
        endpoint = f"/devices/{self._device_id}/current"
        data = {"current": intensity}
        response = await self._request("POST", endpoint, data)
        return response is not None

    async def start_charging(self) -> bool:
        """Start charging."""
        endpoint = f"/devices/{self._device_id}/start"
        response = await self._request("POST", endpoint)
        return response is not None

    async def stop_charging(self) -> bool:
        """Stop charging."""
        endpoint = f"/devices/{self._device_id}/stop"
        response = await self._request("POST", endpoint)
        return response is not None

    async def set_dynamic_power(self, enabled: bool) -> bool:
        """Enable/disable dynamic power control."""
        endpoint = f"/devices/{self._device_id}/dynamic"
        data = {"enabled": enabled}
        response = await self._request("POST", endpoint, data)
        return response is not None

    async def set_paused(self, paused: bool) -> bool:
        """Pause/unpause charging."""
        endpoint = f"/devices/{self._device_id}/pause"
        data = {"paused": paused}
        response = await self._request("POST", endpoint, data)
        return response is not None

    async def set_locked(self, locked: bool) -> bool:
        """Lock/unlock charger."""
        endpoint = f"/devices/{self._device_id}/lock"
        data = {"locked": locked}
        response = await self._request("POST", endpoint, data)
        return response is not None

    async def restart_device(self) -> bool:
        """Restart the device."""
        endpoint = f"/devices/{self._device_id}/restart"
        response = await self._request("POST", endpoint)
        return response is not None

    async def reset_session(self) -> bool:
        """Reset current session."""
        endpoint = f"/devices/{self._device_id}/session/reset"
        response = await self._request("POST", endpoint)
        return response is not None
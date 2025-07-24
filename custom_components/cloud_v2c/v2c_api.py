"""API client for V2C Cloud services."""
from __future__ import annotations

import aiohttp
import asyncio
import logging
from typing import Any, Dict

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class V2CCloudAPI:
    """V2C Cloud API client."""

    def __init__(self, token: str, device_id: str) -> None:
        """Initialize the API client."""
        self.token = token
        self.device_id = device_id
        self.base_url = API_BASE_URL
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make a request to the V2C Cloud API."""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        try:
            async with session.request(
                method, url, headers=headers, json=data, timeout=30
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error making request to %s: %s", url, err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error making request to %s: %s", url, err)
            raise

    async def get_device_status(self) -> dict:
        """Get the current status of the V2C device."""
        try:
            # Endpoint basado en la documentación típica de APIs de cargadores
            response = await self._make_request("GET", f"/devices/{self.device_id}/status")
            return response.get("data", response)
        except Exception as err:
            _LOGGER.error("Error getting device status: %s", err)
            raise

    async def get_device_info(self) -> dict:
        """Get device information."""
        try:
            response = await self._make_request("GET", f"/devices/{self.device_id}")
            return response.get("data", response)
        except Exception as err:
            _LOGGER.error("Error getting device info: %s", err)
            raise

    async def set_charge_current(self, current: int) -> bool:
        """Set the charging current in Amperes."""
        try:
            data = {"current": current}
            await self._make_request("POST", f"/devices/{self.device_id}/set_current", data)
            return True
        except Exception as err:
            _LOGGER.error("Error setting charge current: %s", err)
            return False

    async def set_max_current(self, max_current: int) -> bool:
        """Set the maximum charging current in Amperes."""
        try:
            data = {"max_current": max_current}
            await self._make_request("POST", f"/devices/{self.device_id}/set_max_current", data)
            return True
        except Exception as err:
            _LOGGER.error("Error setting max current: %s", err)
            return False

    async def set_min_current(self, min_current: int) -> bool:
        """Set the minimum charging current in Amperes."""
        try:
            data = {"min_current": min_current}
            await self._make_request("POST", f"/devices/{self.device_id}/set_min_current", data)
            return True
        except Exception as err:
            _LOGGER.error("Error setting min current: %s", err)
            return False

    async def set_dynamic_power(self, enabled: bool) -> bool:
        """Enable or disable dynamic power control."""
        try:
            data = {"dynamic_enabled": enabled}
            await self._make_request("POST", f"/devices/{self.device_id}/set_dynamic", data)
            return True
        except Exception as err:
            _LOGGER.error("Error setting dynamic power: %s", err)
            return False

    async def set_pause_charge(self, paused: bool) -> bool:
        """Pause or resume charging."""
        try:
            data = {"paused": paused}
            await self._make_request("POST", f"/devices/{self.device_id}/set_pause", data)
            return True
        except Exception as err:
            _LOGGER.error("Error setting pause charge: %s", err)
            return False

    async def set_lock_charger(self, locked: bool) -> bool:
        """Lock or unlock the charger."""
        try:
            data = {"locked": locked}
            await self._make_request("POST", f"/devices/{self.device_id}/set_lock", data)
            return True
        except Exception as err:
            _LOGGER.error("Error setting lock charger: %s", err)
            return False

    async def set_km_to_charge(self, km: int) -> bool:
        """Set the kilometers to charge."""
        try:
            data = {"km_to_charge": km}
            await self._make_request("POST", f"/devices/{self.device_id}/set_km", data)
            return True
        except Exception as err:
            _LOGGER.error("Error setting km to charge: %s", err)
            return False

    async def start_charge(self) -> bool:
        """Start charging."""
        try:
            await self._make_request("POST", f"/devices/{self.device_id}/start_charge")
            return True
        except Exception as err:
            _LOGGER.error("Error starting charge: %s", err)
            return False

    async def stop_charge(self) -> bool:
        """Stop charging."""
        try:
            await self._make_request("POST", f"/devices/{self.device_id}/stop_charge")
            return True
        except Exception as err:
            _LOGGER.error("Error stopping charge: %s", err)
            return False
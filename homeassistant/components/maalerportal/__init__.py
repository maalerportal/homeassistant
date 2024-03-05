"""The Målerportal integration."""
from __future__ import annotations

import logging
import re

from mpsmarthome import ApiClient, Configuration, HomeAssistantApi, MetersResponse

from homeassistant.components.recorder.statistics import get_instance
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Målerportal from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    api_key: str = entry.data["api_key"]
    api_config = Configuration(host="http://gateway-smarthome:8080")
    api_client = ApiClient(api_config)
    api_client.default_headers["X-API-KEY"] = api_key
    hassapi = HomeAssistantApi(api_client)
    hass.data[DOMAIN][entry.entry_id] = hassapi
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        recorder = get_instance(hass)
        meters: list[MetersResponse] = entry.data["meters"]
        for m in meters:
            if isinstance(m, dict):
                m = MetersResponse(**m)
            if m.identifier is None or m.address is None or m.address_meter_id is None:
                continue
            recorder.async_clear_statistics(
                [
                    f"sensor.{to_snake_case(m.identifier + m.address + m.address_meter_id)}"
                ]
            )

    return unload_ok


def to_snake_case(s: str) -> str:
    """Convert a string to snake_case."""
    # Replace special characters with " "
    s = re.sub("[^a-zA-Z0-9]", " ", s)
    # Replace capital letters with space + letter to handle camelCase
    s = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", s)
    # For the case where there are no spaces between camelCase letters
    s = re.sub("([a-z0-9])([A-Z])", r"\1 \2", s)
    # Convert to lower case and replace spaces with underscores
    return s.lower().replace(" ", "_")

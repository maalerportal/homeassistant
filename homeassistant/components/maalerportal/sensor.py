"""Platform for Målerportal sensor integration."""

import logging

from mpsmarthome import HomeAssistantApi, MetersResponse

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""

    meters: list[MetersResponse] = config.data["meters"]
    hassapi: HomeAssistantApi = hass.data[DOMAIN][config.entry_id]
    sensors = []

    for m in meters:
        if isinstance(m, dict):
            m = MetersResponse(**m)
        sensors.append(MaalerportalStatisticSensor(m, hassapi))

    async_add_entities(sensors)


class MaalerportalStatisticSensor(SensorEntity):
    """Handles water meter statistics."""

    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, meter: MetersResponse, api: HomeAssistantApi) -> None:
        """Set up the meter."""

        self._meter = meter
        self._attr_name = f"{self._meter.identifier} {self._meter.address} {self._meter.meter_counter_type}"
        self._attr_unique_id = f"{meter.identifier}-statistics"
        self._api = api

    async def async_update(self) -> None:
        """Continually update history."""

        # await asyncio.sleep(randint(0, 10) / 10)
        # print(f"{datetime.now()} - Update {self._attr_name}")

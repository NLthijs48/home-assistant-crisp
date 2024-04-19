"""Sensor platform for Crisp."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import DOMAIN, SENSOR_TOTAL_ORDER_COUNT
from .coordinator import CrispDataUpdateCoordinator
from .entity import CrispEntity

ENTITY_DESCRIPTIONS = (
    # TODO: translation_key?
    SensorEntityDescription(
        key=SENSOR_TOTAL_ORDER_COUNT,
        name="Total order count",
        icon="mdi:sigma",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        CrispSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class CrispSensor(CrispEntity, SensorEntity):
    """Crisp Sensor class."""

    def __init__(
        self,
        coordinator: CrispDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self):
        """Return the native value of the sensor."""

        return self.coordinator.data.get("count")

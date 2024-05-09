"""Sensor platform for Crisp."""

from __future__ import annotations
from collections.abc import Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, SENSOR_NEXT_ORDER_PRODUCT_COUNT, SENSOR_ORDER_COUNT_OPEN, SENSOR_ORDER_COUNT_TOTAL
from .coordinator import CrispData, CrispDataUpdateCoordinator
from .entity import CrispEntity
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class CrispSensorEntityDescription(SensorEntityDescription):
    """Describes Crisp sensor entity."""

    get_value: Callable[[CrispData], StateType]


SENSOR_TYPES: tuple[CrispSensorEntityDescription, ...] = (
    CrispSensorEntityDescription(
        key=SENSOR_ORDER_COUNT_TOTAL,
        name="Order count total",
        icon="mdi:sigma",
        get_value=lambda data: data['order_count_total'],
    ),
    CrispSensorEntityDescription(
        key=SENSOR_ORDER_COUNT_OPEN,
        name="Order count open",
        icon="mdi:receipt-clock-outline",
        get_value=lambda data: data['order_count_open'],
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_PRODUCT_COUNT,
        name="Next order product count",
        icon="mdi:food-croissant",
        get_value=lambda data: data['next_order_product_count'],
    ),
)

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([
        CrispSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in SENSOR_TYPES
    ])

class CrispSensor(CrispEntity, SensorEntity):
    """Crisp Sensor class."""

    def __init__(
        self,
        coordinator: CrispDataUpdateCoordinator,
        entity_description: CrispSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.unique_id}.{entity_description.key}"
        self.entity_description = entity_description

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        return self.entity_description.get_value(self.coordinator.data)

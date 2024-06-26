"""Sensor platform for Crisp."""

from __future__ import annotations
from collections.abc import Callable

from datetime import date, time

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, SENSOR_NEXT_ORDER_DELIVERY_END, SENSOR_NEXT_ORDER_DELIVERY_END_TIME, SENSOR_NEXT_ORDER_DELIVERY_START, SENSOR_NEXT_ORDER_DELIVERY_START_TIME, SENSOR_NEXT_ORDER_PRODUCT_COUNT, SENSOR_ORDER_COUNT_OPEN, SENSOR_ORDER_COUNT_TOTAL, SENSOR_NEXT_ORDER_DELIVERY_ON
from .coordinator import CrispData, CrispDataUpdateCoordinator
from .entity import CrispEntity
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class CrispSensorEntityDescription(SensorEntityDescription):
    """Describes Crisp sensor entity."""

    get_value: Callable[[CrispData], StateType | date | time]


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
        get_value=lambda data: None if data["next_order"] is None else data['next_order'].get('product_count'),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_ON,
        name="Next order delivery on",
        icon="mdi:calendar",
        get_value=lambda data: None if data["next_order"] is None else data['next_order'].get('delivery_on'),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_START,
        name="Next order delivery start",
        icon="mdi:clock-start",
        get_value=lambda data: None if data["next_order"] is None else data['next_order'].get('delivery_start'),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_START_TIME,
        name="Next order delivery start time",
        icon="mdi:clock-start",
        get_value=lambda data: None if data["next_order"] is None else data['next_order'].get('delivery_start_time'),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_END,
        name="Next order delivery end",
        icon="mdi:clock-end",
        get_value=lambda data: None if data["next_order"] is None else data['next_order'].get('delivery_end'),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_END_TIME,
        name="Next order delivery end time",
        icon="mdi:clock-end",
        get_value=lambda data: None if data["next_order"] is None else data['next_order'].get('delivery_end_time'),
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
    def native_value(self):
        """Return the value reported by the sensor."""
        return self.entity_description.get_value(self.coordinator.data)

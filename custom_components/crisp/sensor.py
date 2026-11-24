"""Sensor platform for Crisp."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import CrispConfigEntry
from .const import (
    DEVICE_NEXT_ORDER,
    SENSOR_NEXT_ORDER_DELIVERY_END,
    SENSOR_NEXT_ORDER_DELIVERY_EXPECTED,
    SENSOR_NEXT_ORDER_DELIVERY_ON,
    SENSOR_NEXT_ORDER_DELIVERY_START,
    SENSOR_NEXT_ORDER_DRIVER_NAME,
    SENSOR_NEXT_ORDER_MEALKIT_COUNT,
    SENSOR_NEXT_ORDER_PRODUCT_COUNT,
    SENSOR_NEXT_ORDER_RECIPE_COUNT,
    SENSOR_NEXT_ORDER_USER_RECIPE_COUNT,
    SENSOR_ORDER_COUNT_OPEN,
    SENSOR_ORDER_COUNT_TOTAL,
)
from .coordinator import CrispData, CrispDataUpdateCoordinator
from .entity import CrispEntity, async_register_devices


@dataclass(frozen=True, kw_only=True)
class CrispSensorEntityDescription(SensorEntityDescription):
    """Describes Crisp sensor entity."""

    get_value: Callable[[CrispData], StateType | date | datetime]
    next_order: bool = False
    # Unavailable (instead of unknown) while there is no value, e.g. no tracking
    unavailable_without_value: bool = False


SENSOR_TYPES: tuple[CrispSensorEntityDescription, ...] = (
    CrispSensorEntityDescription(
        key=SENSOR_ORDER_COUNT_TOTAL,
        name="Order count total",
        icon="mdi:sigma",
        get_value=lambda data: data["order_count_total"],
    ),
    CrispSensorEntityDescription(
        key=SENSOR_ORDER_COUNT_OPEN,
        name="Order count open",
        icon="mdi:receipt-clock-outline",
        get_value=lambda data: data["order_count_open"],
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_PRODUCT_COUNT,
        name="Product count",
        next_order=True,
        icon="mdi:food-croissant",
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("product_count")
        ),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_RECIPE_COUNT,
        name="Recipe count",
        next_order=True,
        icon="mdi:chef-hat",
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("recipe_count")
        ),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_USER_RECIPE_COUNT,
        name="User recipe count",
        next_order=True,
        icon="mdi:chef-hat",
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("user_recipe_count")
        ),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_MEALKIT_COUNT,
        name="Mealkit count",
        next_order=True,
        icon="mdi:food-variant",
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("mealkit_count")
        ),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_ON,
        name="Delivery on",
        next_order=True,
        icon="mdi:calendar",
        device_class=SensorDeviceClass.DATE,
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("delivery_on")
        ),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_START,
        name="Delivery start",
        next_order=True,
        icon="mdi:clock-start",
        device_class=SensorDeviceClass.TIMESTAMP,
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("delivery_start")
        ),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_END,
        name="Delivery end",
        next_order=True,
        icon="mdi:clock-end",
        device_class=SensorDeviceClass.TIMESTAMP,
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("delivery_end")
        ),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DELIVERY_EXPECTED,
        name="Delivery expected",
        next_order=True,
        unavailable_without_value=True,
        icon="mdi:truck-fast",
        device_class=SensorDeviceClass.TIMESTAMP,
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("delivery_expected")
        ),
    ),
    CrispSensorEntityDescription(
        key=SENSOR_NEXT_ORDER_DRIVER_NAME,
        name="Driver name",
        next_order=True,
        unavailable_without_value=True,
        icon="mdi:account-hard-hat",
        get_value=lambda data: (
            None
            if data["next_order"] is None
            else data["next_order"].get("driver_name")
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CrispConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data
    async_register_devices(hass, entry)
    async_add_devices(
        [
            CrispSensor(
                coordinator=coordinator,
                entity_description=entity_description,
            )
            for entity_description in SENSOR_TYPES
        ]
    )


class CrispSensor(CrispEntity, SensorEntity):
    """Crisp Sensor class."""

    def __init__(
        self,
        coordinator: CrispDataUpdateCoordinator,
        entity_description: CrispSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(
            coordinator,
            sub_device=DEVICE_NEXT_ORDER if entity_description.next_order else None,
        )
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}.{entity_description.key}"
        )
        self.entity_description = entity_description

    @property
    def available(self) -> bool:
        """Next order sensors are unavailable without an open order."""
        if not super().available:
            return False
        if (
            self.entity_description.next_order
            and (self.coordinator.data or {}).get("next_order") is None
        ):
            return False
        if self.entity_description.unavailable_without_value:
            return self.native_value is not None
        return True

    @property
    def native_value(self) -> StateType | date | datetime:
        """Return the value reported by the sensor."""
        return self.entity_description.get_value(self.coordinator.data)

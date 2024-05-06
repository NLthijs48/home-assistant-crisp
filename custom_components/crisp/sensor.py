"""Sensor platform for Crisp."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import DOMAIN, ORDER_COUNT_OPEN_KEY, ORDER_COUNT_TOTAL_KEY, SENSOR_ORDER_COUNT_OPEN, SENSOR_ORDER_COUNT_TOTAL
from .coordinator import CrispDataUpdateCoordinator
from .entity import CrispEntity

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([
        OrderCountTotalSensor(coordinator=coordinator),
        OrderCountOpenSensor(coordinator=coordinator)
    ])


class CrispSensor(CrispEntity, SensorEntity):
    """Crisp Sensor class."""

    def __init__(
        self,
        coordinator: CrispDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.unique_id}.{entity_description.key}"
        self.entity_description = entity_description


class OrderCountTotalSensor(CrispSensor):
    """Order count total sensor."""

    def __init__(self, coordinator: CrispDataUpdateCoordinator) -> None:
        """Init."""
        super().__init__(coordinator, SensorEntityDescription(
            key=SENSOR_ORDER_COUNT_TOTAL,
            name="Order count total",
            icon="mdi:sigma",
        )
    )

    @property
    def native_value(self):
        """Value."""
        return self.coordinator.data.get(ORDER_COUNT_TOTAL_KEY)


class OrderCountOpenSensor(CrispSensor):
    """Order count open sensor."""

    def __init__(self, coordinator: CrispDataUpdateCoordinator) -> None:
        """Init."""
        super().__init__(coordinator, SensorEntityDescription(
            key=SENSOR_ORDER_COUNT_OPEN,
            name="Order count open",
            icon="mdi:receipt-clock-outline",
        )
    )

    @property
    def native_value(self):
        """Value."""
        return self.coordinator.data.get(ORDER_COUNT_OPEN_KEY)

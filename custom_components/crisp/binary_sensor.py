"""Binary sensor platform for Crisp."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CrispConfigEntry
from .const import BINARY_SENSOR_NEXT_ORDER_CONTAINS_ALCOHOL, DEVICE_NEXT_ORDER
from .coordinator import CrispDataUpdateCoordinator, CrispUpcomingOrderData
from .entity import CrispEntity, async_register_devices

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CrispConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    async_register_devices(hass, entry)
    async_add_devices([CrispContainsAlcoholSensor(entry.runtime_data)])


class CrispContainsAlcoholSensor(CrispEntity, BinarySensorEntity):
    """Whether the next order contains alcohol."""

    _attr_name = "Contains alcohol"
    _attr_icon = "mdi:glass-wine"

    def __init__(self, coordinator: CrispDataUpdateCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, sub_device=DEVICE_NEXT_ORDER)
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}"
            f".{BINARY_SENSOR_NEXT_ORDER_CONTAINS_ALCOHOL}"
        )

    def _next_order(self) -> CrispUpcomingOrderData | None:
        return (self.coordinator.data or {}).get("next_order")

    @property
    def available(self) -> bool:
        """Unavailable while there is no track & trace data."""
        order = self._next_order()
        return (
            super().available
            and order is not None
            and order["contains_alcohol"] is not None
        )

    @property
    def is_on(self) -> bool | None:
        """Return true when the order contains alcohol."""
        order = self._next_order()
        return None if order is None else order["contains_alcohol"]

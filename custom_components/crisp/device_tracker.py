"""Device tracker platform for Crisp."""

from __future__ import annotations

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CrispConfigEntry
from .const import DEVICE_NEXT_ORDER, TRACKER_NEXT_ORDER_DRIVER
from .coordinator import CrispDataUpdateCoordinator
from .entity import CrispEntity, async_register_devices


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CrispConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the device tracker platform."""
    async_register_devices(hass, entry)
    async_add_devices([CrispDriverTracker(entry.runtime_data)])


class CrispDriverTracker(CrispEntity, TrackerEntity):
    """Tracks the location of the delivery driver."""

    _attr_name = "Driver"
    _attr_icon = "mdi:truck-delivery"

    def __init__(self, coordinator: CrispDataUpdateCoordinator) -> None:
        """Initialize the tracker."""
        super().__init__(coordinator, sub_device=DEVICE_NEXT_ORDER)
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}.{TRACKER_NEXT_ORDER_DRIVER}"
        )

    def _next_order(self):
        return (self.coordinator.data or {}).get("next_order")

    @property
    def available(self) -> bool:
        """Unavailable while there is no driver position."""
        order = self._next_order()
        return (
            super().available
            and order is not None
            and order.get("driver_latitude") is not None
            and order.get("driver_longitude") is not None
        )

    @property
    def latitude(self) -> float | None:
        """Return the latitude of the driver."""
        order = self._next_order()
        return None if order is None else order.get("driver_latitude")

    @property
    def longitude(self) -> float | None:
        """Return the longitude of the driver."""
        order = self._next_order()
        return None if order is None else order.get("driver_longitude")

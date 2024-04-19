"""CrispEntity class."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION, ATTRIBUTION
from .coordinator import CrispDataUpdateCoordinator


class CrispEntity(CoordinatorEntity):
    """Crisp entity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: CrispDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)

        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            manufacturer=NAME,
        )

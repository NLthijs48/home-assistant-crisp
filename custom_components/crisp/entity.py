"""CrispEntity class."""

from __future__ import annotations

from homeassistant.const import CONF_COUNTRY_CODE
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import CrispCountry
from .const import ATTRIBUTION, DOMAIN, NAME
from .coordinator import CrispDataUpdateCoordinator


class CrispEntity(CoordinatorEntity[CrispDataUpdateCoordinator]):
    """Crisp entity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: CrispDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)

        country = CrispCountry(coordinator.config_entry.data[CONF_COUNTRY_CODE])

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.unique_id)},
            entry_type=DeviceEntryType.SERVICE,
            name=NAME,
            manufacturer=NAME,
            configuration_url=country.configuration_url,
        )

"""CrispEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, ATTRIBUTION
from .coordinator import CrispDataUpdateCoordinator
from homeassistant.const import CONF_COUNTRY_CODE


class CrispEntity(CoordinatorEntity[CrispDataUpdateCoordinator]):
    """Crisp entity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: CrispDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)

        country = coordinator.config_entry.data[CONF_COUNTRY_CODE]
        configuration_url = {
            'nl': 'https://crisp.nl/app',
            'be': 'https://crisp.app/app',
        }.get(country)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            manufacturer=NAME,
            configuration_url=configuration_url
        )

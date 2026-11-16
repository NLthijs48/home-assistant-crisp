"""CrispEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_COUNTRY_CODE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import CrispCountry
from .const import (
    ATTRIBUTION,
    DEVICE_ACCOUNT_NAME,
    DEVICE_NEXT_ORDER,
    DEVICE_NEXT_ORDER_NAME,
    DOMAIN,
    NAME,
)
from .coordinator import CrispDataUpdateCoordinator

if TYPE_CHECKING:
    from . import CrispConfigEntry


def async_register_devices(hass: HomeAssistant, entry: CrispConfigEntry) -> None:
    """Register the account device and the linked next order device."""
    unique_id = entry.unique_id or entry.entry_id
    country = CrispCountry(entry.data[CONF_COUNTRY_CODE])
    registry = dr.async_get(hass)

    account = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, unique_id)},
        entry_type=DeviceEntryType.SERVICE,
        name=DEVICE_ACCOUNT_NAME,
        manufacturer=NAME,
        configuration_url=country.configuration_url,
    )
    registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{unique_id}_{DEVICE_NEXT_ORDER}")},
        entry_type=DeviceEntryType.SERVICE,
        name=DEVICE_NEXT_ORDER_NAME,
        manufacturer=NAME,
        via_device_id=account.id,
    )


class CrispEntity(CoordinatorEntity[CrispDataUpdateCoordinator]):
    """Crisp entity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: CrispDataUpdateCoordinator,
        sub_device: str | None = None,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        country = CrispCountry(coordinator.config_entry.data[CONF_COUNTRY_CODE])

        unique_id = (
            coordinator.config_entry.unique_id or coordinator.config_entry.entry_id
        )

        if sub_device == DEVICE_NEXT_ORDER:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{unique_id}_{DEVICE_NEXT_ORDER}")},
                entry_type=DeviceEntryType.SERVICE,
                name=DEVICE_NEXT_ORDER_NAME,
                manufacturer=NAME,
            )
        else:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, unique_id)},
                entry_type=DeviceEntryType.SERVICE,
                name=DEVICE_ACCOUNT_NAME,
                manufacturer=NAME,
                configuration_url=country.configuration_url,
            )

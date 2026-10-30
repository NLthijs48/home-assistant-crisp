"""
Custom integration to integrate Crisp with Home Assistant.

For more details about this integration, please refer to
https://github.com/NLthijs48/home-assistant-crisp
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CrispApiClient
from .const import DOMAIN
from .coordinator import CrispDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

type CrispConfigEntry = ConfigEntry[CrispDataUpdateCoordinator]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: CrispConfigEntry) -> bool:
    """Set up this integration using UI."""
    coordinator = CrispDataUpdateCoordinator(
        hass=hass,
        client=CrispApiClient(
            client_id=entry.data[CONF_TOKEN],
            session=async_get_clientsession(hass),
        ),
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _remove_stale_devices(hass, entry)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


def _remove_stale_devices(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Remove devices of this entry that don't match the current identifier.

    Older versions registered the device with identifier (DOMAIN, None).
    """
    registry = dr.async_get(hass)
    current = (DOMAIN, entry.unique_id)
    for device in dr.async_entries_for_config_entry(registry, entry.entry_id):
        if current not in device.identifiers:
            registry.async_remove_device(device.id)


async def async_unload_entry(hass: HomeAssistant, entry: CrispConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: CrispConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)

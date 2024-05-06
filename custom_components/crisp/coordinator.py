"""DataUpdateCoordinator for crisp."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    CrispApiClient,
    CrispApiClientAuthenticationError,
    CrispApiClientError,
)
from .const import DOMAIN, LOGGER, ORDER_COUNT_OPEN_KEY, ORDER_COUNT_TOTAL_KEY


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class CrispDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: CrispApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=15),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            order_count_data = await self.client.get_order_count()
            open_order_ids = order_count_data.get("openOrderIds") or []
            if (len(open_order_ids) >= 1):
                next_order_id = open_order_ids[0]
                LOGGER.debug("next order id: %s", next_order_id)

            return {
                ORDER_COUNT_TOTAL_KEY: order_count_data['count'],
                ORDER_COUNT_OPEN_KEY: len(open_order_ids)
            }
        except CrispApiClientAuthenticationError as exception:
            # Authentication failed: this will start the reauth flow: SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed(exception) from exception
        except CrispApiClientError as exception:
            raise UpdateFailed(exception) from exception

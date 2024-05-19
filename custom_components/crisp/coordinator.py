"""DataUpdateCoordinator for crisp."""

from __future__ import annotations

from datetime import timedelta, date
from typing import TypedDict

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
from .const import DOMAIN, LOGGER

class CrispData(TypedDict):
    """Class that stores all Crisp data retreived by the Coordinator."""

    order_count_total: int
    order_count_open: int
    next_order: None | CrispUpcomingOrderData

class CrispUpcomingOrderData(TypedDict):
    """Stores data describing an upcoming order."""

    id: int
    product_count: int
    delivery_on: date

# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class CrispDataUpdateCoordinator(DataUpdateCoordinator[CrispData]):
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

            order_count_total = order_count_data['count']
            order_count_open = len(open_order_ids)

            next_order: None | CrispUpcomingOrderData = None
            if (len(open_order_ids) >= 1):
                next_order_id = open_order_ids[0]
                # LOGGER.debug("next order id: %s", next_order_id)
                next_open_order = await self.client.get_order_details(next_order_id)
                # LOGGER.debug(json.dumps(next_open_order.keys(), indent=4))
                next_open_order_data = next_open_order.get('data', {})

                product_count = len(next_open_order_data.get('products'))

                delivery_slot = next_open_order_data.get('deliverySlot', {})
                delivery_on = date.fromisoformat(delivery_slot.get('date'))

                next_order = {
                    'id': next_order_id,
                    'product_count': product_count,
                    'delivery_on': delivery_on,
                }

            result: CrispData = {
                'order_count_total': order_count_total,
                'order_count_open': order_count_open,
                'next_order': next_order
            }
            return result
        except CrispApiClientAuthenticationError as exception:
            # Authentication failed: this will start the reauth flow: SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed(exception) from exception
        except CrispApiClientError as exception:
            raise UpdateFailed(exception) from exception

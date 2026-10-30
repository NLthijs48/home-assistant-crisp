"""DataUpdateCoordinator for crisp."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TypedDict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

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
    next_order: CrispUpcomingOrderData | None


class CrispUpcomingOrderData(TypedDict):
    """Stores data describing an upcoming order."""

    id: int
    product_count: int
    # None for the case it cannot get parsed
    delivery_on: date | None
    # None for the case it cannot get parsed
    delivery_start: datetime | None
    # None for the case it cannot get parsed
    delivery_end: datetime | None


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

    async def _async_update_data(self) -> CrispData:
        """Update data via library."""
        try:
            order_count_data = await self.client.get_order_count()
            open_order_ids = order_count_data.get("openOrderIds") or []

            order_count_total = order_count_data["count"]
            order_count_open = len(open_order_ids)

            next_order: CrispUpcomingOrderData | None = None
            if len(open_order_ids) >= 1:
                next_order_id = open_order_ids[0]
                next_open_order = await self.client.get_order_details(next_order_id)
                next_open_order_data = next_open_order.get("data", {})

                product_count = len(next_open_order_data.get("products"))

                delivery_slot = next_open_order_data.get("deliverySlot", {})

                delivery_on_raw = delivery_slot.get("date")
                delivery_on = (
                    dt_util.parse_date(delivery_on_raw)
                    if delivery_on_raw is not None
                    else None
                )

                # Is it best practice to store in UTC or using as_local in the state?
                delivery_start_raw = delivery_slot.get("tsStart")
                delivery_start = (
                    dt_util.as_local(dt_util.parse_datetime(delivery_start_raw))
                    if delivery_start_raw is not None
                    else None
                )

                delivery_end_raw = delivery_slot.get("tsEnd")
                delivery_end = (
                    dt_util.as_local(dt_util.parse_datetime(delivery_end_raw))
                    if delivery_end_raw is not None
                    else None
                )

                next_order = {
                    "id": next_order_id,
                    "product_count": product_count,
                    "delivery_on": delivery_on,
                    "delivery_start": delivery_start,
                    "delivery_end": delivery_end,
                }

            result: CrispData = {
                "order_count_total": order_count_total,
                "order_count_open": order_count_open,
                "next_order": next_order,
            }
            return result
        except CrispApiClientAuthenticationError as exception:
            # Authentication failed: this will start the reauth flow:
            # (see async_step_reauth)
            raise ConfigEntryAuthFailed(exception) from exception
        except CrispApiClientError as exception:
            raise UpdateFailed(exception) from exception

"""DataUpdateCoordinator for crisp."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, TypedDict
from zoneinfo import ZoneInfo

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
    recipe_count: int
    user_recipe_count: int
    mealkit_count: int
    # None for the case it cannot get parsed
    delivery_on: date | None
    # None for the case it cannot get parsed
    delivery_start: datetime | None
    # None for the case it cannot get parsed
    delivery_end: datetime | None
    # None when no driver position is available
    driver_latitude: float | None
    driver_longitude: float | None
    # None when no track & trace data is available or it cannot get parsed
    estimated_arrival: datetime | None


DEFAULT_UPDATE_INTERVAL = timedelta(minutes=15)
TRACK_TRACE_TIMEZONE = ZoneInfo("Europe/Amsterdam")


def _interval_for_arrival(estimated_arrival: datetime | None) -> timedelta:
    """Determine the polling interval based on the expected arrival."""
    if estimated_arrival is None:
        return DEFAULT_UPDATE_INTERVAL
    remaining = estimated_arrival - dt_util.utcnow()
    if remaining > timedelta(hours=1):
        return DEFAULT_UPDATE_INTERVAL
    if remaining > timedelta(minutes=15):
        return timedelta(minutes=5)
    return timedelta(minutes=1)


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
            update_interval=DEFAULT_UPDATE_INTERVAL,
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

                driver_latitude: float | None = None
                driver_longitude: float | None = None
                estimated_arrival: datetime | None = None
                delivery_link = next_open_order_data.get("deliveryLink")
                if delivery_link:
                    status = await self._get_status(delivery_link)
                    if status is not None and status.get("type") != "delivery":
                        # Delivery finished or changed: reload the order, the
                        # delivery link should be gone now
                        next_open_order = await self.client.get_order_details(
                            next_order_id
                        )
                        next_open_order_data = next_open_order.get("data", {})
                        status = None
                        delivery_link = next_open_order_data.get("deliveryLink")
                        if delivery_link:
                            status = await self._get_status(delivery_link)
                    if status is not None:
                        try:
                            van = status.get("van")
                            if van:
                                driver_latitude = float(van["latitude"])
                                driver_longitude = float(van["longitude"])
                        except (KeyError, TypeError, ValueError):
                            LOGGER.debug("Could not parse van position")
                        estimated_arrival = self._parse_arrival(
                            status.get("estimatedArrivalAt")
                        )

                product_count = len(next_open_order_data.get("products"))

                recipe_count = len(next_open_order_data.get("recipes") or [])
                user_recipe_count = len(next_open_order_data.get("userRecipes") or [])

                mealkit = next_open_order_data.get("mealkit") or {}
                mealkit_count = len(mealkit.get("items") or [])

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
                    "recipe_count": recipe_count,
                    "user_recipe_count": user_recipe_count,
                    "mealkit_count": mealkit_count,
                    "delivery_on": delivery_on,
                    "delivery_start": delivery_start,
                    "delivery_end": delivery_end,
                    "driver_latitude": driver_latitude,
                    "driver_longitude": driver_longitude,
                    "estimated_arrival": estimated_arrival,
                }
                self.update_interval = _interval_for_arrival(estimated_arrival)
            else:
                self.update_interval = DEFAULT_UPDATE_INTERVAL

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

    async def _get_status(self, delivery_link: str) -> dict[str, Any] | None:
        """Fetch track & trace status, None when unavailable."""
        token = delivery_link.rstrip("/").rsplit("/", 1)[-1]
        try:
            status = await self.client.get_track_trace_status(token)
        except CrispApiClientAuthenticationError:
            LOGGER.debug("Track & trace token rejected")
            return None
        except CrispApiClientError:
            LOGGER.debug("Could not fetch track & trace status")
            return None
        return status if isinstance(status, dict) else None

    @staticmethod
    def _parse_arrival(raw: str | None) -> datetime | None:
        """Parse a Dutch local time string like '2026-11-16 16:37:30'."""
        if not raw:
            return None
        parsed = dt_util.parse_datetime(raw)
        if parsed is None:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=TRACK_TRACE_TIMEZONE)
        return dt_util.as_local(parsed)

"""Adds config flow for Blueprint."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    IntegrationBlueprintApiClient,
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientCommunicationError,
    IntegrationBlueprintApiClientError,
)
from .const import DOMAIN, LOGGER


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Crisp."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self,
        info: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user: initial setup"""
        _errors = {}
        if info is not None:
            # TODO: validate email? is there some function for that?

            # TODO: switch to the Crisp userid which is more stable? Or at least make email lowercase
            # Set unique id of this config flow to the entered email
            await self.async_set_unique_id(info[CONF_EMAIL])
            # Ensure config flow can only be done once for this email
            self._abort_if_unique_id_configured()

            try:
                # TODO: call Crisp api to request code, handle response
                await self._test_credentials(
                    email=info[CONF_EMAIL],
                )
            except IntegrationBlueprintApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except IntegrationBlueprintApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except IntegrationBlueprintApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info[CONF_EMAIL],
                    data=info,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL,
                        default=(info or {}).get(CONF_EMAIL),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.EMAIL
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, email: str) -> None:
        """Validate credentials."""
        client = IntegrationBlueprintApiClient(
            email=email,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()

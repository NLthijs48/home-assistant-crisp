"""Adds config flow for Blueprint."""

from __future__ import annotations
import random

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_TOKEN
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    IntegrationBlueprintApiClient,
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientCommunicationError,
    IntegrationBlueprintApiClientError,
)
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Crisp."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self,
        info: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user: initial setup."""
        _errors = {}
        if info is not None:
            # TODO: validate email? is there some function for that?

            # TODO: switch to the Crisp userid which is more stable? Or at least make email lowercase
            # Set unique id of this config flow to the entered email
            await self.async_set_unique_id(info[CONF_EMAIL])
            # Ensure config flow can only be done once for this email
            self._abort_if_unique_id_configured()

            # TODO: check if modification is allowed?
            info[CONF_TOKEN] = self.create_token()

            try:
                # TODO: call Crisp api to request code, handle response
                await self._test_credentials(
                    token=info[CONF_TOKEN],
                    email=info[CONF_EMAIL],
                )
            except IntegrationBlueprintApiClientAuthenticationError as exception:
                _LOGGER.warning(exception)
                _errors["base"] = "auth"
            except IntegrationBlueprintApiClientCommunicationError as exception:
                _LOGGER.error(exception)
                _errors["base"] = "connection"
            except IntegrationBlueprintApiClientError as exception:
                _LOGGER.exception(exception)
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

    async def _test_credentials(self, token: str, email: str) -> None:
        """Validate credentials."""
        client = IntegrationBlueprintApiClient(
            email=email,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()

    def create_token(self) -> str:
        """Create a new token to use for the API."""
        # This matches what the crisp app generates

        tokenCharacters = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )
        token = ""
        while len(token) < 20:
            token += tokenCharacters[random.randrange(0, len(tokenCharacters))]
        return token

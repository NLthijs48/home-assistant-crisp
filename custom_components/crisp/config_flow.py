"""Adds config flow for Crisp."""

from __future__ import annotations


import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_TOKEN
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    CrispApiClient,
    CrispApiClientAuthenticationError,
    CrispApiClientCommunicationError,
    CrispApiClientError,
)
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


class CrispConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Crisp."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self,
        info: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user: initial setup."""
        errors = {}
        # TODO: validate email? is there some function for that?

        if info is not None:
            try:
                info[CONF_TOKEN] = CrispApiClient.generate_client_id()

                # Request a login code for the user belonging to the email
                response = await self.request_login_email(
                    client_id=info[CONF_TOKEN], email=info[CONF_EMAIL]
                )
            except CrispApiClientAuthenticationError as exception:
                _LOGGER.warning(exception)
                errors["base"] = "auth"
            except CrispApiClientCommunicationError as exception:
                _LOGGER.error(exception)
                errors["base"] = "connection"
            except CrispApiClientError as exception:
                _LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                # Error from the api, email not found or something like that
                if "error" in response:
                    errors["email"] = response.error
                elif "id" in response:
                    # TODO: finish the flow without requesting login, use user id directly
                    errors["base"] = "Already logged in"
                else:
                    # TODO: show login code form
                    # Set unique id of this config flow to the Crisp user id
                    # await self.async_set_unique_id(user_id)
                    # Ensure config flow can only be done once for this email
                    # self._abort_if_unique_id_configured()

                    # All good, create config entry
                    return self.async_create_entry(
                        title=info[CONF_EMAIL],
                        data=info,
                    )

        # Show errors in the form
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
            errors=errors,
        )

    async def request_login_email(self, client_id: str, email: str) -> any:
        """Request a login code for the Crisp user that belongs to the given email address."""

        # TODO: ask for country code from the user
        client = CrispApiClient(
            session=async_create_clientsession(self.hass),
            client_id=client_id,
        )
        response = await client.request_login_code(email=email, country="nl")
        _LOGGER.debug(response)
        return response

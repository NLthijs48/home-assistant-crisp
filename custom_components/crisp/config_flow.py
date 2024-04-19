"""Adds config flow for Crisp."""

from __future__ import annotations


import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_TOKEN, CONF_CODE, CONF_COUNTRY_CODE
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    CrispApiClient,
    CrispApiClientAuthenticationError,
    CrispApiClientCommunicationError,
    CrispApiClientError,
)
from .const import DOMAIN, LOGGER


class CrispConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Crisp."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user: enter email of Crisp user."""

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                # Generate client_id
                client_id = CrispApiClient.generate_client_id()
                user_input[CONF_TOKEN] = client_id

                # TODO: ask country from the user
                country = "nl"
                user_input[CONF_COUNTRY_CODE] = country

                self.crisp_client = CrispApiClient(
                    session=async_create_clientsession(self.hass),
                    client_id=client_id,
                )

                # Request a login code for the user belonging to the email
                response = await self.crisp_client.request_login_code(
                    email=user_input[CONF_EMAIL], country=country
                )
                LOGGER.debug("request_login_code response: %s", response)
            except CrispApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                errors["base"] = "auth"
            except CrispApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "connection"
            except CrispApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                # Error from the api, email not found or something like that
                if "error" in response:
                    errors["email"] = response["error"]
                else:
                    # Save the email/client_id
                    self.user_info = user_input

                    if "id" in response:
                        # Somehow this client id is already logged in, directly continue using that user
                        return await self.async_save_user_id(response["id"])

                    # Show the login code step
                    return await self.async_step_login()

        # Show errors in the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL,
                        default=(user_input or {}).get(CONF_EMAIL),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.EMAIL
                        ),
                    ),
                }
            ),
            errors=errors,
            last_step=False,
        )

    async def async_step_login(self, user_input: dict | None = None):
        """Second step of the setup; enter login code for the Crisp user."""

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                # Try to login using the provided code
                response = await self.crisp_client.login(
                    email=self.user_info[CONF_EMAIL],
                    country=self.user_info[CONF_COUNTRY_CODE],
                    login_code=user_input[CONF_CODE],
                )
                LOGGER.debug("login response: %s", response)
            except CrispApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                errors["base"] = "auth"
            except CrispApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "connection"
            except CrispApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                if "error" in response:
                    # These errors are not super human-readable, could attempt to map some of them to better text
                    errors[CONF_CODE] = "Could not login: " + response["error"]
                elif "id" not in response:
                    # Did not get a user id back as confirmation, something went wrong
                    errors["base"] = "Unknown error, could not login"
                else:
                    return await self.async_save_user_id(response["id"])

        return self.async_show_form(
            step_id="login",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CODE,
                        default=(user_input or {}).get(CONF_CODE),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                }
            ),
            errors=errors,
        )

    async def async_save_user_id(
        self, user_id: int
    ) -> config_entries.data_entry_flow.FlowResult:
        """Save the Crisp user id and create the config entry."""

        self.user_info["user_id"] = user_id

        # Set unique id of this config flow to the Crisp user id (more stable than email, which can be changed)
        await self.async_set_unique_id(str(user_id))
        # Ensure config flow can only be done once for this Crisp user id
        self._abort_if_unique_id_configured()

        # All good, create config entry
        return self.async_create_entry(
            title=self.user_info[CONF_EMAIL],
            data=self.user_info,
        )

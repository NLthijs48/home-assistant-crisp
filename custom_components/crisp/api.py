"""Sample API Client."""

from __future__ import annotations

import socket

import aiohttp
import async_timeout
import random


DEFAULT_ORIGIN = "https://crispapp.nl"
"""Default origin as used by the Crisp app api"""


class CrispApiClientError(Exception):
    """Exception to indicate a general API error."""


class CrispApiClientCommunicationError(CrispApiClientError):
    """Exception to indicate a communication error."""


# TODO: probably remove this and replace with something more specific
class CrispApiClientAuthenticationError(CrispApiClientError):
    """Exception to indicate an authentication error."""


# TODO: country enum?
class CrispApiClient:
    """Crisp API client."""

    @staticmethod
    def generate_client_id() -> str:
        """Generate a new client id to use with the api.

        A client id is meant as unique identifier for a device, and is meant to remain the same forever.
        Login/logout actions will attach/detacht a user account to this client identifier.
        """
        # These characters and the length match what the Crisp app generates
        character_set = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        client_id = ""
        while len(client_id) < 20:
            client_id += character_set[random.randrange(0, len(character_set))]
        return client_id

    def __init__(
        self,
        client_id: str,
        session: aiohttp.ClientSession,
        origin: str = DEFAULT_ORIGIN,
    ) -> None:
        """Crisp API Client."""

        self._client_id = client_id
        self._session = session
        self._origin = origin
        self._headers = {
            "Origin": origin,
            "Content-Type": "application/json",
            "Authorization": f"bearer {client_id}",
            # Indicate where these requests are coming from
            "User-Agent": "github.com/NLthijs48/home-assistant-crisp",
            # Identify as Android release from around 2024-04
            # - upside: ensures the api will remain compatible for a while
            # - downside: at some point this version is phased out and blocked
            "X-Crisp-Agent": "crisp/56eaa8fd96/app/android/519",
        }

    async def request_login_code(self, email: str, country: str) -> any:
        """Request login code for the account of the given email."""

        return await self._api_wrapper(
            method="post", path="/user/login", data={"email": email, "country": country}
        )

    async def login(self, email: str, country: str, login_code: str) -> any:
        """Login a user using the login code retreived from the email sent by request_login_code."""

        return await self._api_wrapper(
            method="post",
            path="/user/login",
            data={"email": email, "country": country, "code": login_code},
        )

    async def _api_wrapper(
        self,
        method: str,
        path: str,
        data: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=f"{self._origin}/v1{path}",
                    headers=self._headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise CrispApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except TimeoutError as exception:
            raise CrispApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            print(exception)
            raise CrispApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise CrispApiClientError("Something really wrong happened!") from exception

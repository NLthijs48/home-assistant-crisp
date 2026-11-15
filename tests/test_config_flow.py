"""Tests for the Crisp config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_CODE, CONF_COUNTRY_CODE, CONF_EMAIL, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.crisp.api import (
    CrispApiClient,
    CrispApiClientAuthenticationError,
    CrispApiClientCommunicationError,
    CrispApiClientError,
    CrispCountry,
)
from custom_components.crisp.const import DOMAIN

EMAIL = "user@example.com"
COUNTRY = CrispCountry.NETHERLANDS.value
TOKEN = "test-client-id"  # noqa: S105
USER_ID = 12345
USER_INPUT = {CONF_COUNTRY_CODE: COUNTRY, CONF_EMAIL: EMAIL}
TITLE = f"{EMAIL} ({CrispCountry.NETHERLANDS.display_name})"

EXCEPTION_ERRORS = [
    (CrispApiClientAuthenticationError, "auth"),
    (CrispApiClientCommunicationError, "connection"),
    (CrispApiClientError, "unknown"),
]


@pytest.fixture(autouse=True)
def mock_client_id():
    """Use a fixed client id."""
    with patch.object(CrispApiClient, "generate_client_id", return_value=TOKEN):
        yield


@pytest.fixture
def mock_request_login_code():
    """Mock requesting a login code (login code needed)."""
    with patch.object(
        CrispApiClient, "request_login_code", new_callable=AsyncMock, return_value={}
    ) as mock:
        yield mock


@pytest.fixture
def mock_login():
    """Mock logging in with a code."""
    with patch.object(
        CrispApiClient, "login", new_callable=AsyncMock, return_value={"id": USER_ID}
    ) as mock:
        yield mock


async def _start_user_flow(hass: HomeAssistant) -> dict:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    return result


async def _to_login_step(hass: HomeAssistant) -> dict:
    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], dict(USER_INPUT)
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "login"
    return result


def _assert_created(result: dict) -> None:
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == TITLE
    assert result["data"] == {
        CONF_COUNTRY_CODE: COUNTRY,
        CONF_EMAIL: EMAIL,
        CONF_TOKEN: TOKEN,
        "user_id": USER_ID,
    }


async def test_full_flow(
    hass: HomeAssistant, mock_request_login_code, mock_login, mock_setup_entry
) -> None:
    """Test the user form, login form and entry creation."""
    result = await _to_login_step(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )

    _assert_created(result)
    assert result["result"].unique_id == str(USER_ID)
    mock_request_login_code.assert_awaited_once_with(email=EMAIL, country=COUNTRY)
    mock_login.assert_awaited_once_with(
        email=EMAIL, country=COUNTRY, login_code="123456"
    )
    assert len(mock_setup_entry.mock_calls) == 1


async def test_already_logged_in(
    hass: HomeAssistant, mock_request_login_code, mock_login, mock_setup_entry
) -> None:
    """Test the shortcut where the client id is already logged in."""
    mock_request_login_code.return_value = {"id": USER_ID}
    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], dict(USER_INPUT)
    )

    _assert_created(result)
    mock_login.assert_not_awaited()


async def test_duplicate_account(
    hass: HomeAssistant, mock_request_login_code, mock_login, mock_setup_entry
) -> None:
    """Test a second flow for the same Crisp user aborts."""
    MockConfigEntry(domain=DOMAIN, unique_id=str(USER_ID), data={}).add_to_hass(hass)

    result = await _to_login_step(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(("exception", "error"), EXCEPTION_ERRORS)
async def test_user_step_exceptions(
    hass: HomeAssistant,
    mock_request_login_code,
    mock_login,
    mock_setup_entry,
    exception: type[Exception],
    error: str,
) -> None:
    """Test errors from the API in the user step, then recover."""
    mock_request_login_code.side_effect = exception("boom")
    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], dict(USER_INPUT)
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": error}

    mock_request_login_code.side_effect = None
    mock_request_login_code.return_value = {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], dict(USER_INPUT)
    )
    assert result["step_id"] == "login"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )
    _assert_created(result)


async def test_user_step_error_in_response(
    hass: HomeAssistant, mock_request_login_code, mock_login, mock_setup_entry
) -> None:
    """Test an error in the response is shown on the email field."""
    mock_request_login_code.return_value = {"error": "unknown_email"}
    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], dict(USER_INPUT)
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_EMAIL: "invalid_email"}
    assert result["description_placeholders"] == {"error": "unknown_email"}

    mock_request_login_code.return_value = {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], dict(USER_INPUT)
    )
    assert result["step_id"] == "login"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )
    _assert_created(result)


@pytest.mark.parametrize(("exception", "error"), EXCEPTION_ERRORS)
async def test_login_step_exceptions(
    hass: HomeAssistant,
    mock_request_login_code,
    mock_login,
    mock_setup_entry,
    exception: type[Exception],
    error: str,
) -> None:
    """Test errors from the API in the login step, then recover."""
    result = await _to_login_step(hass)
    mock_login.side_effect = exception("boom")
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "000000"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "login"
    assert result["errors"] == {"base": error}

    mock_login.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )
    _assert_created(result)


@pytest.mark.parametrize(
    ("response", "errors"),
    [
        ({"error": "bad_code"}, {CONF_CODE: "invalid_code"}),
        ({}, {"base": "login_failed"}),
    ],
)
async def test_login_step_bad_response(
    hass: HomeAssistant,
    mock_request_login_code,
    mock_login,
    mock_setup_entry,
    response: dict,
    errors: dict,
) -> None:
    """Test unsuccessful login responses, then recover."""
    result = await _to_login_step(hass)
    mock_login.return_value = response
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "000000"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == errors
    if "error" in response:
        assert result["description_placeholders"] == {"error": response["error"]}

    mock_login.return_value = {"id": USER_ID}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )
    _assert_created(result)


@pytest.fixture
def reauth_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create an existing config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        unique_id=str(USER_ID),
        data={
            CONF_EMAIL: EMAIL,
            CONF_COUNTRY_CODE: COUNTRY,
            CONF_TOKEN: "old-token",
            "user_id": USER_ID,
        },
    )
    entry.add_to_hass(hass)
    return entry


async def test_reauth_success(
    hass: HomeAssistant,
    reauth_entry: MockConfigEntry,
    mock_request_login_code,
    mock_login,
    mock_setup_entry,
) -> None:
    """Test reauth with a login code updates the entry."""
    result = await reauth_entry.start_reauth_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_EMAIL: "new@example.com"}
    )
    assert result["step_id"] == "login"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert reauth_entry.data[CONF_EMAIL] == "new@example.com"
    assert reauth_entry.data[CONF_TOKEN] == "old-token"


async def test_reauth_already_logged_in(
    hass: HomeAssistant,
    reauth_entry: MockConfigEntry,
    mock_request_login_code,
    mock_login,
    mock_setup_entry,
) -> None:
    """Test reauth where the client id is still logged in."""
    mock_request_login_code.return_value = {"id": USER_ID}
    result = await reauth_entry.start_reauth_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_EMAIL: EMAIL}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    mock_login.assert_not_awaited()


@pytest.mark.parametrize(
    ("side_effect", "return_value", "error"),
    [
        (CrispApiClientAuthenticationError("boom"), None, "auth"),
        (CrispApiClientCommunicationError("boom"), None, "connection"),
        (CrispApiClientError("boom"), None, "unknown"),
        (None, {"error": "nope"}, "auth"),
    ],
)
async def test_reauth_confirm_errors(
    hass: HomeAssistant,
    reauth_entry: MockConfigEntry,
    mock_request_login_code,
    mock_login,
    mock_setup_entry,
    side_effect: Exception | None,
    return_value: dict | None,
    error: str,
) -> None:
    """Test errors in reauth_confirm, then recover."""
    mock_request_login_code.side_effect = side_effect
    if return_value is not None:
        mock_request_login_code.return_value = return_value
    result = await reauth_entry.start_reauth_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_EMAIL: EMAIL}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {"base": error}

    mock_request_login_code.side_effect = None
    mock_request_login_code.return_value = {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_EMAIL: EMAIL}
    )
    assert result["step_id"] == "login"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"


async def test_reauth_unique_id_mismatch(
    hass: HomeAssistant,
    reauth_entry: MockConfigEntry,
    mock_request_login_code,
    mock_login,
    mock_setup_entry,
) -> None:
    """Test reauth with a different Crisp account aborts."""
    mock_login.return_value = {"id": USER_ID + 1}
    result = await reauth_entry.start_reauth_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_EMAIL: EMAIL}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CODE: "123456"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unique_id_mismatch"
    assert reauth_entry.data["user_id"] == USER_ID

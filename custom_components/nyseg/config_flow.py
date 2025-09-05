"""Config flow for NYSEG"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DEFAULT_NAME,
    DOMAIN,
)
from .coordinator import NysegConfigEntry


class NysegFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle NYSEG config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: NysegConfigEntry,
    ) -> NysegOptionsFlowHandler:
        """Get the options flow for this handler."""
        return NysegOptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(title=DEFAULT_NAME, data=user_input)


class NysegOptionsFlowHandler(OptionsFlowWithReload):
    """Handle NYSEG options."""

    def __init__(self) -> None:
        """Initialize options flow."""
        self._servers: dict = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        self._servers = self.config_entry.runtime_data.servers

        options = {
            vol.Required(
                CONF_USERNAME,
                default=self.config_entry.options.get(CONF_USERNAME, ''),
            ): vol.In(self._servers.keys()),
            vol.Required(
                CONF_PASSWORD,
                default=self.config_entry.options.get(CONF_PASSWORD, ''),
            ): vol.In(self._servers.keys()),
        }

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(options), errors=errors
        )
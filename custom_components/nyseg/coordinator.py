"""Coordinator for NYSEG"""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from nyseg_scraper import NysegScraper

from .const import CONF_PASSWORD, CONF_USERNAME, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type NysegConfigEntry = ConfigEntry[NysegDataCoordinator]


class NysegDataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Get the latest data from NYSEG."""

    config_entry: NysegConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: NysegConfigEntry,
        api: NysegScraper,
    ) -> None:
        """Initialize the data object."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
        )

    def update_data(self) -> dict[str, Any]:
        """Get the latest data from NYSEG."""
        username = self.config_entry.options.get(CONF_USERNAME)
        password = self.config_entry.options.get(CONF_PASSWORD)
        results = self.api.fetch(username, password)
        return results

    async def _async_update_data(self) -> dict[str, Any]:
        """Update NYSEG data."""
        try:
            return await self.hass.async_add_executor_job(self.update_data)
        except Exception as err:
            raise UpdateFailed(err) from err
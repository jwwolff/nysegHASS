"""Support for loading data from NYSEG."""

from __future__ import annotations

from functools import partial

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.start import async_at_started

from nyseg_scraper import NysegScraper

from .coordinator import NysegConfigEntry, NysegDataCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: NysegConfigEntry
) -> bool:
    """Set up the NYSEG component."""
    try:
        api = await hass.async_add_executor_job(
            partial(NysegScraper, secure=True)
        )
        coordinator = NysegDataCoordinator(hass, config_entry, api)
    except Exception as err:
        raise ConfigEntryNotReady from err

    config_entry.runtime_data = coordinator

    async def _async_finish_startup(hass: HomeAssistant) -> None:
        """Run this only when HA has finished its startup."""
        if config_entry.state is ConfigEntryState.LOADED:
            await coordinator.async_refresh()
        else:
            await coordinator.async_config_entry_first_refresh()

    # Don't fetch data during startup
    async_at_started(hass, _async_finish_startup)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True

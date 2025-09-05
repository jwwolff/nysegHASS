from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR

_LOGGER = logging.getLogger(__name__)
DOMAIN = "nyseg"

async def nysegFetch() -> tuple[str, float]:
    """Mock function to fetch energy usage data from NYSEG."""
    # Replace this with actual scraping or API logic
    from datetime import date
    return date.today().isoformat(), 12.34  # Example: ("2025-09-04", 12.34 kWh)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the nyseg integration via configuration.yaml (legacy)."""
    return True  # Prefer config entry setup

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up nyseg from a config entry."""
    coordinator = NysegDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    hass.helpers.entity_platform.async_add_entities(
        [NysegEnergySensor(coordinator)],
        update_before_add=True
    )

    return True

class NysegDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch NYSEG energy usage daily."""

    def __init__(self, hass: HomeAssistant):
        super().__init__(
            hass,
            _LOGGER,
            name="NYSEG Energy Coordinator",
            update_interval=timedelta(days=1),
        )

    async def _async_update_data(self):
        """Fetch the latest energy usage data."""
        try:
            async with async_timeout.timeout(10):
                date_str, energy_value = await nysegFetch()
                return {"date": date_str, "energy": energy_value}
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch NYSEG data: {err}")

class NysegEnergySensor(CoordinatorEntity, SensorEntity):
    """Sensor entity to report daily NYSEG energy usage."""

    def __init__(self, coordinator: NysegDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_name = "NYSEG Energy Usage"
        self._attr_unique_id = "nyseg_energy_usage"
        self._attr_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_device_class = "energy"

    @property
    def state(self):
        return self.coordinator.data.get("energy")

    @property
    def extra_state_attributes(self):
        return {
            "date": self.coordinator.data.get("date")
        }

"""The Prusa Connect integration."""
import logging
import time
from typing import Optional

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.const import (
    CONF_HOST,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_SENSORS,
    CONF_SSL,
    PERCENTAGE,
    TEMP_CELSIUS,
    TIME_SECONDS,
)
from homeassistant.helpers.discovery import load_platform
from homeassistant.util import slugify as util_slugify

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Prusa Connect"
DOMAIN = "prusa_connect"


def has_all_unique_names(value):
    """Validate that printers have an unique name."""
    names = [util_slugify(printer["name"]) for printer in value]
    vol.Schema(vol.Unique())(names)
    return value


SENSOR_TYPES = {
    # key, unit, icon
    "Current State": ["state", None, "mdi:printer-3d"],
    "Bed Temperature": ["temp_bed", TEMP_CELSIUS, "mdi:thermometer"],
    "Job Percentage": ["progress", PERCENTAGE, "mdi:file-percent"],
    "Material": ["material", None, "mdi:printer-3d-nozzle"],
    "Nozzle Temperature": ["temp_nozzle", TEMP_CELSIUS, "mdi:thermometer"],
    "Project Name": ["project_name", None, "mdi:file-cad"],
    "Time Elapsed": ["print_dur", TIME_SECONDS, "mdi:clock-start"],
    "Time Remaining": ["time_est", TIME_SECONDS, "mdi:clock-end"],
}

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_HOST): cv.string,
                        vol.Optional(CONF_SSL, default=False): cv.boolean,
                        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                        vol.Optional(CONF_SENSORS, default={}): SENSOR_SCHEMA,
                    }
                )
            ],
            has_all_unique_names,
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up the Prusa Connect component."""

    printers = hass.data[DOMAIN] = {}
    success = False

    if DOMAIN not in config:
        # Skip the setup if there is no configuration present
        return True

    for printer in config[DOMAIN]:
        name = printer[CONF_NAME]
        protocol = "https" if printer[CONF_SSL] else "http"
        url = f"{protocol}://{printer[CONF_HOST]}/api/telemetry"
        try:
            prusa_connect_api = PrusaConnectAPI(url)
            printers[url] = prusa_connect_api
            prusa_connect_api.get()
        except requests.exceptions.RequestException as conn_err:
            _LOGGER.error("Error setting up Prusa Conect API: %r", conn_err)
            continue

        sensors = printer[CONF_SENSORS][CONF_MONITORED_CONDITIONS]
        load_platform(
            hass,
            "sensor",
            DOMAIN,
            {"name": name, "url": url, "sensors": sensors},
            config,
        )

        success = True

    return success


class PrusaConnectAPI:
    """Simple JSON wrapper for Prusa Connect API."""

    def __init__(self, url):
        """Initialize Prusa Connect API."""
        self.url = url
        self.last_reading = [{}, None]
        self.available = False
        self.error_logged = False

    def get(self) -> Optional[dict]:
        """Send a get request, and return the response as a dict."""
        # Only query the API at most every 30 seconds
        now = time.time()
        last_time: Optional[float] = self.last_reading[1]
        if last_time is not None and now - last_time < 30.0:
            return self.last_reading[0]

        try:
            response = requests.get(self.url, timeout=9)
            response.raise_for_status()
            self.last_reading[0] = response.json()
            self.last_reading[1] = time.time()
            self.available = True
            self.error_logged = False
            return response.json()

        except requests.exceptions.RequestException as exc:
            log_string = "Failed to update Prusa Connect status. Error: %s" % exc
            if not self.error_logged:
                _LOGGER.warning(log_string)
                self.available = False
                self.error_logged = True
            return None

    def update(self, sensor_type):
        """Return the value for sensor_type from the provided endpoint."""
        response = self.get()
        if response is not None:
            return get_value_from_json(response, sensor_type)
        return None


def get_value_from_json(json_dict, sensor_type):
    """Return the value for sensor_type from the JSON."""
    if sensor_type == "state":
        if "project_name" in json_dict:
            return "Printing"
        return "Operational"
    return json_dict.get(sensor_type)

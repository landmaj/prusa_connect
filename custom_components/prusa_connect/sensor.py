"""Support for monitoring Prusa Connect sensors."""
import logging

from homeassistant.components.sensor import SensorEntity

from . import DOMAIN as COMPONENT_DOMAIN
from . import SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the available Prusa Connect sensors."""
    if discovery_info is None:
        return

    printer_name = discovery_info["name"]
    url = discovery_info["url"]
    sensors = discovery_info["sensors"]
    prusa_connect_api = hass.data[COMPONENT_DOMAIN][url]

    devices = []
    for sensor_name in sensors:
        new_sensor = PrusaConnectSensor(
            api=prusa_connect_api,
            sensor_name=sensor_name,
            sensor_type=SENSOR_TYPES[sensor_name][0],
            printer_name=printer_name,
            unit=SENSOR_TYPES[sensor_name][1],
            icon=SENSOR_TYPES[sensor_name][2],
        )
        devices.append(new_sensor)
    add_entities(devices, True)


class PrusaConnectSensor(SensorEntity):
    """Representation of an OctoPrint sensor."""

    def __init__(
        self,
        api,
        sensor_name,
        sensor_type,
        printer_name,
        unit,
        icon=None,
    ):
        """Initialize a new Prusa Connect sensor."""
        if sensor_type == "temp_nozzle":
            sensor_name = "Actual Tool0 Temp"
        elif sensor_type == "temp_bed":
            sensor_name = "Actual Bed Temp"

        self._name = f"{printer_name} {sensor_name}"
        self.sensor_type = sensor_type
        self.api = api
        self._state = None
        self._unit_of_measurement = unit
        self._icon = icon
        _LOGGER.debug("Created Prusa Connect sensor %r", self)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.sensor_type == "print_dur":
            return parse_print_dur(self._state)
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def update(self):
        """Update state of sensor."""
        self._state = self.api.update(self.sensor_type)

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return self._icon


def parse_print_dur(print_dur):
    """
    Parse formatted string containing print duration to total seconds.

    >>> parse_print_dur("     56m 47s")
    3407
    """

    h_index = print_dur.find("h")
    hours = int(print_dur[h_index - 2 : h_index]) if h_index != -1 else 0

    m_index = print_dur.find("m")
    minutes = int(print_dur[m_index - 2 : m_index]) if m_index != -1 else 0

    s_index = print_dur.find("s")
    seconds = int(print_dur[s_index - 2 : s_index]) if s_index != -1 else 0

    return hours * 60 * 60 + minutes * 60 + seconds

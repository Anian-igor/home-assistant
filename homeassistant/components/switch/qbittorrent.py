import logging

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.exceptions import PlatformNotReady
from homeassistant.const import (
    CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME, STATE_OFF,
    STATE_ON)
from homeassistant.helpers.entity import ToggleEntity
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['python-qbittorrent==0.3.1']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Qbittorrent Switch'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the qbittorrent switch."""
    from qbittorrent import Client

    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    
    try:
        qbit_client = Client(host)
        qbit_client.login(username, password)
    except:
        _LOGGER.error("Connection to qbittorrent failed")
        raise PlatformNotReady

    add_devices([QbittorrentSwitch(qbit_client, name, username, password)])


class QbittorrentSwitch(ToggleEntity):
    """Representation of a qbittorrent switch."""

    def __init__(self, qbit_client, name, username, password):
        """Initialize the qbittorrent switch."""
        self._name = name
        self.qbit_client = qbit_client
        self.username = username
        self.password = password
        self._state = STATE_OFF
        self._available = False

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state == STATE_ON

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self.qbit_client.login(self.username, self.password)
        self.qbit_client.toggle_alternative_speed()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.qbit_client.login(self.username, self.password)
        self.qbit_client.toggle_alternative_speed()

    def update(self):
        """Get the latest data from qbittorrent and updates the state."""
        try:
            self.qbit_client.login(self.username, self.password)
            self.qbit_client.qbittorrent_version
            self._available = True
        except:
            _LOGGER.error("Connection to qbittorrent Lost")
            self._available = False
            return

        if self.qbit_client.alternative_speed_status == 0:
            self._state = STATE_OFF
        else:
            self._state = STATE_ON
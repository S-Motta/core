"""Support for ISY994 lights."""
import logging
from typing import Callable

from homeassistant.components.light import DOMAIN, SUPPORT_BRIGHTNESS, Light
from homeassistant.helpers.typing import ConfigType

from . import ISY994_NODES, ISYDevice

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass, config: ConfigType, add_entities: Callable[[list], None], discovery_info=None
):
    """Set up the ISY994 light platform."""
    devices = []
    for node in hass.data[ISY994_NODES][DOMAIN]:
        devices.append(ISYLightDevice(node))

    add_entities(devices)


class ISYLightDevice(ISYDevice, Light):
    """Representation of an ISY994 light device."""

    def __init__(self, node) -> None:
        """Initialize the ISY994 light device."""
        super().__init__(node)
        self._last_brightness = self.brightness

    @property
    def is_on(self) -> bool:
        """Get whether the ISY994 light is on."""
        if self.is_unknown():
            return False
        return self.value != 0

    @property
    def brightness(self) -> float:
        """Get the brightness of the ISY994 light."""
        return None if self.is_unknown() else self.value

    def turn_off(self, **kwargs) -> None:
        """Send the turn off command to the ISY994 light device."""
        self._last_brightness = self.brightness
        if not self._node.off():
            _LOGGER.debug("Unable to turn off light")

    def on_update(self, event: object) -> None:
        """Save brightness in the update event from the ISY994 Node."""
        if not self.is_unknown() and self.value != 0:
            self._last_brightness = self.value
        super().on_update(event)

    # pylint: disable=arguments-differ
    def turn_on(self, brightness=None, **kwargs) -> None:
        """Send the turn on command to the ISY994 light device."""
        if brightness is None and self._last_brightness is not None:
            brightness = self._last_brightness
        if not self._node.on(val=brightness):
            _LOGGER.debug("Unable to turn on light")

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

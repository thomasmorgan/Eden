"""The sun."""

import settings


class Sun():
    """The sun.

    It is part of the simulation.
    It affects the energy inputs to the world.
    """

    def __init__(self):
        """Create the sun."""
        self.power = settings.sun_power
        self.distance = settings.sun_distance

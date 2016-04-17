import settings
import math


class Sun():

    """ The sun object is part of the simulation.
    It affects the energy inputs to the world.
    """

    def __init__(self):
        self.power = settings.sun_power
        self.distance = settings.sun_distance

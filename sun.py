import settings
import math


class Sun():

    """ The sun object is part of the simulation.
    It affects the energy inputs to the world.
    """

    def __init__(self):
        self.total_daily_energy = settings.sun_total_daily_energy
        self.distance = settings.sun_distance
        self.max_solar_energy_per_cell = pow(settings.cell_size, 2)/(4*math.pi*pow(self.distance, 2))*self.total_daily_energy

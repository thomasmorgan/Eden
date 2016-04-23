import settings
import math


class Cell():

    """ The cell class is a repeated unit that collectively make a world.
    Cells have land and water and can be though of as a single column on
    the world's surface.
    """

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.apparent_size_from_sun = math.sin(math.radians(self.latitude))*settings.cell_area
        self.land = Land()
        self.water = Water()

    def calculate_temperature(self):
        self.land.calculate_temperature()


class Land():

    """ The terrain of a cell """

    def __init__(self):
        self.mass = pow(settings.cell_area, 2)*settings.land_depth*settings.land_density
        self.thermal_energy = settings.initial_land_temperature * self.mass * settings.land_specific_heat_capacity
        self.height = 0.0
        self.calculate_temperature()

    def calculate_temperature(self):
        """ calculate the temperature of the cell given its thermal energy """
        # see: https://en.wikipedia.org/wiki/Heat_capacity
        self.temperature = self.thermal_energy/(self.mass*settings.land_specific_heat_capacity)


class Water():

    """ The water of a cell """

    def __init__(self):
        self.volume = 0.0

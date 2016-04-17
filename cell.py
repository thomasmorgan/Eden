import settings
import math


class Cell():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.apparent_size_from_sun = math.cos(abs(self.y - (settings.world_cell_height-1)/2.0)/((settings.world_cell_height-1)/2.0)*(math.pi/2))

        self.land = Land()
        self.water = Water()

        # self.calculate_temperature()
        # self.wind = None
        # self.wind_speed = None

    def calculate_temperature(self):
        # self.temperature = self.thermal_energy/(settings.atmosphere_heat_constant*settings.atmosphere_mass_per_cell)
        self.land.calculate_temperature()


class Land():

    def __init__(self):
        self.mass = pow(settings.cell_size, 2)*settings.land_depth*settings.land_density
        self.thermal_energy = 1.0*pow(10, 18)
        self.height = None
        self.calculate_temperature()

    def calculate_temperature(self):
        self.temperature = self.thermal_energy/(self.mass + settings.land_specific_heat)


class Water():

    def __init__(self):
        self.volume = 0.0

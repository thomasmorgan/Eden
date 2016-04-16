import settings
import math


class Cell():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ground_height = None
        self.water_depth = 0.0
        self.solar_energy_per_day = (1-settings.atmosphere_albedo)*math.cos(abs(self.y - (settings.world_cell_height-1)/2.0)/((settings.world_cell_height-1)/2.0)*(math.pi/2))*settings.max_solar_energy_per_cell
        self.thermal_energy = settings.initial_temperature*settings.atmosphere_heat_constant*settings.atmosphere_mass_per_cell
        self.temperature = None
        self.calculate_temperature()
        self.wind = None
        self.wind_speed = None

        self.x_min = x*settings.cell_width + settings.map_border
        self.y_min = y*settings.cell_height + settings.map_border
        self.x_max = (x+1)*settings.cell_width + settings.map_border
        self.y_max = (y+1)*settings.cell_height + settings.map_border

    def calculate_temperature(self):
        self.temperature = self.thermal_energy/(settings.atmosphere_heat_constant*settings.atmosphere_mass_per_cell)

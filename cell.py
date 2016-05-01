"""Cells and their constituent classes."""

import settings
import math


class Cell():
    """The repeated unit that makes up a world.

    Cells have land and water and can be though of as a single column on
    the world's surface.
    """

    def __init__(self, latitude, longitude):
        """Make a cell."""
        self.latitude = latitude
        self.longitude = longitude
        self.facing_sun = math.sin(math.radians(self.latitude))
        self.land = Land()
        self.water = Water()
        self.neighbors = []

    def calculate_temperature(self):
        """Update temperature values."""
        self.land.calculate_temperature()

    @property
    def surface_height(self):
        """Height of the surface (land or sea)."""
        return self.land.height + self.water.depth

    @property
    def surface_temperature(self):
        """Temperature of surface (land or sea)."""
        if self.water.depth > 0:
            return self.water.temperature
        else:
            return self.land.temperature


class Land():
    """The terrain of a cell."""

    def __init__(self):
        """Make some land."""
        self.mass = (settings.cell_area * settings.land_depth *
                     settings.land_density)
        self.thermal_energy = (settings.initial_land_temperature * self.mass *
                               settings.land_specific_heat_capacity)
        self.height = 0.0
        self.calculate_temperature()

    def calculate_temperature(self):
        """Calculate the temperature of the cell given its thermal energy."""
        # see: https://en.wikipedia.org/wiki/Heat_capacity
        self.temperature = (self.thermal_energy /
                            (self.mass*settings.land_specific_heat_capacity))


class Water():
    """The water of a cell."""

    def __init__(self):
        """Create some water."""
        self.mass = 0.0
        self.depth = 0.0
        self.volume = 0.0

    def change_volume(self, amount):
        """Change volume by specified amount."""
        self.volume += amount
        self.depth = self.volume/settings.cell_area
        self.mass = self.volume*settings.tv.water_density

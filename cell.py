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
        self.land = Land(self)
        self.water = Water(self)
        self.neighbors = []

    def add_material(self, material, mass, temperature):
        """Add some material to a cell."""
        if material == "land":
            self.land.change_mass(mass, temperature)
        elif material == "water":
            self.water.change_mass(mass, temperature)
        else:
            raise ValueError("Unrecognised material: {}".format(material))

    def gain_solar_energy(self, energy):
        """Absorb energy from above."""
        if self.water.volume > 0:
            # water reflects some
            energy_reflected_by_water =\
                energy*settings.water_albedo(self.facing_sun)
            energy -= energy_reflected_by_water

            # water absorbs some
            energy_absorbed_by_water =\
                (1 - math.exp(-settings.water_absorbicity *
                              self.water.depth))*energy
            self.water.thermal_energy += energy_absorbed_by_water
            energy -= energy_absorbed_by_water

        # land reflects some
        energy_reflected_by_land = energy * settings.land_albedo
        energy_lost_to_space = energy_reflected_by_land

        # land absorbs some
        energy_absorbed_by_land =\
            energy - energy_reflected_by_land
        self.land.thermal_energy += energy_absorbed_by_land

        if self.water.volume > 0:
            # water absorbs some that was reflected by land
            energy_absorbed_by_water2 =\
                (1 - math.exp(-settings.water_absorbicity *
                              self.water.depth))*energy_reflected_by_land
            self.water.thermal_energy += energy_absorbed_by_water2
            energy_lost_to_space = energy_reflected_by_land -\
                energy_absorbed_by_water2

        self.calculate_temperature()

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


class Material(object):
    """An abstract class for physical materials."""

    def __init__(self, cell):
        """Create some material."""
        self.cell = cell
        self.mass = 0.0
        self.thermal_energy = 0.0
        self.specific_heat_capacity = None
        self.density = None

    @property
    def temperature(self):
        """The temperature of the material."""
        if self.mass > 0:
            return (self.thermal_energy /
                    (self.mass * self.specific_heat_capacity))
        else:
            return 0.0

    @property
    def volume(self):
        """The volume of the material."""
        return self.mass / self.density

    @property
    def depth(self):
        """The depth of the material."""
        return self.volume / settings.cell_area

    def change_mass(self, mass, temperature):
        """Change the mass of the material."""
        self.mass += mass
        energy = temperature * mass * self.specific_heat_capacity
        self.thermal_energy += energy


class Land(Material):
    """The terrain of a cell."""

    def __init__(self, cell):
        """Make some land."""
        super(Land, self).__init__(cell)
        self.specific_heat_capacity = settings.land_specific_heat_capacity
        self.density = settings.land_density
        self.height = 0.0


class Water(Material):
    """The water of a cell."""

    def __init__(self, cell):
        """Create some water."""
        super(Water, self).__init__(cell)
        self.specific_heat_capacity = settings.water_specific_heat_capacity
        self.density = settings.water_density

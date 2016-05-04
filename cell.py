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
        energy = self.water.reflect_solar_energy(energy)[1]
        energy = self.water.absorb_solar_energy(energy)[1]
        energies = self.land.reflect_solar_energy(energy)
        self.water.absorb_solar_energy(energies[0])
        self.land.absorb_energy(energies[1])

    def radiate_energy(self):
        """Radiate energy into space."""
        lost_energy = self.land.radiate_energy()
        self.water.absorb_solar_energy(lost_energy)
        self.water.radiate_energy()

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
        self.albedo = None
        self.emissivity = None

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

    def reflect_solar_energy(self, energy):
        """Reflect incident solar energy."""
        if self.mass > 0:
            reflected_energy = energy * self.albedo
        else:
            reflected_energy = 0.0
        remaining_energy = energy - reflected_energy
        return [reflected_energy, remaining_energy]

    def absorb_energy(self, energy):
        """Asborb energy."""
        self.thermal_energy += energy

    def radiate_energy(self):
        """Radiate energy into space."""
        if self.thermal_energy > 0 and self.mass > 0:
            initial_energy = self.thermal_energy
            top = 3 * (settings.tv.stefan_boltzmann_constant *
                       settings.cell_area * self.emissivity *
                       settings.time_step_size)
            bottom = (pow(self.mass, 4) *
                      pow(self.specific_heat_capacity, 4))
            Z = top/bottom
            self.thermal_energy = pow(Z + pow(self.thermal_energy, -3),
                                      -1.0/3.0)
            return initial_energy - self.thermal_energy
        else:
            return 0


class Land(Material):
    """The terrain of a cell."""

    def __init__(self, cell):
        """Make some land."""
        super(Land, self).__init__(cell)
        self.specific_heat_capacity = settings.land_specific_heat_capacity
        self.density = settings.land_density
        self.height = 0.0
        self.albedo = settings.land_albedo
        self.emissivity = settings.land_emissivity


class Water(Material):
    """The water of a cell."""

    def __init__(self, cell):
        """Create some water."""
        super(Water, self).__init__(cell)
        self.specific_heat_capacity = settings.water_specific_heat_capacity
        self.density = settings.water_density
        self.albedo = settings.water_albedo(self.cell.facing_sun)
        self.absorbicity = settings.water_absorbicity
        self.emissivity = settings.water_emissivity

    def absorb_solar_energy(self, energy):
        """Absorb sunlight."""
        energy_absorbed =\
            (1 - math.exp(-self.absorbicity *
                          self.depth))*energy
        self.thermal_energy += energy_absorbed
        energy_remaining = energy - energy_absorbed
        return [energy_absorbed, energy_remaining]

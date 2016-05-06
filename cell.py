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
        mat = getattr(self, material)
        mat.change_mass(mass, temperature)

    def gain_solar_energy(self, energy):
        """Absorb energy from above."""
        if self.water.mass > 0:
            energy = self.water.reflect_solar_energy(energy)[1]
            energy = self.water.absorb_solar_energy(energy)[1]
        energies = self.land.reflect_solar_energy(energy)
        if self.water.mass > 0:
            self.water.absorb_infrared_energy(energies[0])
        self.land.absorb_energy(energies[1])

    def gain_core_energy(self, energy):
        """Absorb energy from the world's core."""
        self.land.absorb_energy(energy)

    def radiate_energy_vertically(self):
        """Radiate energy between land/water/air."""
        # land radiates energy
        lost_land_energy = self.land.radiate_energy()
        if self.water.mass > 0:
            lost_water_energy = self.water.radiate_energy()
            self.water.radiate_energy()
            self.water.absorb_infrared_energy(lost_land_energy)
            self.land.absorb_energy(lost_water_energy)

    def conduct_energy_vertically(self):
        """Conduct energy between land/water/air."""
        # land conducts to water
        if self.water.mass > 0:
            self.land.conduct_energy(to=self.water, area=settings.cell_area)
            self.water.conduct_energy(to=self.land, area=settings.cell_area)

    def conduct_energy_horizontally(self):
        """Conduct energy between neighbors."""
        for n in self.neighbors:
            self.land.conduct_energy(
                to=n.land, area=settings.cell_width*settings.land_depth
            )

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

    def conduct_energy(self, to, area):
        """Conduct energy between materials.

        See thermal energy formula for derivation.
        It is actually based on the laws for thermal
        eergy transfer via convection, but assumes the
        two materials are not moving relative to each other.
        """
        target = to

        if self.temperature > target.temperature:
            E0 = self.thermal_energy
            E = E0 + target.thermal_energy
            m0 = self.mass
            c0 = self.specific_heat_capacity
            m1 = target.mass
            c1 = target.specific_heat_capacity
            k = self.thermal_conductivity
            time = settings.time_step_size

            energy_loss = E0 - (
                ((E * m0 * c0) / (m1 * c1 + m0 * c0)) +
                (E0 - (
                    (E * m0 * c0) /
                    (m1 * c1 + m0 * c0)
                )) * math.exp(
                    (-k * area * (m1 * c1 + m0 * c0) * time) /
                    (m0 * c0 * m1 * c1)
                )
            )

            self.thermal_energy -= energy_loss
            target.thermal_energy += energy_loss


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
        self.thermal_conductivity = settings.land_thermal_conductivity


class Water(Material):
    """The water of a cell."""

    def __init__(self, cell):
        """Create some water."""
        super(Water, self).__init__(cell)
        self.specific_heat_capacity = settings.water_specific_heat_capacity
        self.density = settings.water_density
        self.albedo = settings.water_albedo(self.cell.facing_sun)
        self.attenuation_coefficient_sunlight =\
            settings.water_attenuation_coefficient_sunlight
        self.attenuation_coefficient_infrared =\
            settings.water_attenuation_coefficient_infrared
        self.emissivity = settings.water_emissivity
        self.thermal_conductivity = settings.water_thermal_conductivity

    def absorb_solar_energy(self, energy):
        """Absorb sunlight."""
        energy_absorbed =\
            (1 - math.exp(-self.attenuation_coefficient_sunlight *
                          self.depth))*energy
        self.thermal_energy += energy_absorbed
        energy_remaining = energy - energy_absorbed
        return [energy_absorbed, energy_remaining]

    def absorb_infrared_energy(self, energy):
        """Absorb sunlight."""
        energy_absorbed =\
            (1 - math.exp(-self.attenuation_coefficient_infrared *
                          self.depth))*energy
        self.thermal_energy += energy_absorbed
        energy_remaining = energy - energy_absorbed
        return [energy_absorbed, energy_remaining]

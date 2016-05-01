"""The world class."""

import random
from cell import Cell
import settings
import math
from utility import log


class World():
    """The world class.

    Part of the simulation.
    It is composed of a number of cells that are arranged into a grid.
    """

    """ #####################
    ### CREATION METHODS ####
    ##################### """

    def __init__(self):
        """Build a world."""
        log(">> Creating cells")
        self.create_cells()
        log(">> Distorting terrain")
        self.create_terrain()
        self.normalize_terrain()
        log(">> Creating oceans")
        self.create_oceans()

    def create_cells(self):
        """Create the cells.

        Cells are the spatial units of the world and are stored in a list.
        """
        self.cells = []
        degrees_per_cell = 360.0/float(settings.world_cell_circumference)
        for y in range(settings.world_cell_circumference/2 + 1):
            latitude = degrees_per_cell*y

            if latitude in [0, 180]:
                self.cells.append(Cell(longitude=0.0, latitude=latitude))
            else:
                rad = math.sin(math.radians(latitude))*settings.world_radius
                circ = 2*math.pi*rad
                cells = int(round(circ/float(settings.cell_width)))
                for x in range(cells):
                    longitude = (360.0/float(cells))*x
                    self.cells.append(Cell(longitude=longitude,
                                           latitude=latitude))

        log(">> Assigning cells neighbors")
        for a in range(len(self.cells)):
            cell = self.cells[a]
            for b in range(a+1, len(self.cells)):
                c = self.cells[b]
                if math.acos(
                    max(
                        min(math.cos(math.radians(cell.latitude)) *
                            math.cos(math.radians(c.latitude)) +
                            math.sin(math.radians(cell.latitude)) *
                            math.sin(math.radians(c.latitude)) *
                            math.cos(abs(math.radians(cell.longitude) -
                                         math.radians(c.longitude))),
                            1.0),
                        -1.0)) < 1.3*math.radians(degrees_per_cell):
                    cell.neighbors.append(c)
                    c.neighbors.append(cell)

    def create_terrain(self):
        """Assign height values to the land."""
        # see http://mathworld.wolfram.com/GreatCircle.html
        settings.n_distortions = 1000
        longs = [random.choice(self.cells).longitude
                 for _ in range(settings.n_distortions)]
        lats = [random.choice(self.cells).latitude
                for _ in range(settings.n_distortions)]
        heights = [5000]*len(range(settings.n_distortions))
        rates = [random.random()*3 + 3 for _ in range(settings.n_distortions)]

        for cell in self.cells:
            distances = [settings.world_radius*math.acos(
                max(min(
                    math.cos(math.radians(cell.latitude)) *
                    math.cos(math.radians(lat)) +
                    math.sin(math.radians(cell.latitude)) *
                    math.sin(math.radians(lat)) *
                    math.cos(abs(math.radians(cell.longitude) -
                                 math.radians(long))),
                    1.0), -1.0))
                for lat, long in zip(lats, longs)]
            hs = [h / (d/(100000*r) + 1)
                  for h, d, r in zip(heights, distances, rates)]
            cell.land.height += sum(hs)

    def create_oceans(self):
        """Create water."""
        if settings.water_init_mode == "even":
            water_mass_per_cell = settings.world_water_mass/len(self.cells)
            water_vol_per_cell = water_mass_per_cell/settings.tv.water_density
            for cell in self.cells:
                cell.water.change_volume(water_vol_per_cell, settings.initial_water_temperature)
        elif settings.water_init_mode == "dump":
            cell = random.choice(self.cells)
            cell.water.change_volume(settings.world_water_mass /
                                     settings.tv.water_density,
                                     settings.initial_water_temperature)

    def slosh_oceans(self):
        """Move water between cells according to gravity."""
        index = range(len(self.cells))
        random.shuffle(index)
        for i in index:
            # for each cell
            cell = self.cells[i]
            if cell.water.depth > 0:
                random.shuffle(cell.neighbors)
                # get height difference with neighbors
                height_diffs = [max(0, cell.surface_height - n.surface_height)
                                for n in cell.neighbors]

                # calculate the size and speed of a wave
                # because the tile sends water to all neighbors simultaneously
                # the speed is artifically reduced to avoid excess sloshing
                wave_height = [min(cell.water.depth, h/2)
                               for h in height_diffs]
                wave_area = [h*settings.cell_width for h in wave_height]
                wave_speed = [max(h/5, 1) for h in height_diffs]

                # work out how far the wave goes
                wave_distance = [s*settings.time_step_size for s in wave_speed]

                # work out how much water moves
                # it cannot be more than the max possible
                max_vol_loosable = [w*settings.cell_area for w in wave_height]
                vol_moved = [d*a for d, a in zip(wave_distance, wave_area)]
                for j in range(len(cell.neighbors)):
                    if vol_moved[j] > max_vol_loosable[j]:
                        vol_moved[j] = max_vol_loosable[j]
                total_vol = sum(vol_moved)
                if total_vol > cell.water.volume:
                    vol_moved = [v/(total_vol/cell.water.volume)
                                 for v in vol_moved]

                # update the cells
                cell.water.change_volume(-sum(vol_moved))
                for j in range(len(cell.neighbors)):
                    if vol_moved[j] != 0:
                        cell.neighbors[j].water.change_volume(vol_moved[j])

    """ #####################
    ### EXECUTION METHODS ###
    ######################"""

    def radiate_energy(self):
        """Lose thermal energy (kJ) into space.

        see:
        https://en.wikipedia.org/wiki/Stefan-Boltzmann_law
        https://en.wikipedia.org/wiki/Stefan-Boltzmann_constant
        eden/docs/thermal energy formulae.docx
        """
        time = settings.time_step_size
        area = settings.cell_area
        Z = (settings.tv.stefan_boltzmann_constant *
             area *
             settings.land_emissivity /
             (pow(self.cells[0].land.mass, 4) *
              pow(settings.land_specific_heat_capacity, 4)))
        Z = 3*Z*time
        for c in self.cells:
            c.land.thermal_energy = pow(Z + pow(c.land.thermal_energy, -3),
                                        -1.0/3.0)

    def absorb_energy_from_sun(self, sun):
        """Gain thermal energy (kJ) from the sun."""
        time = settings.time_step_size
        max_W = settings.cell_area/(4*math.pi*pow(sun.distance, 2))*sun.power
        max_E = max_W*time*(1-settings.land_albedo)

        for c in self.cells:
            c.land.thermal_energy += max_E*c.facing_sun

    def absorb_energy_from_core(self):
        """Gain thermal energy (kJ) from within the earth."""
        W = settings.world_power
        time = settings.time_step_size
        E = W*time
        e_per_cell = E / len(self.cells)
        for c in self.cells:
            c.land.thermal_energy += e_per_cell

    def conduct_energy_between_cells(self):
        """Transmit thermal energy between neighboring cells.

        Note that this method makes severe deviations from real physics.
        The rate of conduction is proportional to the energy difference
        and so decreases as conduction occurs. However, the proper solution
        requires integration beyond my abilities and so I have assumed that
        the rate of conduction depends only on the starting temperature
        difference.
        """
        pass

    def calculate_temperature(self):
        """Calculate temperature given thermal energy."""
        for c in self.cells:
            c.land.calculate_temperature()

    """ #####################
    #### SUPPORT METHODS ####
    ######################"""

    def normalize_terrain(self):
        """Adjust land heights so they fit within bounds and average is 0."""
        heights = [t.land.height for t in self.cells]
        mean_height = sum(heights)/len(heights)
        for t in self.cells:
            t.land.height = t.land.height - mean_height

        heights = [t.land.height for t in self.cells]

        scale = max([1, min(heights)/settings.min_ground_height, max(heights) /
                     settings.max_ground_height])
        for t in self.cells:
            t.land.height = t.land.height/scale

    def raise_cell(self, cell_id, height):
        """Raise a cells land height."""
        cell = self.cells[cell_id]

        long = cell.longitude
        lat = cell.latitude
        rate = random.random()*3 + 3

        for cell in self.cells:
            distance = settings.world_radius*math.acos(
                max(min(
                    math.cos(math.radians(cell.latitude)) *
                    math.cos(math.radians(lat)) +
                    math.sin(math.radians(cell.latitude)) *
                    math.sin(math.radians(lat)) *
                    math.cos(abs(math.radians(cell.longitude) -
                                 math.radians(long))),
                    1.0), -1.0))
            hs = height / (distance/(100000*rate) + 1)
            cell.land.height += hs
        self.normalize_terrain()

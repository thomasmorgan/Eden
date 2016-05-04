"""The world class."""

import random
from cell import Cell
import settings
import math
from utility import log
from operator import attrgetter


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
        self.create_land()
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

    def create_land(self):
        """Add land to each cell."""
        vol_per_cell = settings.cell_area * settings.land_depth
        mass_per_cell = vol_per_cell*settings.land_density
        for c in self.cells:
            c.add_material("land",
                           mass_per_cell,
                           settings.initial_land_temperature)

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
            for cell in self.cells:
                cell.add_material("water",
                                  water_mass_per_cell,
                                  settings.initial_water_temperature)
        elif settings.water_init_mode == "dump":
            cell = random.choice(self.cells)
            cell.add_material("water",
                              settings.world_water_mass,
                              settings.initial_water_temperature)

    def slosh_oceans(self):
        """Move water between cells according to gravity.

        This method deviates from real physics.
        """
        index = range(len(self.cells))
        random.shuffle(index)
        for i in index:
            # for each cell
            cell = self.cells[i]
            if cell.water.depth > 0:
                random.shuffle(cell.neighbors)
                for n in cell.neighbors:
                    height_diff = max(0,
                                      cell.surface_height - n.surface_height)
                    if height_diff > 0:
                        wave_height = min(cell.water.depth, height_diff/2)
                        wave_area = wave_height*settings.cell_width
                        wave_vol = max(wave_area * 2.0,
                                       1.0) * settings.time_step_size
                        max_vol_loosable = min(settings.cell_width * wave_area,
                                               cell.water.volume)
                        vol_moved = min(wave_vol,
                                        max_vol_loosable)
                        mass_moved = vol_moved * settings.water_density
                        temp = cell.water.temperature
                        cell.add_material("water",
                                          -mass_moved,
                                          temp)
                        n.add_material("water",
                                       mass_moved,
                                       temp)

    """ #####################
    ### EXECUTION METHODS ###
    ######################"""

    def transfer_energy_vertically(self):
        """Transfer energy between land/water/air/space.

        see:
        https://en.wikipedia.org/wiki/Stefan-Boltzmann_law
        https://en.wikipedia.org/wiki/Stefan-Boltzmann_constant
        eden/docs/thermal energy formulae.docx
        """
        for c in self.cells:
            c.radiate_energy_vertically()
            c.conduct_energy_vertically()

    def absorb_energy_from_sun(self, sun):
        """Gain thermal energy (kJ) from the sun."""
        max_E = settings.cell_area / (4 * math.pi * pow(sun.distance, 2))\
            * sun.power * settings.time_step_size

        for c in self.cells:
            c.gain_solar_energy(max_E*c.facing_sun)

    def absorb_energy_from_core(self):
        """Gain thermal energy (kJ) from within the earth."""
        E = (settings.world_power * settings.time_step_size) / len(self.cells)
        for c in self.cells:
            c.gain_core_energy(E)

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

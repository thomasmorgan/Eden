"""The world class."""

import random
import settings
import math
import utility
from utility import log
import numpy as np
import scipy.stats as stats


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

        Cells are the spatial units of the world and are stored in a dictionary.
        """

        # initialize empty dictionary
        self.cells = {}

        # add longitude and latitiude for all cells
        longitude = []
        latitude = []
        cells_at_latitude = []
        for y in range(settings.world_cell_circumference/2 + 1):
            lat = settings.degrees_per_cell*y - 90.0

            if lat in [-90.0, 90.0]:
                longitude.append(0.0)
                latitude.append(lat)
                cells_at_latitude.append(1)
            else:
                # radius of world at this latitiude
                rad = np.cos(np.radians(lat))*settings.world_radius
                circ = 2*math.pi*rad
                cells = int(round(circ/float(settings.cell_width)))
                for x in range(cells):
                    longit = (360.0/float(cells))*x - 180.0
                    longitude.append(longit)
                    latitude.append(lat)
                    cells_at_latitude.append(cells)

        self.cells['longitude'] = np.array(longitude)
        self.cells['latitude'] = np.array(latitude)
        self.cells['relative_longitude'] = np.array(longitude)
        self.cells['cells_at_latitude'] = np.array(cells_at_latitude)
        self.num_cells = len(self.cells['latitude'])

        print self.cells["latitude"]
        print self.cells["longitude"]

        # create a distance matrix and add it to the dictionary
        self.cells['distance'] = np.empty(shape=(self.num_cells, self.num_cells))
        self.cells['influence'] = np.empty(shape=(self.num_cells, self.num_cells))
        for x in range(self.num_cells):
            self.cells['distance'][x, :] = utility.haversine(self.cells['longitude'][x], self.cells['latitude'][x], self.cells['longitude'], self.cells['latitude'])
            self.cells['influence'][x, :] = np.exp(-settings.influence_lambda*self.cells['distance'][x, :])

        print self.cells['distance'][1, :]
        print self.cells['influence'][1, :]

    def create_terrain(self):
        """Assign height values to the land."""
        # see http://mathworld.wolfram.com/GreatCircle.html

        self.cells["altitude"] = np.zeros(shape=self.num_cells, dtype=float)

        # choose focal cells
        cells = np.random.choice(range(self.num_cells), settings.n_distortions)

        # choose magnitudes of distortions
        magnitudes = (np.random.rand(settings.n_distortions)*1.5 - 0.5)*settings.max_distortion

        # choose scale of distortions
        sds = (np.random.rand(settings.n_distortions)*0.8 + 0.2)*settings.cell_width*4

        for i in range(settings.n_distortions):
            distance = self.cells["distance"][cells[i], ]
            self.cells["altitude"] += magnitudes[i]*stats.norm.pdf(distance, loc=0, scale=sds[i])/stats.norm.pdf(0, loc=0, scale=sds[i])

        self.normalize_terrain()

    def create_oceans(self):
        """Create water."""
        self.cells["water"] = np.zeros(shape=(self.num_cells), dtype=float)
        if settings.water_init_mode == "even":
            water_mass_per_cell = settings.world_water_mass/len(self.cells)
            self.cells["water"] = np.full(water_mass_per_cell, shape=(self.num_cells), dtype=float)
        elif settings.water_init_mode == "dump":
            cell = np.random.randint(0, self.num_cells)
            self.cells["water"][cell] = settings.world_water_mass
        self.cells["water_depth"] = (self.cells["water"]/settings.water_density)/settings.cell_area

    def slosh_oceans(self):
        """Move water between cells according to gravity.

        This method deviates from real physics.
        """

        # work our all current water surface altitudes
        initial_surface_altitude = self.cells["altitude"] + self.cells["water_depth"]

        # how much water can each cell lose in the time step
        water_to_transport = np.minimum(settings.time_step_size*settings.water_transport_rate*self.cells["water_depth"]*settings.cell_width*4, self.cells["water"])

        # take the water away, recalculate depth and altitude
        self.cells["water"] -= water_to_transport
        self.cells["water_depth"] = (self.cells["water"]/settings.water_density)/settings.cell_area
        secondary_surface_altitude = self.cells["altitude"] + self.cells["water_depth"] - 0.000001

        # make a matrix of the secondary surface altitudes of each cell
        ssa_matrix = np.reshape(np.tile(secondary_surface_altitude, self.num_cells), (self.num_cells, self.num_cells))

        # subtract the initial surface altitude of the ith cell from the ith row, floor at 0.0001, then multiply by the influence matrix
        # this gives a matrix saying how much each cell wants to send water to every other cell according to influence and difference in altitude
        attraction_matrix = np.maximum(initial_surface_altitude - ssa_matrix.T, 0).T*self.cells["influence"]

        # scale values to each row sums to water_to_transport
        delta_water = sum(((attraction_matrix.T/sum(attraction_matrix.T))*water_to_transport).T)
        self.cells["water"] += delta_water

        self.cells["water_depth"] = (self.cells["water"]/settings.water_density)/settings.cell_area

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

    def transfer_energy_horizontally(self):
        """Transfer energy between neighboring tiles."""
        for c in self.cells:
            c.conduct_energy_horizontally()

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
        mean_height = sum(self.cells["altitude"])/self.num_cells
        self.cells["altitude"] -= mean_height

        scale = max([1, min(self.cells["altitude"])/settings.min_ground_height, max(self.cells["altitude"]) /
                     settings.max_ground_height])
        self.cells["altitude"] = self.cells["altitude"]/scale

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

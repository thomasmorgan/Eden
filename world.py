import random
import numpy as np
from cell import Cell
import settings
import math


class World():

    """ The world class is part of the simulation.
    It is composed of a number of cells that are arranged into a grid.
    """

    """ #####################
    ### CREATION METHODS ####
    ##################### """

    def __init__(self):
        """ build a world! """
        self.create_cells()
        self.create_terrain()

    def create_cells(self):
        """ create a list of the tile objects that constitute the terrain of the world """
        self.cells = []
        for y in range(settings.world_cell_height):
            for x in range(settings.world_cell_width):
                self.cells.append(Cell(x=x, y=y))

        for cell in self.cells:
            cell.north_neighbor = self.cell_at(cell.x, cell.y-1)
            cell.south_neighbor = self.cell_at(cell.x, cell.y+1)
            cell.west_neighbor = self.cell_at(cell.x-1, cell.y)
            cell.east_neighbor = self.cell_at(cell.x+1, cell.y)

    def create_terrain(self):
        """ assign ground height values to all the tiles """
        # initialize the first four cells
        x_step = settings.world_cell_width/2
        y_step = settings.world_cell_height/2
        coords = [[0, x_step], [0, y_step]]
        for x in coords[0]:
            for y in coords[1]:
                cell = self.cell_at(x=x, y=y)
                cell.land.height = self.random_ground_height()

        # now loop through all other cells
        while True:
            # halve the step size
            x_step = x_step/2
            y_step = y_step/2
            # if step size = 0 you are done
            if x_step == 0 and y_step == 0:
                break
            # if only one = 0, put it back to 1
            if x_step == 0:
                x_step = 1
            if y_step == 0:
                y_step = 1

            # calculate distance and weighting:
            distance = pow(pow(x_step, 2) + pow(y_step, 2), 0.5)
            influence = self.height_influence(distance)

            # shift diagonally to get the next cells
            coords = [[x+x_step for x in coords[0]], [y+y_step for y in coords[1]]]
            for x in coords[0]:
                for y in coords[1]:
                    cell = self.cell_at(x=x, y=y)
                    if cell.land.height is None:
                        if influence == 0:
                            cell.land.height = self.random_ground_height()
                        else:
                            neighbors = [self.cell_at(x=x+x_step, y=y+y_step),
                                         self.cell_at(x=x-x_step, y=y+y_step),
                                         self.cell_at(x=x+x_step, y=y-y_step),
                                         self.cell_at(x=x-x_step, y=y-y_step)]
                            cell.land.height = sum([n.land.height*influence for n in neighbors] +
                                                   [self.random_ground_height()*(1-4*influence)])

            # get next set of cells
            coords = self.get_coordinate_set(x_step=x_step, y_step=y_step)
            # calculate distance and weighting:
            x_influence = self.height_influence(x_step)
            y_influence = self.height_influence(y_step)

            for x in coords[0]:
                for y in coords[1]:
                    cell = self.cell_at(x=x, y=y)
                    if cell.land.height is None:
                        if x_influence == 0 and y_influence == 0:
                            cell.land.height = self.random_ground_height()
                        else:
                            y_neighbors = [self.cell_at(x=x, y=y+y_step),
                                           self.cell_at(x=x, y=y-y_step)]
                            x_neighbors = [self.cell_at(x=x+x_step, y=y),
                                           self.cell_at(x=x-x_step, y=y)]
                            cell.land.height = sum([n.land.height*x_influence for n in x_neighbors] +
                                                   [n.land.height*y_influence for n in y_neighbors] +
                                                   [self.random_ground_height()*(1-2*x_influence-2*y_influence)])
        self.normalize_terrain()

    def create_oceans(self):
        """ fill the oceans """
        heights = [t.land.height for t in self.cells]
        self.water_level = min(heights)
        water_change = 10.0

        while water_change > 0.0001:
            self.water_level += water_change
            if self.water_volume() > settings.total_water_volume:
                self.water_level -= water_change
                water_change = water_change/2

        for t in self.cells:
            t.water_depth = max(self.water_level - t.land.height, 0)

    """ #####################
    ### EXECUTION METHODS ###
    ######################"""

    def radiate_energy(self):
        """ lose thermal energy (kJ) into space.
        see:
        https://en.wikipedia.org/wiki/Stefan-Boltzmann_law
        https://en.wikipedia.org/wiki/Stefan-Boltzmann_constant
        eden/docs/thermal energy formulae.docx
         """

        time = settings.time_step_size
        area = pow(settings.cell_size, 2)
        Z = settings.stefan_boltzmann_constant*area*settings.land_emissivity/(pow(self.cells[0].land.mass, 4)*pow(settings.land_specific_heat_capacity, 4))
        Z = 3*Z*time
        for c in self.cells:
            c.land.thermal_energy = pow(Z + pow(c.land.thermal_energy, -3), -1.0/3.0)

    def absorb_energy_from_sun(self, sun):
        """ gain thermal energy (kJ) from the sun """
        time = settings.time_step_size
        max_W = pow(settings.cell_size, 2)/(4*math.pi*pow(sun.distance, 2))*sun.power
        max_E = max_W*time*(1-settings.land_albedo)
        for c in self.cells:
            c.land.thermal_energy += max_E*c.apparent_size_from_sun

    def absorb_energy_from_core(self):
        """ gain thermal energy (kJ) from within the earth """
        W = settings.world_power
        time = settings.time_step_size
        E = W*time
        e_per_cell = E / len(self.cells)
        for c in self.cells:
            c.land.thermal_energy += e_per_cell

    def conduct_energy_between_cells(self):
        """ thermal energy (kJ) is transmitted between cells

        Note that this method makes severe deviations from real physics.
        The rate of conduction is proportional to the energy difference
        and so decreases as conduction occurs. However, the proper solution
        requires integration beyond my abilities and so I have assumed that
        the rate of conduction depends only on the starting temperature difference.
        """
        time = settings.time_step_size  # (s)
        area = (settings.cell_size*settings.land_depth)  # (m^2)
        thermal_conductivity = settings.land_thermal_conductivity

        index = list(range(settings.world_cell_width*settings.world_cell_height))
        random.shuffle(index)
        for i in index:
            cell = self.cells[i]

            x_temp_diff = cell.east_neighbor.land.temperature - cell.land.temperature  # (K)
            y_temp_diff = cell.south_neighbor.land.temperature - cell.land.temperature  # (K)

            x_energy_transfer = thermal_conductivity*area*time*(x_temp_diff)/settings.cell_size  # J
            y_energy_transfer = thermal_conductivity*area*time*(y_temp_diff)/settings.cell_size  # J

            cell.land.thermal_energy = cell.land.thermal_energy + x_energy_transfer + y_energy_transfer
            cell.east_neighbor.land.thermal_energy = cell.east_neighbor.land.thermal_energy - x_energy_transfer
            cell.south_neighbor.land.thermal_energy = cell.south_neighbor.land.thermal_energy - y_energy_transfer

    def calculate_temperature(self):
        """ calculate temperature given thermal energy """
        for c in self.cells:
            c.land.calculate_temperature()

    """ #####################
    #### SUPPORT METHODS ####
    ######################"""

    def get_coordinate_set(self, x_step=1, y_step=1):
        """ Returns a list of coordinates for cells at a given granularity
        form is [[x1, x2, x3...], [y1, y2, y3...]]
        e.g, with x_step = y_step = 3, return value is:
        [[0, 3, 6...], [0, 3, 6...]]
        """
        xs = [x*x_step for x in range(settings.world_cell_width/x_step)]
        ys = [y*y_step for y in range(settings.world_cell_height/y_step)]
        return[xs, ys]

    def height_influence(self, distance):
        """ Calculate the influence of one cell on another given the distance between them """
        influence = settings.smoothness_buffer - distance*settings.smoothness_rate
        influence = max(min(influence, 5), -5)
        if influence == 5:
            influence = 1.0
        elif influence == -5:
            influence = 0.0
        else:
            influence = np.exp(influence)/(1+np.exp(influence))
        return influence/4

    def random_ground_height(self):
        """ generate a random value for ground height """
        return np.random.beta(settings.beta_a, settings.beta_b)*(settings.max_ground_height - settings.min_ground_height) + settings.min_ground_height

    def normalize_terrain(self):
        """ adjust cell heights such that the average is 0 and it fits within the specified bounds"""
        heights = [t.land.height for t in self.cells]
        mean_height = sum(heights)/len(heights)
        for t in self.cells:
            t.land.height = t.land.height - mean_height

        heights = [t.land.height for t in self.cells]

        scale = max([1, min(heights)/settings.min_ground_height, max(heights)/settings.max_ground_height])
        for t in self.cells:
            t.land.height = t.land.height/scale

    def cell_at(self, x, y):
        """ Get the cell at the specified coordinates
        the coordinates wrap around """
        while x >= settings.world_cell_width:
            x -= settings.world_cell_width
        while x < 0:
            x += settings.world_cell_width
        while y >= settings.world_cell_height:
            y -= settings.world_cell_height
        while y < 0:
            y += settings.world_cell_height

        return self.cells[x + y*settings.world_cell_width]

    def water_volume(self):
        return sum([(self.water_level - t.land.height) for t in self.cells if t.land.height < self.water_level])*pow(settings.cell_size, 2)

import random
import numpy as np
from cell import Cell
from sun import Sun
import settings


class World():

    """ #####################
    ### CREATION METHODS ####
    ######################"""

    def __init__(self):
        """ build a world! """
        self.create_cells()
        self.create_terrain()
        #self.create_oceans()
        #self.calculate_wind()

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

    def calculate_wind(self):
        """ use temperature differentials to determine the wind speed at each cell """
        for t in self.cells:
            x_diff = ((self.cell_at(t.x+1, t.y).temperature - t.temperature) + (t.temperature - self.cell_at(t.x-1, t.y).temperature))/2
            y_diff = ((self.cell_at(t.x, t.y-1).temperature - t.temperature) + (t.temperature - self.cell_at(t.x, t.y+1).temperature))/2

            t.wind = [x_diff*settings.wind_per_degree_difference, y_diff*settings.wind_per_degree_difference]
            t.wind_speed = pow(pow(x_diff, 2) + pow(y_diff, 2), 0.5)

    """ #####################
    ### EXECUTION METHODS ###
    ######################"""

    def step(self):
        """ Allow one day to pass """
        self.blow_wind()
        self.radiate_heat_into_space()
        self.absorb_heat_from_sun()
        self.absorb_heat_from_core()
        self.calculate_temperature()
        self.calculate_wind()

        print "****"
        print "polar cell: temp = {}, wind = {}".format(self.cells[0].temperature - 273, self.cells[0].wind_speed)
        half = settings.world_cell_height*settings.world_cell_width/2
        print "equatorial cell: temp = {}, wind = {}".format(self.cells[half].temperature - 273, self.cells[half].wind_speed)

    def blow_wind(self):
        """ use calculated wind speeds to transfer thermal energy between cells """
        index = list(range(settings.world_cell_width*settings.world_cell_height))
        random.shuffle(index)
        for i in index:
            cell = self.cells[i]
            # how much thermal energy remains with them
            kept_energy = (((300-abs(cell.wind[0]))*(300-abs(cell.wind[1]))) /
                           (300*300)) * cell.thermal_energy

            # how much do they gain along the x axis
            if cell.wind[0] == 0:
                wind_from_x = cell
            elif cell.wind[0] > 1:
                wind_from_x = self.cell_at(cell.x-1, cell.y)
            else:
                wind_from_x = self.cell_at(cell.x+1, cell.y)
            gained_energy_x = ((abs(cell.wind[0])*(300-abs(cell.wind[1]))) /
                               (300*300)) * wind_from_x.thermal_energy

            #how much do they gain along the y axis
            if cell.wind[1] == 0:
                wind_from_y = cell
            elif cell.wind[1] > 1:
                wind_from_y = self.cell_at(cell.x, cell.y-1)
            else:
                wind_from_y = self.cell_at(cell.x, cell.y+1)
            gained_energy_y = ((abs(cell.wind[1])*(300-abs(cell.wind[0]))) /
                               (300*300)) * wind_from_y.thermal_energy

            # how much do they gain along the diagonal
            if cell.wind[0] == 0 or cell.wind[1] == 0:
                wind_from_x_y = cell
            else:
                if cell.wind[0] > 0 and cell.wind[1] > 0:
                    wind_from_x_y = self.cell_at(cell.x-1, cell.y+1)
                elif cell.wind[0] > 0 and cell.wind[1] < 0:
                    wind_from_x_y = self.cell_at(cell.x-1, cell.y-1)
                elif cell.wind[0] < 0 and cell.wind[1] > 0:
                    wind_from_x_y = self.cell_at(cell.x+1, cell.y+1)
                elif cell.wind[0] < 0 and cell.wind[1] < 0:
                    wind_from_x_y = self.cell_at(cell.x+1, cell.y-1)
            gained_energy_x_y = ((abs(cell.wind[1])*abs(cell.wind[0])) /
                                 (300*300)) * wind_from_x_y.thermal_energy

            cell.thermal_energy = kept_energy + gained_energy_x + gained_energy_y + gained_energy_x_y

    def radiate_energy(self):
        """ lose thermal energy (kJ) into space """
        for c in self.cells:
            time = 60*60*40
            area = pow(settings.cell_size*1000, 2)
            c.land.thermal_energy -= settings.stefan_boltzmann_constant*pow(c.land.temperature, 4)*time*area/1000

    def absorb_energy_from_sun(self, sun):
        """ gain thermal energy (kJ) from the sun """
        for c in self.cells:
            c.land.thermal_energy += sun.max_solar_energy_per_cell*c.apparent_size_from_sun

    def absorb_energy_from_core(self):
        """ gain thermal energy (kJ) from within the earth """
        for c in self.cells:
            c.land.thermal_energy += settings.thermal_energy_from_core_per_day_per_cell

    def conduct_energy_between_cells(self):
        """ thermal energy (kJ) is transmitted between cells """
        index = list(range(settings.world_cell_width*settings.world_cell_height))
        random.shuffle(index)
        for i in index:
            cell = self.cells[i]

            thermal_conductivity = settings.land_thermal_conductivity

            x_temp_diff = cell.east_neighbor.land.temperature - cell.land.temperature  # (K)
            y_temp_diff = cell.south_neighbor.land.temperature - cell.land.temperature  # (K)

            time = 60*60*24  # (s)

            area = (settings.cell_size*1000*settings.land_depth*1000)  # m^2

            cell.x_energy_transfer = thermal_conductivity*area*time*(0 - x_temp_diff)/1000  # kJ
            cell.y_energy_transfer = thermal_conductivity*area*time*(0 - y_temp_diff)/1000  # kJ

            cell.east_neighbor.land.thermal_energy = cell.east_neighbor.land.thermal_energy + cell.x_energy_transfer
            cell.land.thermal_energy = cell.land.thermal_energy - cell.x_energy_transfer
            cell.south_neighbor.land.thermal_energy = cell.south_neighbor.land.thermal_energy + cell.y_energy_transfer
            cell.land.thermal_energy = cell.land.thermal_energy - cell.y_energy_transfer

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

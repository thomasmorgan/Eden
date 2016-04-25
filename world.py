import random
import numpy as np
from cell import Cell
import settings
import math
from utility import log


class World():

    """ The world class is part of the simulation.
    It is composed of a number of cells that are arranged into a grid.
    """

    """ #####################
    ### CREATION METHODS ####
    ##################### """

    def __init__(self):
        """ build a world! """
        log(">> Creating cells")
        self.create_cells()
        log(">> Distorting terrain")
        self.create_terrain()
        self.normalize_terrain()
        log(">> Creating oceans")
        self.create_oceans()

    def create_cells(self):
        """ create a list of the tile objects that constitute the terrain of the world """
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
                    self.cells.append(Cell(longitude=longitude, latitude=latitude))

        log(">> Assigning cells neighbors")
        for a in range(len(self.cells)):
            cell = self.cells[a]
            for b in range(a+1, len(self.cells)):
                c = self.cells[b]
                if math.acos(max(min(math.cos(math.radians(cell.latitude))*math.cos(math.radians(c.latitude)) +
                                 math.sin(math.radians(cell.latitude))*math.sin(math.radians(c.latitude))*math.cos(abs(math.radians(cell.longitude) - math.radians(c.longitude))),
                                 1.0),
                                 -1.0)) < 1.3*math.radians(degrees_per_cell):
                    cell.neighbors.append(c)
                    c.neighbors.append(cell)

    def create_terrain(self):
        """ assign ground height values to all the tiles """
        # see http://mathworld.wolfram.com/GreatCircle.html
        settings.n_distortions = 400
        longs = [random.choice(self.cells).longitude for _ in range(settings.n_distortions)]
        lats = [random.choice(self.cells).latitude for _ in range(settings.n_distortions)]
        heights = [5000]*len(range(settings.n_distortions))
        rates = [random.random()*3 + 3 for _ in range(settings.n_distortions)]

        for cell in self.cells:
            distances = [settings.world_radius*math.acos(
                max(min(
                    math.cos(math.radians(cell.latitude))*math.cos(math.radians(lat)) +
                    math.sin(math.radians(cell.latitude))*math.sin(math.radians(lat))*math.cos(abs(math.radians(cell.longitude) - math.radians(long))), 1.0), -1.0))
                for lat, long in zip(lats, longs)]
            hs = [h / (d/(100000*r) + 1) for h, d, r in zip(heights, distances, rates)]
            cell.land.height += sum(hs)

    def create_oceans(self):
        """ fill the oceans """
        if settings.water_init_mode == "even":
            water_mass_per_cell = settings.world_water_mass/len(self.cells)
            water_vol_per_cell = water_mass_per_cell/settings.water_density
            for cell in self.cells:
                cell.water.change_volume(water_vol_per_cell)
        elif settings.water_init_mode == "dump":
            cell = random.choice(self.cells)
            cell.water.change_volume(settings.world_water_mass/settings.water_density)

    def slosh_oceans(self):
        """ allow water to move according to gravity """
        index = range(len(self.cells))
        random.shuffle(index)
        for i in index:
            # for each cell
            cell = self.cells[i]
            if cell.water.depth > 0:
                random.shuffle(cell.neighbors)
                # get height difference with neighbors
                height_diffs = [max(0, cell.surface_height - n.surface_height) for n in cell.neighbors]

                # calculate the size and speed of a wave
                wave_height = [min(cell.water.depth, h/2) for h in height_diffs]
                wave_area = [h*settings.cell_width for h in wave_height]
                wave_speed = [min(max(pow(h, (1.0/3.0)), 1), 20) for h in wave_height]

                # hork out how far the wave goes
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
                    vol_moved = [v/(total_vol/cell.water.volume) for v in vol_moved]

                # update the cells
                cell.water.change_volume(-sum(vol_moved))
                for j in range(len(cell.neighbors)):
                    if vol_moved[j] != 0:
                        cell.neighbors[j].water.change_volume(vol_moved[j])

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
        area = settings.cell_area
        Z = settings.stefan_boltzmann_constant*area*settings.land_emissivity/(pow(self.cells[0].land.mass, 4)*pow(settings.land_specific_heat_capacity, 4))
        Z = 3*Z*time
        for c in self.cells:
            c.land.thermal_energy = pow(Z + pow(c.land.thermal_energy, -3), -1.0/3.0)

    def absorb_energy_from_sun(self, sun):
        """ gain thermal energy (kJ) from the sun """
        time = settings.time_step_size
        max_W = settings.cell_area/(4*math.pi*pow(sun.distance, 2))*sun.power
        max_E = max_W*time*(1-settings.land_albedo)

        for c in self.cells:
            c.land.thermal_energy += max_E*c.facing_sun

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
        # time = settings.time_step_size  # (s)
        # area = (settings.cell_width*settings.land_depth)  # (m^2)
        # thermal_conductivity = settings.land_thermal_conductivity

        # index = list(range(len(self.cells)))
        # random.shuffle(index)
        # for i in index:
        #     cell = self.cells[i]

        #     x_temp_diff = cell.east_neighbor.land.temperature - cell.land.temperature  # (K)
        #     y_temp_diff = cell.south_neighbor.land.temperature - cell.land.temperature  # (K)

        #     x_energy_transfer = thermal_conductivity*area*time*(x_temp_diff)/settings.cell_size  # J
        #     y_energy_transfer = thermal_conductivity*area*time*(y_temp_diff)/settings.cell_size  # J

        #     cell.land.thermal_energy = cell.land.thermal_energy + x_energy_transfer + y_energy_transfer
        #     cell.east_neighbor.land.thermal_energy = cell.east_neighbor.land.thermal_energy - x_energy_transfer
        #     cell.south_neighbor.land.thermal_energy = cell.south_neighbor.land.thermal_energy - y_energy_transfer

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
        return sum([(self.water_level - t.land.height) for t in self.cells if t.land.height < self.water_level])*settings.cell_area

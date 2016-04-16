import random
import numpy as np
from tile import Tile
from sun import Sun
import settings


class World():

    """ #####################
    ### CREATION METHODS ####
    ######################"""

    def __init__(self):
        """ build a world! """
        self.create_tiles()
        self.create_terrain()
        self.create_sun()
        self.create_oceans()
        self.calculate_wind()

    def create_tiles(self):
        """ create a list of the tile objects that constitute the terrain of the world """
        self.tiles = []
        for y in range(settings.world_tile_height):
            for x in range(settings.world_tile_width):
                self.tiles.append(Tile(x=x, y=y))

    def create_terrain(self):
        """ assign ground height values to all the tiles """
        # initialize the first four tiles
        x_step = settings.world_tile_width/2
        y_step = settings.world_tile_height/2
        coords = [[0, x_step], [0, y_step]]
        for x in coords[0]:
            for y in coords[1]:
                tile = self.tile_at(x=x, y=y)
                tile.ground_height = self.random_ground_height()

        # now loop through all other tiles
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

            # shift diagonally to get the next tiles
            coords = [[x+x_step for x in coords[0]], [y+y_step for y in coords[1]]]
            for x in coords[0]:
                for y in coords[1]:
                    tile = self.tile_at(x=x, y=y)
                    if tile.ground_height is None:
                        if influence == 0:
                            tile.ground_height = self.random_ground_height()
                        else:
                            neighbors = [self.tile_at(x=x+x_step, y=y+y_step),
                                         self.tile_at(x=x-x_step, y=y+y_step),
                                         self.tile_at(x=x+x_step, y=y-y_step),
                                         self.tile_at(x=x-x_step, y=y-y_step)]
                            tile.ground_height = sum([n.ground_height*influence for n in neighbors] +
                                                     [self.random_ground_height()*(1-4*influence)])

            # get next set of tiles
            coords = self.get_coordinate_set(x_step=x_step, y_step=y_step)
            # calculate distance and weighting:
            x_influence = self.height_influence(x_step)
            y_influence = self.height_influence(y_step)

            for x in coords[0]:
                for y in coords[1]:
                    tile = self.tile_at(x=x, y=y)
                    if tile.ground_height is None:
                        if x_influence == 0 and y_influence == 0:
                            tile.ground_height = self.random_ground_height()
                        else:
                            y_neighbors = [self.tile_at(x=x, y=y+y_step),
                                           self.tile_at(x=x, y=y-y_step)]
                            x_neighbors = [self.tile_at(x=x+x_step, y=y),
                                           self.tile_at(x=x-x_step, y=y)]
                            tile.ground_height = sum([n.ground_height*x_influence for n in x_neighbors] +
                                                     [n.ground_height*y_influence for n in y_neighbors] +
                                                     [self.random_ground_height()*(1-2*x_influence-2*y_influence)])
        self.normalize_terrain()

    def create_sun(self):
        """ create the sun object """
        self.sun = Sun()

    def create_oceans(self):
        """ fill the oceans """
        heights = [t.ground_height for t in self.tiles]
        self.water_level = min(heights)
        water_change = 10.0

        while water_change > 0.0001:
            self.water_level += water_change
            if self.water_volume() > settings.total_water_volume:
                self.water_level -= water_change
                water_change = water_change/10

        for t in self.tiles:
            t.water_depth = max(self.water_level - t.ground_height, 0)

    def calculate_wind(self):
        """ use temperature differentials to determine the wind speed at each tile """
        for t in self.tiles:
            x_diff = ((self.tile_at(t.x+1, t.y).temperature - t.temperature) + (t.temperature - self.tile_at(t.x-1, t.y).temperature))/2
            y_diff = ((self.tile_at(t.x, t.y-1).temperature - t.temperature) + (t.temperature - self.tile_at(t.x, t.y+1).temperature))/2

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
        print "polar tile: temp = {}, wind = {}".format(self.tiles[0].temperature - 273, self.tiles[0].wind_speed)
        half = settings.world_tile_height*settings.world_tile_width/2
        print "equatorial tile: temp = {}, wind = {}".format(self.tiles[half].temperature - 273, self.tiles[half].wind_speed)

    def blow_wind(self):
        """ use calculated wind speeds to transfer thermal energy between tiles """
        index = list(range(settings.world_tile_width*settings.world_tile_height))
        random.shuffle(index)
        for i in index:
            tile = self.tiles[i]
            # how much thermal energy remains with them
            kept_energy = (((300-abs(tile.wind[0]))*(300-abs(tile.wind[1]))) /
                           (300*300)) * tile.thermal_energy

            # how much do they gain along the x axis
            if tile.wind[0] == 0:
                wind_from_x = tile
            elif tile.wind[0] > 1:
                wind_from_x = self.tile_at(tile.x-1, tile.y)
            else:
                wind_from_x = self.tile_at(tile.x+1, tile.y)
            gained_energy_x = ((abs(tile.wind[0])*(300-abs(tile.wind[1]))) /
                               (300*300)) * wind_from_x.thermal_energy

            #how much do they gain along the y axis
            if tile.wind[1] == 0:
                wind_from_y = tile
            elif tile.wind[1] > 1:
                wind_from_y = self.tile_at(tile.x, tile.y-1)
            else:
                wind_from_y = self.tile_at(tile.x, tile.y+1)
            gained_energy_y = ((abs(tile.wind[1])*(300-abs(tile.wind[0]))) /
                               (300*300)) * wind_from_y.thermal_energy

            # how much do they gain along the diagonal
            if tile.wind[0] == 0 or tile.wind[1] == 0:
                wind_from_x_y = tile
            else:
                if tile.wind[0] > 0 and tile.wind[1] > 0:
                    wind_from_x_y = self.tile_at(tile.x-1, tile.y+1)
                elif tile.wind[0] > 0 and tile.wind[1] < 0:
                    wind_from_x_y = self.tile_at(tile.x-1, tile.y-1)
                elif tile.wind[0] < 0 and tile.wind[1] > 0:
                    wind_from_x_y = self.tile_at(tile.x+1, tile.y+1)
                elif tile.wind[0] < 0 and tile.wind[1] < 0:
                    wind_from_x_y = self.tile_at(tile.x+1, tile.y-1)
            gained_energy_x_y = ((abs(tile.wind[1])*abs(tile.wind[0])) /
                                 (300*300)) * wind_from_x_y.thermal_energy

            tile.thermal_energy = kept_energy + gained_energy_x + gained_energy_y + gained_energy_x_y

    def radiate_heat_into_space(self):
        """ lose thermal energy into space """
        for t in self.tiles:
            t.thermal_energy = t.thermal_energy - (settings.thermal_energy_radiated_per_day_per_kelvin*pow(t.temperature, 4))*(1-settings.atmosphere_albedo)

    def absorb_heat_from_sun(self):
        """ gain thermal energy from the sun """
        for t in self.tiles:
            t.thermal_energy = t.thermal_energy + t.solar_energy_per_day

    def absorb_heat_from_core(self):
        """ gain thermal energy from within the earth """
        for t in self.tiles:
            t.thermal_energy = t.thermal_energy + settings.thermal_energy_from_core_per_day_per_tile

    def calculate_temperature(self):
        """ calculate temperature given thermal energy """
        for t in self.tiles:
            t.calculate_temperature()

    """ #####################
    #### SUPPORT METHODS ####
    ######################"""

    def get_coordinate_set(self, x_step=1, y_step=1):
        """ Returns a list of coordinates for tiles at a given granularity
        form is [[x1, x2, x3...], [y1, y2, y3...]]
        e.g, with x_step = y_step = 3, return value is:
        [[0, 3, 6...], [0, 3, 6...]]
        """
        xs = [x*x_step for x in range(settings.world_tile_width/x_step)]
        ys = [y*y_step for y in range(settings.world_tile_height/y_step)]
        return[xs, ys]

    def height_influence(self, distance):
        """ Calculate the influence of one tile on another given the distance between them """
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
        """ adjust tile heights such that the average is 0 and it fits within the specified bounds"""
        heights = [t.ground_height for t in self.tiles]
        mean_height = sum(heights)/len(heights)
        for t in self.tiles:
            t.ground_height = t.ground_height - mean_height

        heights = [t.ground_height for t in self.tiles]

        scale = max([1, min(heights)/settings.min_ground_height, max(heights)/settings.max_ground_height])
        for t in self.tiles:
            t.ground_height = t.ground_height/scale

    def tile_at(self, x, y):
        """ Get the tile at the specified coordinates
        the coordinates wrap around """
        while x >= settings.world_tile_width:
            x -= settings.world_tile_width
        while x < 0:
            x += settings.world_tile_width
        while y >= settings.world_tile_height:
            y -= settings.world_tile_height
        while y < 0:
            y += settings.world_tile_height

        return self.tiles[x + y*settings.world_tile_width]

    """ #####################
    ##### PRINT METHODS #####
    ######################"""

    def print_tile_heights(self):
        print "###################"
        print "Tile heights:"
        print "max: {}".format(max([tile.ground_height for tile in self.tiles]))
        print "min: {}".format(min([tile.ground_height for tile in self.tiles]))
        for r in self.tiles:
            print [int(t.ground_height) for t in r]
        print "###################"

    def print_ocean_depths(self):
        print "###################"
        print "Ocean Depths:"
        print "max: {}".format(max([tile.water_depth for tile in self.tiles]))
        print "min: {}".format(min([tile.water_depth for tile in self.tiles]))
        for r in self.tiles:
            print [int(t.water_depth) for t in r]
        print "###################"

    def print_tile_coords(self):
        print "###################"
        print "Tile coords:"
        for i in range(self.num_tiles):
            print [(str(tile.xcor) + ":" + str(tile.ycor)) for tile in self.tiles[i*self.num_tiles:((i+1)*self.num_tiles)]]
        print "###################"

    def print_tile_temperatures(self):
        print "###################"
        print "Tile temperature:"
        print [tile.temperature for tile in self.tiles]
        print "###################"

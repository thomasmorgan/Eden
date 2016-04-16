import random
from scipy import stats
import numpy as np
from tile import Tile
import settings
import math


class World():

    def __init__(self):
        self.create_tiles()
        self.create_terrain()
        self.create_sun()
        #self.create_oceans()
        self.calculate_temperature()
        self.calculate_wind()

    def create_tiles(self):
        self.tiles = []
        for y in range(settings.world_tile_height):
            for x in range(settings.world_tile_width):
                self.tiles.append(Tile(x=x, y=y))

    def create_sun(self):
        self.sun = Sun()

    def get_coordinate_set(self, x_step=1, y_step=1):
        xs = [x*x_step for x in range(settings.world_tile_width/x_step)]
        ys = [y*y_step for y in range(settings.world_tile_height/y_step)]
        return[xs, ys]

    def create_terrain(self):
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

    def height_influence(self, distance):
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
        return np.random.beta(settings.beta_a, settings.beta_b)*(settings.max_ground_height - settings.min_ground_height) + settings.min_ground_height

    def normalize_terrain(self):
        # reset average tile height to be 0 and scale heights within boundaries.
        heights = [t.ground_height for t in self.tiles]
        mean_height = sum(heights)/len(heights)
        for t in self.tiles:
            t.ground_height = t.ground_height - mean_height

        heights = [t.ground_height for t in self.tiles]

        scale = max([1, min(heights)/settings.min_ground_height, max(heights)/settings.max_ground_height])
        for t in self.tiles:
            t.ground_height = t.ground_height/scale

    def distort_terrain(self, type="cone", nsteps=1, tile=None, change=None, scope=None, random_walk=False, step_size=5):

        if random_walk is False:
            if tile is None:
                focal_tiles = np.random.choice(self.tiles, size=nsteps, replace=True)
            else:
                focal_tiles = [tile]*nsteps
        else:
            if tile is None:
                focal_tiles = [random.choice(self.tiles)]
            else:
                focal_tiles = [tile]
            for i in range(nsteps-1):
                focal_tiles.append(self.random_step_from(focal_tiles[-1], step_size=step_size))

        if scope is None:
            focal_ranges = np.random.normal(0.0, 2, nsteps)
            focal_ranges = [abs(f)+1 for f in focal_ranges]
        else:
            focal_ranges = [scope]*nsteps

        if change is None:
            direction_of_change = [-1]*0 + [1]*9
            focal_changes = [r*(random.random()*5)*random.choice(direction_of_change) for r in focal_ranges]
        else:
            focal_changes = [change]*nsteps

        if (type == "cone"):
            for t in self.tiles:
                distances = [t.distance_from(t2) for t2 in focal_tiles]
                local_change = [c - d*(c/r) for c, d, r in zip(focal_changes, distances, focal_ranges) if d < r]
                t.height += sum(local_change)
        elif (type == "circle"):
            for t in self.tiles:
                distances = [t.distance_from(t2) for t2 in focal_tiles]
                local_change = [c for c, d, r in zip(focal_changes, distances, focal_ranges) if d < r]
                t.height += sum(local_change)
        elif (type == "reciprocal"):
            for t in self.tiles:
                distances = [t.distance_from(t2) for t2 in focal_tiles]
                local_change = [c/((d/pow(r, 2))+1) for c, d, r in zip(focal_changes, distances, focal_ranges)]
                t.height += sum(local_change)
        elif (type == "normal"):
            for t in self.tiles:
                distances = [t.distance_from(t2) for t2 in focal_tiles]
                d2 = [d for d, r in zip(distances, focal_ranges) if d < r]
                c2 = [c for c, r, d in zip(focal_changes, focal_ranges, distances) if d < r]
                r2 = [r for r, d in zip(focal_ranges, distances) if d < r]
                local_change = [(c/stats.norm.pdf(0, loc=0, scale=r/3))*stats.norm.pdf(d, loc=0, scale=r/3) for c, d, r in zip(c2, d2, r2)]
                t.height += sum(local_change)
        else:
            raise Exception("Unknown terrain distort type: {}".format(type))

        self.normalize_terrain()

    def create_oceans(self):
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

    def calculate_temperature(self):
        for t in self.tiles:
            t.solar_energy = math.cos(abs(t.y - (settings.world_tile_height-1)/2.0)/((settings.world_tile_height-1)/2.0)*(math.pi/2))
            t.temp = t.solar_energy

    def calculate_wind(self):
        for t in self.tiles:
            x_diff = (self.tile_at(t.x+1, t.y).temp - t.temp) + (t.temp - self.tile_at(t.x-1, t.y).temp)
            y_diff = (self.tile_at(t.x, t.y+1).temp - t.temp) + (t.temp - self.tile_at(t.x, t.y-1).temp)

            t.wind = [x_diff, y_diff]
            t.wind_speed = pow(pow(x_diff, 2) + pow(y_diff, 2), 0.5)

        ys = [t.wind[0] for t in self.tiles]
        print max(ys)
        print sum(ys)

    def water_volume(self):
        return sum([(self.water_level - t.ground_height) for t in self.tiles if t.ground_height < self.water_level])

    def at_threshold(self):
        heights = [t.height for t in self.tiles]
        min_height = min(heights)
        max_height = max(heights)
        if (min_height == self.min_tile_height or max_height == self.max_tile_height):
            return True
        else:
            return False

    def random_step_from(self, tile=None, step_size=None):
        old_x = tile.xcor
        old_y = tile.ycor

        new_x = old_x + random.randint(1, step_size)*random.choice([1, -1])
        new_y = old_y + random.randint(1, step_size)*random.choice([1, -1])

        if new_x >= self.num_tiles:
            new_x -= self.num_tiles
        elif new_x < 0:
            new_x += self.num_tiles
        if new_y >= self.num_tiles:
            new_y -= self.num_tiles
        elif new_y < 0:
            new_y += self.num_tiles

        return self.tile_at(new_x, new_y)

    def tile_at(self, x, y):
        while x >= settings.world_tile_width:
            x -= settings.world_tile_width
        while x < 0:
            x += settings.world_tile_width
        while y >= settings.world_tile_height:
            y -= settings.world_tile_height
        while y < 0:
            y += settings.world_tile_height

        return self.tiles[x + y*settings.world_tile_width]

    def step(self):
        index = list(range(settings.world_tile_width*settings.world_tile_height))
        random.shuffle(index)
        for i in index:
            tile = self.tiles[i]
            if tile.wind[0] == 0:
                wind_from_x = tile
            elif tile.wind[0] > 1:
                wind_from_x = self.tile_at(tile.x-1, tile.y)
            else:
                wind_from_x = self.tile_at(tile.x+1, tile.y)

            if tile.wind[1] == 0:
                wind_from_y = tile
            elif tile.wind[1] > 1:
                wind_from_y = self.tile_at(tile.x, tile.y-1)
            else:
                wind_from_y = self.tile_at(tile.x, tile.y+1)

            thermal_inertia = 0.01
            tile.temp = (wind_from_x.temp*abs(tile.wind[0]) + wind_from_y.temp*abs(tile.wind[1]) + tile.temp*thermal_inertia)/(thermal_inertia + abs(tile.wind[0]) + abs(tile.wind[1]))

        self.calculate_wind()

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

    def print_tile_distances_from(self, focal_tile=None):
        print "###################"
        print "Tile distances:"
        for i in range(self.num_tiles):
            print [int(tile.distance_from(focal_tile)) for tile in self.tiles[i*self.num_tiles:((i+1)*self.num_tiles)]]
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

import random
from scipy import stats
import numpy as np
import math
from tile import Tile
from threading import Thread


class Map():

    tiles = None
    num_tiles = None
    min_tile_height = -50
    max_tile_height = 50

    def __init__(self, total_width=None, num_tiles=None):
        self.num_tiles = num_tiles
        self.total_width = total_width

    def create_tiles(self):
        self.tiles = []
        for i in range(pow(self.num_tiles, 2)):
            xcor = (i % self.num_tiles)
            ycor = int(i/float(self.num_tiles))
            self.tiles.append(Tile(map=self, x=xcor, y=ycor))

    def create_terrain(self, smoothness=1):

        done_tiles = []

        # initialize four tiles
        coords = [0, self.num_tiles/2]
        for x in coords:
            for y in coords:
                tile = self.tile_at(x=x, y=y)
                tile.height = self.random_tile_height()
                done_tiles.append(tile)

        # set up the step size
        step_size = self.num_tiles/4

        while (step_size >= 1):

            for stage in range(2):

                nt = len(done_tiles)
                for i in range(nt):
                    t = done_tiles[i]
                    if stage == 0:
                        new_tile = self.tile_at(x=t.xcor + step_size, y=t.ycor + step_size)
                        nearest_four = [t,
                                        self.tile_at(x=t.xcor, y=t.ycor + 2*step_size),
                                        self.tile_at(x=t.xcor + 2*step_size, y=t.ycor),
                                        self.tile_at(x=t.xcor + 2*step_size, y=t.ycor + 2*step_size)]
                    else:
                        new_tile = self.tile_at(x=t.xcor + step_size, y=t.ycor)
                        nearest_four = [t,
                                        self.tile_at(x=new_tile.xcor + step_size, y=new_tile.ycor),
                                        self.tile_at(x=new_tile.xcor, y=new_tile.ycor + step_size),
                                        self.tile_at(x=new_tile.xcor, y=new_tile.ycor - step_size)]
                    # collate the height of the 4 tiles
                    four_heights = [n.height for n in nearest_four]
                    # assign the new tile a height
                    mean_weight = 1-(stats.norm.cdf(new_tile.distance_from(t), loc=0, scale=(smoothness*self.num_tiles/2))*2-1)
                    new_tile.height = (sum(four_heights)/len(four_heights)*mean_weight +
                                              (1-mean_weight)*self.random_tile_height())
                    done_tiles.append(new_tile)

            step_size = step_size/2

        for tile in self.tiles:
            tile.height = pow(abs(tile.height), 2)*(tile.height/abs(tile.height))

        self.normalize_terrain()

    def random_tile_height(self):
        height_range = self.max_tile_height - self.min_tile_height
        mean_height = (self.max_tile_height - self.min_tile_height)/2 + self.min_tile_height
        return np.random.normal(loc=mean_height, scale=height_range/3)

    def normalize_terrain(self):
        # reset average tile height to be 0 and scale heights within boundaries.
        heights = [s.height for s in self.tiles]
        mean_height = sum(heights)/len(heights)
        for t in self.tiles:
            t.height = t.height - mean_height

        heights = [s.height for s in self.tiles]

        scale = max([1, min(heights)/self.min_tile_height, max(heights)/self.max_tile_height])
        for t in self.tiles:
            t.height = t.height/scale

        vol_water = sum([t.height for t in self.tiles if t.height < 0])

        print "vol water is now: {}".format(vol_water)

    def distort_terrain(self, type="cone", nsteps=1, tile=None, change=None, scope=None, random_walk=False):

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
                focal_tiles.append(self.random_step_from(focal_tiles[-1]))

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
                local_change = [c/((d/r)+1) for c, d, r in zip(focal_changes, distances, focal_ranges)]
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

    def add_water(self):
        water_level = 0
        for t in self.tiles:
            if t.height < water_level:
                t.water_depth = water_level - t.height
            else:
                t.water_depth = 0

    def at_threshold(self):
        heights = [t.height for t in self.tiles]
        min_height = min(heights)
        max_height = max(heights)
        if (min_height == self.min_tile_height or max_height == self.max_tile_height):
            return True
        else:
            return False

    def random_step_from(self, tile=None):
        old_x = tile.xcor
        old_y = tile.ycor

        new_x = old_x + random.randint(1, 5)*random.choice([1, -1])
        new_y = old_y + random.randint(1, 5)*random.choice([1, -1])

        if new_x >= self.num_tiles:
            new_x -= self.num_tiles
        elif new_x < 0:
            new_x += self.num_tiles
        if new_y >= self.num_tiles:
            new_y -= self.num_tiles
        elif new_y < 0:
            new_y += self.num_tiles

        return self.tile_at(new_x, new_y)

    def tile_at(self, x=None, y=None):
        if x >= self.num_tiles:
            x -= self.num_tiles
        elif x < 0:
            x += self.num_tiles
        if y >= self.num_tiles:
            y -= self.num_tiles
        elif y < 0:
            y += self.num_tiles

        return self.tiles[x + y*self.num_tiles]

    def print_tile_heights(self):
        print "###################"
        print "Tile heights:"
        print "max: {}".format(max([tile.height for tile in self.tiles]))
        print "min: {}".format(min([tile.height for tile in self.tiles]))
        for i in range(self.num_tiles):
            print [int(tile.height) for tile in self.tiles[i*self.num_tiles:((i+1)*self.num_tiles)]]
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

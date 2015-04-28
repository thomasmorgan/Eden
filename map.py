import random
from scipy import stats as stats
import numpy as np
import math
from tile import Tile
from threading import Thread


class Map():

    tiles = None
    num_tiles = None

    def __init__(self, total_width=None, num_tiles=None):
        self.num_tiles = num_tiles
        self.total_width = total_width

    def create_tiles(self):
        self.tiles = []
        for i in range(pow(self.num_tiles, 2)):
            xcor = (i % self.num_tiles)
            ycor = int(i/float(self.num_tiles))
            self.tiles.append(Tile(map=self, x=xcor, y=ycor))

    def distort_terrain_cone(self, nsteps=1, tile=None, change=None, scope=None):

        if tile is None:
            focal_tiles = np.random.choice(self.tiles, size=nsteps, replace=True)
        else:
            focal_tiles = [tile]*nsteps

        #if change is None:
            #focal_changes = np.random.rand(nsteps)*40 - 20
        #else:
            #focal_changes = [change]*nsteps
        if scope is None:
            focal_ranges = np.random.normal(0.0, 4, nsteps)
            focal_ranges = [abs(f)+1 for f in focal_ranges]
        else:
            focal_ranges = [scope]*nsteps

        direction_of_change = [-1] + [1]*9
        if change is None:
            focal_changes = [r*(random.random()*3)*random.choice(direction_of_change) for r in focal_ranges]
        else:
            focal_changes = [change]*nsteps

        for t in self.tiles:
            distances = [t.distance_from(t2) for t2 in focal_tiles]
            local_change = [c - d*(c/r) for c, d, r in zip(focal_changes, distances, focal_ranges) if d < r]
            #local_change = [(c/((d/r)+1)) for c, d, r in zip(focal_changes, distances, focal_ranges)]
            t.ground_height += sum(local_change)

        # reset average tile height to be 0
        ground_heights = [tile.ground_height for tile in self.tiles]
        mean_ground_height = sum(ground_heights)/len(ground_heights)
        for tile in self.tiles:
            tile.ground_height = tile.ground_height - mean_ground_height

        # scale height to range from -50 to 50
        ground_heights = [tile.ground_height for tile in self.tiles]

        scale = max([1, abs(min(ground_heights))/50.0, abs(max(ground_heights))/50.0])
        if (scale > 1):
            for tile in self.tiles:
                tile.ground_height = tile.ground_height/scale

    def add_water(self):
        water_level = 0
        for t in self.tiles:
            if t.ground_height < water_level:
                t.water_depth = water_level - t.ground_height
            else:
                t.water_depth = 0

    def print_tile_heights(self):
        print "###################"
        print "Tile heights:"
        print "max: {}".format(max([tile.ground_height for tile in self.tiles]))
        print "min: {}".format(min([tile.ground_height for tile in self.tiles]))
        for i in range(self.num_tiles):
            print [int(tile.ground_height) for tile in self.tiles[i*self.num_tiles:((i+1)*self.num_tiles)]]
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

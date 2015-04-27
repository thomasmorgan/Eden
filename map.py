import random
from scipy import stats as stats
import math
from tile import Tile


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

    def generate_terrain(self, nsteps=1, tile=None, change=None, rang=None):

        # for each step add a focal distortion
        for i in range(nsteps):
            focal_change_in_height = change
            range_of_change = rang
            focal_tile = tile

            if focal_tile is None:
                focal_tile = random.choice(self.tiles)
            if focal_change_in_height is None:
                focal_change_in_height = random.random()*40 - 20
            if range_of_change is None:
                range_of_change = random.random()*9.0 + 1

            for t in self.tiles:
                distance = t.distance_from(focal_tile)
                density = stats.norm.pdf(distance, loc=0, scale=range_of_change)
                local_change_in_height = density * (focal_change_in_height/stats.norm.pdf(0, loc=0, scale=range_of_change))
                t.ground_height = t.ground_height + local_change_in_height
                # print "#####"
                # print "focal change in height is {}".format(focal_change_in_height)
                # print "range of change is {}".format(range_of_change)
                # print "tile is {} from focus".format(distance)
                # print "density here is {}".format(density)
                # print "therefore local height change is {}".format(local_change_in_height)
                # print "########"

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

    def print_tile_heights(self):
        print "###################"
        print "Tile heights:"
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

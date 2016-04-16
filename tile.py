import math
import settings


class Tile():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ground_height = None
        self.water_depth = 0.0
        self.solar_energy = None
        self.temp = None
        self.wind = None
        self.wind_speed = None

        self.x_min = x*settings.tile_width + settings.map_border
        self.y_min = y*settings.tile_height + settings.map_border
        self.x_max = (x+1)*settings.tile_width + settings.map_border
        self.y_max = (y+1)*settings.tile_height + settings.map_border

    def gradient(self):
        neighbors = [self.map.tile_at(x=self.xcor+1, y=self.ycor),
                     self.map.tile_at(x=self.xcor, y=self.ycor+1),
                     self.map.tile_at(x=self.xcor-1, y=self.ycor),
                     self.map.tile_at(x=self.xcor, y=self.ycor-1)]
        diffs = [abs(t.height-self.height) for t in neighbors]
        return sum(diffs)/len(diffs)

    def calculate_temperature(self):
        suns_heat = self.map.sun_strength*math.sin(self.ycor/float(self.map.num_tiles)*math.pi)
        if self.water_depth == 0:
            reduction_due_to_water = 0
        else:
            reduction_due_to_water = (1-(1/(1+float(self.water_depth)/3)))*0.5
        self.temperature = self.base_temp + self.temp_from_sun*suns_heat*(1-reduction_due_to_water)
        if self.height > self.map.water_level:
            self.temperature -= (self.height - self.map.water_level)*(self.map.degrees_per_altitude)

    def distance_from(self, other_tile=None, x=None, y=None):
        if other_tile is not None:
            d_x = other_tile.xcor - self.xcor
            d_y = other_tile.ycor - self.ycor
        else:
            d_x = x - self.xcor
            d_y = y - self.ycor

        if (d_x > (self.map.num_tiles/2.0)):
            d_x = d_x - self.map.num_tiles
        elif (d_x < -(self.map.num_tiles/2.0)):
            d_x = d_x + self.map.num_tiles
        if (d_y > (self.map.num_tiles/2.0)):
            d_y = d_y - self.map.num_tiles
        elif (d_y < -(self.map.num_tiles/2.0)):
            d_y = d_y + self.map.num_tiles

        d = pow((pow(d_x, 2) + pow(d_y, 2)), 0.5)

        return d

class Tile():

    xcor = None
    ycor = None
    height = 0.0
    water_depth = 0.0
    rectangle = None

    def __init__(self, map=None, x=None, y=None, height=0.0):
        self.map = map
        self.xcor = x
        self.ycor = y
        self.height = float(height)
        if (self.height < self.map.min_tile_height):
            self.height = self.map.min_tile_height
        if (self.height > self.map.max_tile_height):
            self.height = self.map.max_tile_height

        if (None in [self.xcor, self.ycor]):
            raise Exception("Tile {} has not been properly initialized").format(self)

    def color(self, water=True, gradient=False):
        if not gradient:
            if self.water_depth == 0 or water is False:
                col_min = [50, 20, 4]
                col_max = [255, 255, 255]
                p = (self.height - self.map.min_tile_height)/(self.map.max_tile_height - self.map.min_tile_height)
            else:
                col_min = [153, 204, 255]
                col_max = [0, 0, 40]
                p = self.water_depth/(self.map.max_tile_height - self.map.min_tile_height)
                if p > 1:
                    p = 1
        else:
            col_min = [255, 255, 255]
            col_max = [255, 0, 0]
            p = min([self.gradient()/10, 1])

        p = round(p, 1)
        q = 1-p

        col = [int(q*col_min[0] + p*col_max[0]), int(q*col_min[1] + p*col_max[1]), int(q*col_min[2] + p*col_max[2])]
        return '#%02X%02X%02X' % (col[0], col[1], col[2])

    def gradient(self):
        neighbors = [self.map.tile_at(x=self.xcor+1, y=self.ycor),
                     self.map.tile_at(x=self.xcor, y=self.ycor+1),
                     self.map.tile_at(x=self.xcor-1, y=self.ycor),
                     self.map.tile_at(x=self.xcor, y=self.ycor-1)]
        diffs = [abs(t.height-self.height) for t in neighbors]
        return sum(diffs)/len(diffs)

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

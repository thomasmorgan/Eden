class Tile():

    xcor = None
    ycor = None
    ground_height = None

    def __init__(self, map=None, x=None, y=None, ground_height=0.0):
        self.map = map
        self.xcor = x
        self.ycor = y
        self.ground_height = float(ground_height)
        if (self.ground_height < -50):
            self.ground_height = -50
        if (self.ground_height > 50):
            self.ground_height = 50

        if (None in [self.xcor, self.ycor]):
            raise Exception("Tile {} has not been properly initialized").format(self)

    def color(self):
        col_min = [59, 19, 9]
        col_max = [245, 222, 179]

        p = (self.ground_height+50)/100.0
        q = 1-p

        col = [int(q*col_min[0] + p*col_max[0]), int(q*col_min[1] + p*col_max[1]), int(q*col_min[2] + p*col_max[2])]
        return '#%02X%02X%02X' % (col[0], col[1], col[2])

    def distance_from(self, other_tile):
        #print "-----------------------------"
        #print "my coords: " + str(self.xcor) + ":" + str(self.ycor)
        #print "their coords: " + str(other_tile.xcor) + ":" + str(other_tile.ycor)
        d_x = other_tile.xcor - self.xcor
        d_y = other_tile.ycor - self.ycor

        #print "vector: " + str([d_x, d_y])

        if (d_x > (self.map.num_tiles/2.0)):
            d_x = d_x - self.map.num_tiles
        elif (d_x < -(self.map.num_tiles/2.0)):
            d_x = d_x + self.map.num_tiles
        elif (d_y > (self.map.num_tiles/2.0)):
            d_y = d_y - self.map.num_tiles
        if (d_y < -(self.map.num_tiles/2.0)):
            d_y = d_y + self.map.num_tiles

        #print "shortest vector: " + str([d_x, d_y])

        d = pow((pow(d_x, 2) + pow(d_y, 2)), 0.5)

        #print d
        return d

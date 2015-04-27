class Tile():

    xcor = None
    ycor = None
    size = None
    ground_height = None

    def __init__(self, x=None, y=None, size=None, ground_height=20):
        self.xcor = x
        self.ycor = y
        self.size = size
        self.ground_height = ground_height
        if (self.ground_height > 255):
            self.ground_height = 255

        if (None in [self.xcor, self.ycor, self.size]):
            raise Exception("Tile {} has not been properly initialized").format(self)

    def color(self):
        r_base = 59
        g_base = 19
        b_base = 9
        r = int(r_base + self.ground_height*(1-(r_base/255.0)))
        g = int(g_base + self.ground_height*(1-(g_base/255.0)))
        b = int(b_base + self.ground_height*(1-(b_base/255.0)))
        return '#%02X%02X%02X' % (r, g, b)

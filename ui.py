from Tkinter import *
import settings
from utility import log


class UI():

    """ The UI class manages the buttons, map and tiles.
    The latter two are visual depictions of the world and cells respectively
    """

    def __init__(self, master, app, frame):
        """ create the window """
        self.master = master
        self.app = app
        self.frame = frame
        self.world = self.app.simulation.world
        self.cells = self.world.cells

        self.add_buttons()
        self.add_map()

        log(">> Creating tiles")
        self.create_tiles()
        log(">> Painting tiles")
        self.paint_tiles()

    def add_buttons(self):
        """ add buttons to the frame """
        ground_button = Button(self.frame, text="TERRA", fg="red", command=self.draw_terrain)
        ground_button.pack(side=LEFT)
        heat_button = Button(self.frame, text="HEAT", fg="red", command=self.draw_heat)
        heat_button.pack(side=LEFT)
        step_button = Button(self.frame, text="STEP", fg="red", command=self.app.step)
        step_button.pack(side=LEFT)
        quit_button = Button(self.frame, text="QUIT", fg="red", command=self.frame.quit)
        quit_button.pack(side=LEFT)

    def add_map(self):
        """ add a blank map """
        self.map = Canvas(self.master, width=settings.map_width + 2*settings.map_border,
                          height=settings.map_height + 2*settings.map_border, bg="black",
                          highlightthickness=0)
        self.map.pack(side=LEFT)

    def create_tiles(self):
        """ create blank tiles """
        self.map.delete("all")
        self.tiles = []
        for cell in self.cells:
            n_in_row = len([c for c in self.cells if c.latitude == cell.latitude])
            x_start = (settings.map_width/2.0) - (n_in_row/2.0)*settings.tile_width
            y_start = (cell.latitude/settings.cell_degree_width)*settings.tile_height

            self.tiles.append(self.map.create_rectangle(
                x_start + (cell.longitude/360.0)*n_in_row*settings.tile_width,
                y_start,
                x_start + (cell.longitude/360.0)*n_in_row*settings.tile_width + settings.tile_width + 1,
                y_start + settings.tile_height,
                fill="yellow",
                outline=""))

    def paint_tiles(self):
        """ color the tiles """
        for x in range(len(self.tiles)):
            self.map.itemconfigure(self.tiles[x], fill=self.cell_color(self.cells[x]))

    def cell_color(self, cell):
        """ Work out what color a tile should be depending on the cell it is
        depicting and the draw_mode parameter.
        """
        if settings.draw_mode == "terrain":
            if cell.water_depth == 0:
                col_min = [50, 20, 4]
                col_max = [255, 255, 255]
                p = (cell.land.height - settings.min_ground_height)/(settings.max_ground_height - settings.min_ground_height)
            else:
                col_min = [153, 204, 255]
                col_max = [0, 0, 40]
                p = cell.water_depth/(settings.max_ground_height - settings.min_ground_height)
                if p > 1:
                    p = 1
        elif settings.draw_mode == "heat":
            col_min = [82, 219, 255]
            col_max = [255, 66, 0]
            p = max(min((cell.land.temperature-200)/200, 1), 0)
        elif settings.draw_mode == "wind":
            col_min = [0, 0, 0]
            col_max = [255, 255, 255]
            p = min(cell.wind_speed, 10)/10
        q = 1-p
        col = [int(q*col_min[0] + p*col_max[0]), int(q*col_min[1] + p*col_max[1]), int(q*col_min[2] + p*col_max[2])]
        return '#%02X%02X%02X' % (col[0], col[1], col[2])

    def draw_terrain(self):
        """ paint map by altitude """
        settings.draw_mode = "terrain"
        self.paint_tiles()

    def draw_heat(self):
        """ paint map by land temperature """
        settings.draw_mode = "heat"
        self.paint_tiles()

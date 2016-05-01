"""The user interface."""

from Tkinter import Button, LEFT, Canvas
import settings
from utility import log


class UI():
    """The UI class manages the buttons, map and tiles.

    The latter two are visual depictions of the world and cells respectively
    """

    def __init__(self, master, app, frame):
        """Create the window."""
        self.master = master
        self.app = app
        self.frame = frame
        self.world = self.app.simulation.world

        self.add_buttons()
        self.add_map()

        log(">> Creating tiles")
        self.create_tiles()
        log(">> Painting tiles")
        self.paint_tiles()

    def add_buttons(self):
        """Add buttons to the frame."""
        ground_button = Button(self.frame, text="TERRA", fg="red",
                               command=self.draw_terrain)
        ground_button.pack(side=LEFT)
        water_button = Button(self.frame, text="WATER", fg="red",
                              command=self.toggle_water)
        water_button.pack(side=LEFT)
        heat_button = Button(self.frame, text="HEAT", fg="red",
                             command=self.draw_heat)
        heat_button.pack(side=LEFT)
        step_button = Button(self.frame, text="STEP", fg="red",
                             command=self.app.step)
        step_button.pack(side=LEFT)
        quit_button = Button(self.frame, text="QUIT", fg="red",
                             command=self.frame.quit)
        quit_button.pack(side=LEFT)

    def add_map(self):
        """Add a blank map."""
        self.map = Canvas(self.master,
                          width=settings.map_width + 2*settings.map_border,
                          height=settings.map_height + 2*settings.map_border,
                          bg="black", highlightthickness=0)
        self.map.pack(side=LEFT)

    def create_tiles(self):
        """Create blank tiles."""
        self.map.delete("all")
        self.tiles = []
        for cell in self.world.cells:
            n_in_row = len([c for c in self.world.cells
                            if c.latitude == cell.latitude])
            x_start = ((settings.map_width/2.0) -
                       (n_in_row/2.0)*settings.tile_width)
            y_start = ((cell.latitude/settings.cell_degree_width) *
                       settings.tile_height)

            self.tiles.append(self.map.create_rectangle(
                (x_start +
                    (cell.longitude/360.0) * n_in_row * settings.tile_width),
                y_start,
                (x_start + settings.tile_width + 1 +
                    (cell.longitude/360.0) * n_in_row * settings.tile_width),
                y_start + settings.tile_height,
                fill="yellow",
                outline=""))
        for x in range(len(self.tiles)):
            self.map.tag_bind(self.tiles[x], "<ButtonPress-1>",
                              lambda event, arg=x: self.left_click_tile(arg))
            self.map.tag_bind(self.tiles[x], "<ButtonPress-2>",
                              lambda event, arg=x: self.right_click_tile(arg))

    def left_click_tile(self, x):
        """Tell world to raise terrain at cell x."""
        self.world.raise_cell(x, 1000)
        self.paint_tiles()

    def right_click_tile(self, x):
        """Tell world to raise terrain at cell x."""
        self.world.raise_cell(x, -1000)
        self.paint_tiles()

    def paint_tiles(self):
        """Color the tiles."""
        for x in range(len(self.tiles)):
            self.map.itemconfigure(self.tiles[x],
                                   fill=self.cell_color(self.world.cells[x]))

    def cell_color(self, cell):
        """Work out what color a tile should be.

        The color depends on the cell and the draw_mode parameter.
        """
        if settings.draw_mode == "terrain":
            if cell.water.depth == 0.0 or settings.draw_water is False:
                col_min = [50, 20, 4]
                col_max = [255, 255, 255]
                p = ((cell.land.height - settings.min_ground_height) /
                     (settings.max_ground_height - settings.min_ground_height))
            else:
                col_min = [153, 204, 255]
                col_max = [20, 20, 80]
                p = cell.water.depth/6000.0
                if p > 1:
                    p = 1
        elif settings.draw_mode == "heat":
            col_min = [82, 219, 255]
            col_max = [255, 66, 0]
            p = max(min((cell.surface_temperature-200)/200, 1), 0)
        elif settings.draw_mode == "wind":
            col_min = [0, 0, 0]
            col_max = [255, 255, 255]
            p = min(cell.wind_speed, 10)/10
        q = 1-p
        col = [int(q*col_min[0] + p*col_max[0]),
               int(q*col_min[1] + p*col_max[1]),
               int(q*col_min[2] + p*col_max[2])]
        return '#%02X%02X%02X' % (col[0], col[1], col[2])

    def draw_terrain(self):
        """Paint map by altitude."""
        settings.draw_mode = "terrain"
        self.paint_tiles()

    def draw_heat(self):
        """Paint map by land temperature."""
        settings.draw_mode = "heat"
        self.paint_tiles()

    def toggle_water(self):
        """Toggle whether water is shown in terrain mode."""
        settings.draw_water = not settings.draw_water
        self.paint_tiles()

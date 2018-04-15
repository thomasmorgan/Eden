"""The user interface."""

from Tkinter import Button, Checkbutton, Canvas, Label, StringVar, W, E, IntVar
import settings
from utility import log
import numpy as np


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
        self.add_other_widgets()
        self.add_map()
        self.camera_longitude = 0.0

        self.tiles = {}

        log(">> Creating tiles")
        self.create_tiles()

    def add_buttons(self):
        """Add buttons to the frame."""
        ground_button = Button(self.frame, text="TERRA", fg="red",
                               command=self.draw_terrain)
        ground_button.grid(row=1, column=0, sticky=W+E)
        water_button = Button(self.frame, text="WATER", fg="red",
                              command=self.toggle_water)
        water_button.grid(row=1, column=1, sticky=W+E)
        heat_button = Button(self.frame, text="HEAT", fg="red",
                             command=self.draw_heat)
        heat_button.grid(row=1, column=2, sticky=W+E)
        influence_button = Button(self.frame, text="INFLUENCE", fg="red",
                                  command=self.draw_influence)
        influence_button.grid(row=1, column=3, sticky=W+E)

    def add_other_widgets(self):
        """Add other widgets to the frame."""
        self.update_map = IntVar()
        update_map_check = Checkbutton(self.frame, text="Update map?", variable=self.update_map)
        update_map_check.grid(row=1, column=4, sticky=W+E)
        self.update_map.set(1)
        self.time_rate = StringVar()
        self.rate_label = Label(self.frame, textvariable=self.time_rate)
        self.rate_label.grid(row=0, column=0, sticky=W, columnspan=2)
        self.time_stamp = StringVar()
        self.time_label = Label(self.frame, textvariable=self.time_stamp)
        self.time_label.grid(row=0, column=2, columnspan=8)
        self.update_time_label(0)

    def add_map(self):
        """Add a blank map."""
        self.map = Canvas(self.master,
                          width=settings.map_width + 2*settings.map_border,
                          height=settings.map_height + 2*settings.map_border,
                          bg="black", highlightthickness=0)
        self.map.grid(columnspan=12)

        for c in range(12):
            self.frame.grid_columnconfigure(c, minsize=settings.map_width/12)

    def create_tiles(self):
        """Create blank tiles."""
        self.map.delete("all")
        tiles = []
        for i in range(self.world.num_cells):
            tiles.append(self.map.create_rectangle(0, 0, 1, 1, fill="yellow", outline=""))
        self.tiles["tile"] = np.array(tiles)
        for x in range(len(self.tiles["tile"])):
            self.map.tag_bind(self.tiles["tile"][x], "<ButtonPress-1>",
                              lambda event, arg=x: self.left_click_tile(arg))
            self.map.tag_bind(self.tiles["tile"][x], "<ButtonPress-2>",
                              lambda event, arg=x: self.right_click_tile(arg))
        self.paint_tiles()
        self.place_tiles()

    def left_click_tile(self, x):
        """Tell world to raise terrain at cell x."""
        self.world.raise_cell(x, 1000, settings.cell_width)
        self.world.normalize_terrain()
        self.paint_tiles()

    def right_click_tile(self, x):
        """Tell world to raise terrain at cell x."""
        self.world.raise_cell(x, -1000, settings.cell_width)
        self.world.normalize_terrain()
        self.paint_tiles()

    def paint_tiles(self):
        """Color the tiles."""
        self.update_tile_colors()
        for x in range(self.world.num_cells):
            self.map.itemconfigure(self.tiles["tile"][x],
                                   fill=self.tiles["color"][x])

    def place_tiles(self):
        # latitude of each cell
        lats = self.world.cells["latitude"]
        start_lats = np.minimum(lats + settings.cell_degree_width/2.0, 90.0)
        stop_lats = np.maximum(lats - settings.cell_degree_width/2.0, -90.0)

        # apparent longitude of each cell
        lons = self.world.cells["relative_longitude"]
        start_lons = lons - (360.0/self.world.cells["cells_at_latitude"])/2.0
        stop_lons = lons + (360.0/self.world.cells["cells_at_latitude"])/2.0

        y0 = settings.map_height * (np.sin(np.radians(start_lats)) + 1) / 2.0
        y0 = [x if sl >= -90.0 and sl <= 90.0 else 0 for x, sl in zip(y0, lons)]
        y1 = settings.map_height * (np.sin(np.radians(stop_lats)) + 1) / 2.0
        y1 = [x if sl >= -90.0 and sl <= 90.0 else 0 for x, sl in zip(y1, lons)]

        # what is the radius of a flat slice through the globe at any latitude?
        RAL = np.maximum(settings.map_width/2.0*np.cos(np.radians(start_lats)), settings.map_width/2.0*np.cos(np.radians(stop_lats)))

        # what is the perceived distance from the centre of the screen (LR) for a given longitude at this latitude
        start_dx = np.sin(np.radians(start_lons))*RAL
        stop_dx = np.sin(np.radians(stop_lons))*RAL
        x0 = settings.map_width / 2.0 + start_dx
        x1 = settings.map_width / 2.0 + stop_dx

        for i in range(self.world.num_cells):
            if lons[i] >= -90 and lons[i] <= 90:
                self.map.coords(self.tiles["tile"][i], x0[i], y0[i], x1[i], y1[i])
            else:
                self.map.coords(self.tiles["tile"][i], 0, 0, 0, 0)

    def update_time_label(self, time):
        """Update the UI time label."""
        year = time / (60*60*24*365)
        time -= year*(60*60*24*365)
        day = time / (60*60*24)
        time -= day * (60*60*24)
        hour = time / (60*60)
        time -= hour*(60*60)
        minute = time / 60
        time -= minute*60
        second = time
        year = format(year, ",d")
        hour = "%02d" % (hour, )
        minute = "%02d" % (minute, )
        second = "%02d" % (second, )
        self.time_stamp.set("{}:{}:{}, day {}, year {}."
                            .format(hour, minute, second, day, year))
        self.time_rate.set("x{}".format(settings.time_step_description))

    def update_tile_colors(self):
        """Work out what color a tile should be.

        The color depends on the cell and the draw_mode parameter.
        """
        if self.update_map.get() == 1:
            if settings.draw_mode == "terrain":
                terrain_col_min = [50, 20, 4]
                terrain_col_max = [255, 255, 255]

                # vector of values for each tile saying how much land there is.
                p_terrain = ((self.world.cells["altitude"] - settings.min_ground_height) /
                             (settings.max_ground_height - settings.min_ground_height))

                # terrain_col_min matrix
                dum = np.asarray(terrain_col_min*self.world.num_cells).reshape(self.world.num_cells, -1)
                # terrain_col_max matrix
                dum2 = np.asarray(terrain_col_max*self.world.num_cells).reshape(self.world.num_cells, -1)

                dum3 = (1-p_terrain)[:, np.newaxis]*dum
                dum4 = (p_terrain)[:, np.newaxis]*dum2

                dum5 = (dum3 + dum4).astype(int)

                self.tiles["color"] = ['#%02X%02X%02X' % (d[0], d[1], d[2]) for d in dum5]

                if settings.draw_water:
                    water_col_min = [153, 204, 255]
                    water_col_max = [20, 20, 80]
                    p_water = np.minimum(self.world.cells["water_depth"]/6000.0, 1.0)

                    # terrain_col_min matrix
                    dum = np.asarray(water_col_min*self.world.num_cells).reshape(self.world.num_cells, -1)
                    # terrain_col_max matrix
                    dum2 = np.asarray(water_col_max*self.world.num_cells).reshape(self.world.num_cells, -1)

                    dum3 = (1-p_water)[:, np.newaxis]*dum
                    dum4 = (p_water)[:, np.newaxis]*dum2

                    dum5 = (dum3 + dum4).astype(int)

                    water_cols = ['#%02X%02X%02X' % (d[0], d[1], d[2]) for d in dum5]

                    self.tiles["color"] = [tc if wd < 0.01 else wc for tc, wc, wd in zip(self.tiles["color"], water_cols, self.world.cells["water_depth"])]

            if settings.draw_mode == "influence":
                influence_col_min = [50, 20, 4]
                influence_col_max = [175, 175, 255]

                focal_cell = np.random.randint(self.world.num_cells)

                p_influence = self.world.cells["influence"][focal_cell, :]

                # terrain_col_min matrix
                dum = np.asarray(influence_col_min*self.world.num_cells).reshape(self.world.num_cells, -1)
                # terrain_col_max matrix
                dum2 = np.asarray(influence_col_max*self.world.num_cells).reshape(self.world.num_cells, -1)

                dum3 = (1-p_influence)[:, np.newaxis]*dum
                dum4 = (p_influence)[:, np.newaxis]*dum2

                dum5 = (dum3 + dum4).astype(int)

                self.tiles["color"] = ['#%02X%02X%02X' % (d[0], d[1], d[2]) for d in dum5]

        if not settings.draw_map_far_side:
            self.tiles["color"] = [tc if l >= -90.0 and l <= 90.0 else '#%02X%02X%02X' % (0, 0, 0) for tc, l in zip(self.tiles["color"], self.world.cells["relative_longitude"])]



        # elif settings.draw_mode == "heat":
        #     if settings.draw_water is True:
        #         temp = cell.surface_temperature
        #     else:
        #         temp = cell.land.temperature
        #     if temp < 223:
        #         col_min = [0, 0, 0]
        #         col_max = [82, 219, 255]
        #         p = max(min((temp)/223.0, 1), 0)
        #     elif temp < 273:
        #         col_min = [82, 219, 255]
        #         col_max = [255, 255, 255]
        #         p = max(min((temp-223.0)/50.0, 1), 0)
        #     elif temp < 313:
        #         col_min = [255, 255, 255]
        #         col_max = [255, 66, 0]
        #         p = max(min((temp-273.0)/40.0, 1), 0)
        #     else:
        #         col_min = [255, 66, 0]
        #         col_max = [0, 0, 0]
        #         p = max(min((temp-313.0)/100.0, 1), 0)

        # elif settings.draw_mode == "wind":
        #     col_min = [0, 0, 0]
        #     col_max = [255, 255, 255]
        #     p = min(cell.wind_speed, 10)/10
        # q = 1-p
        # col = [int(q*col_min[0] + p*col_max[0]),
        #        int(q*col_min[1] + p*col_max[1]),
        #        int(q*col_min[2] + p*col_max[2])]
        # return '#%02X%02X%02X' % (col[0], col[1], col[2])

    def draw_terrain(self):
        """Paint map by altitude."""
        settings.draw_mode = "terrain"
        self.paint_tiles()

    def draw_heat(self):
        """Paint map by land temperature."""
        settings.draw_mode = "heat"
        self.paint_tiles()

    def draw_influence(self):
        """Paint map by influence from random focal cell."""
        settings.draw_mode = "influence"
        self.paint_tiles()

    def toggle_water(self):
        """Toggle whether water is shown in terrain mode."""
        settings.draw_water = not settings.draw_water
        self.paint_tiles()

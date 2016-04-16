from Tkinter import *
import settings


class UI():

    def __init__(self, master, app, frame):
        self.master = master
        self.app = app
        self.frame = frame
        self.sim = app.sim
        self.world = self.sim.world
        self.cells = self.world.cells

        self.add_buttons()
        self.add_map()

        self.create_tiles()
        self.paint_tiles()

    def add_buttons(self):
        ground_button = Button(self.frame, text="TERRA", fg="red", command=self.draw_terrain)
        ground_button.pack(side=LEFT)
        heat_button = Button(self.frame, text="HEAT", fg="red", command=self.draw_heat)
        heat_button.pack(side=LEFT)
        wind_button = Button(self.frame, text="WIND", fg="red", command=self.draw_wind)
        wind_button.pack(side=LEFT)
        step_button = Button(self.frame, text="STEP", fg="red", command=self.app.step)
        step_button.pack(side=LEFT)
        quit_button = Button(self.frame, text="QUIT", fg="red", command=self.frame.quit)
        quit_button.pack(side=LEFT)

    def add_map(self):
        self.map = Canvas(self.master, width=settings.map_width + 2*settings.map_border,
                          height=settings.map_height + 2*settings.map_border, bg="yellow",
                          highlightthickness=0)
        self.map.pack(side=LEFT)

    def create_tiles(self):
        self.map.delete("all")
        self.tiles = []
        for cell in self.cells:
            self.tiles.append(self.map.create_rectangle(
                cell.x_min,
                cell.y_min,
                cell.x_max,
                cell.y_max,
                fill="",
                outline=""))

    def paint_tiles(self):
        for x in range(settings.world_cell_width*settings.world_cell_height):
            self.map.itemconfigure(self.tiles[x], fill=self.cell_color(self.cells[x]))

    def cell_color(self, cell):

        if settings.draw_mode == "terrain":
            if cell.water_depth == 0:
                col_min = [50, 20, 4]
                col_max = [255, 255, 255]
                p = (cell.ground_height - settings.min_ground_height)/(settings.max_ground_height - settings.min_ground_height)
            else:
                col_min = [153, 204, 255]
                col_max = [0, 0, 40]
                p = cell.water_depth/(settings.max_ground_height - settings.min_ground_height)
                if p > 1:
                    p = 1
        elif settings.draw_mode == "heat":
            col_min = [178, 34, 34]
            col_max = [255, 250, 205]
            p = min((cell.temperature-200)/200, 1)
        elif settings.draw_mode == "wind":
            col_min = [0, 0, 0]
            col_max = [255, 255, 255]
            p = min(cell.wind_speed, 10)/10
        q = 1-p
        col = [int(q*col_min[0] + p*col_max[0]), int(q*col_min[1] + p*col_max[1]), int(q*col_min[2] + p*col_max[2])]
        return '#%02X%02X%02X' % (col[0], col[1], col[2])

    def draw_terrain(self):
        settings.draw_mode = "terrain"
        self.color_tiles()

    def draw_heat(self):
        settings.draw_mode = "heat"
        self.color_tiles()

    def draw_wind(self):
        settings.draw_mode = "wind"
        self.color_tiles()

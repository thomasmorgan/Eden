from Tkinter import *
import settings


class UI():

    def __init__(self, master, app, frame, world):
        self.master = master
        self.app = app
        self.frame = frame
        self.world = world
        self.add_buttons()
        self.add_map_canvas()
        self.draw_tiles()

    def add_buttons(self):
        reset_button = Button(self.frame, text="RESET", fg="red", command=self.app.reset_world)
        reset_button.pack(side=LEFT)
        button = Button(self.frame, text="QUIT", fg="red", command=self.frame.quit)
        button.pack(side=LEFT)
        button2 = Button(self.frame, text="STEP", fg="red", command=self.app.step)
        button2.pack(side=LEFT)
        button2 = Button(self.frame, text="PRINT", fg="red", command=self.app.print_map)
        button2.pack(side=LEFT)
        ground_button = Button(self.frame, text="TERRA", fg="red", command=self.app.draw_ground)
        ground_button.pack(side=LEFT)
        water_button = Button(self.frame, text="WATER", fg="red", command=self.app.toggle_water)
        water_button.pack(side=LEFT)
        grad_button = Button(self.frame, text="GRAD", fg="red", command=self.app.draw_gradient)
        grad_button.pack(side=LEFT)
        temp_button = Button(self.frame, text="TEMP", fg="red", command=self.app.draw_temperature)
        temp_button.pack(side=LEFT)

    def add_map_canvas(self):
        self.map_canvas = Canvas(self.master, width=settings.map_canvas_width + 2*settings.tile_canvas_border,
                                 height=settings.map_canvas_height + 2*settings.tile_canvas_border, bg="yellow",
                                 highlightthickness=0)
        self.map_canvas.pack(side=LEFT)

    def draw_tiles(self):
        self.map_canvas.delete("all")
        for row in self.world.tiles:
            for t in row:
                t.icon = self.map_canvas.create_rectangle(
                    t.x_min,
                    t.y_min,
                    t.x_max,
                    t.y_max,
                    fill=self.tile_color(t),
                    outline="")
                # if tile.water_depth == 0.0:
                #     if self.map.tile_at(x=tile.xcor, y=tile.ycor-1).water_depth > 0.0:
                #         self.map_canvas.create_rectangle(tile.x_min, tile.y_min, tile.x_max, tile.y_min+self.coast_width, fill=self.coast_color, outline="")
                #     if self.map.tile_at(x=tile.xcor+1, y=tile.ycor).water_depth > 0.0:
                #         self.map_canvas.create_rectangle(tile.x_max-self.coast_width, tile.y_min, tile.x_max, tile.y_max, fill=self.coast_color, outline="")
                #     if self.map.tile_at(x=tile.xcor, y=tile.ycor+1).water_depth > 0.0:
                #         self.map_canvas.create_rectangle(tile.x_min, tile.y_max-self.coast_width, tile.x_max, tile.y_max, fill=self.coast_color, outline="")
                #     if self.map.tile_at(x=tile.xcor-1, y=tile.ycor).water_depth > 0.0:
                #         self.map_canvas.create_rectangle(tile.x_min+self.coast_width, tile.y_min, tile.x_min, tile.y_max, fill=self.coast_color, outline="")

    def tile_color(self, tile):

        if tile.water_depth == 0:
            col_min = [50, 20, 4]
            col_max = [255, 255, 255]
            p = (tile.ground_height - settings.min_ground_height)/(settings.max_ground_height - settings.min_ground_height)
        else:
            col_min = [153, 204, 255]
            col_max = [0, 0, 40]
            p = tile.water_depth/(settings.max_ground_height - settings.min_ground_height)
            if p > 1:
                p = 1
        q = 1-p
        col = [int(q*col_min[0] + p*col_max[0]), int(q*col_min[1] + p*col_max[1]), int(q*col_min[2] + p*col_max[2])]
        return '#%02X%02X%02X' % (col[0], col[1], col[2])

        # if mode == "gradient":
        #     col_min = [255, 255, 255]
        #     col_max = [255, 0, 0]
        #     p = min([self.gradient()/10, 1])
        # elif mode == "temperature":
        #     col_min = [0, 0, 150]
        #     col_max = [255, 0, 0]
        #     p = ((self.temperature + 20)/60.0)
        #     if p < 0:
        #         p = 0
        #     elif p > 1:
        #         p = 1
        # elif mode == "terrain":
        #     if self.water_depth == 0 or water is False:
        #         col_min = [50, 20, 4]
        #         col_max = [255, 255, 255]
        #         p = (self.height - self.map.min_tile_height)/(self.map.max_tile_height - self.map.min_tile_height)
        #     else:
        #         col_min = [153, 204, 255]
        #         col_max = [0, 0, 40]
        #         p = self.water_depth/(self.map.max_tile_height - self.map.min_tile_height)
        #         if p > 1:
        #             p = 1
        # else:
        #     raise ValueError("Cannot color tiles by {}.".format(mode))

        # #p = round(p, 1)
        # q = 1-p

        # col = [int(q*col_min[0] + p*col_max[0]), int(q*col_min[1] + p*col_max[1]), int(q*col_min[2] + p*col_max[2])]
        # return '#%02X%02X%02X' % (col[0], col[1], col[2])

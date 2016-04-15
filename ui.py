from Tkinter import *
import settings
import datetime


class UI():

    def __init__(self, master, app, frame, world):
        self.master = master
        self.app = app
        self.frame = frame
        self.world = world
        self.add_buttons()
        self.add_map()

        b1 = datetime.datetime.now()
        self.create_tiles()
        b2 = datetime.datetime.now()
        print b2-b1
        self.color_tiles()
        b3 = datetime.datetime.now()
        print b3-b2

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

    def add_map(self):
        self.map = Canvas(self.master, width=settings.map_width + 2*settings.map_border,
                          height=settings.map_height + 2*settings.map_border, bg="yellow",
                          highlightthickness=0)
        self.map.pack(side=LEFT)

    def create_tiles(self):
        self.map.delete("all")
        self.icons = []
        self.icon_list = []
        for x in self.world.tiles:
            row_of_icons = []
            for t in x:
                row_of_icons.append(self.map.create_rectangle(
                    t.x_min,
                    t.y_min,
                    t.x_max,
                    t.y_max,
                    fill="",
                    outline=""))
            self.icons.append(row_of_icons)
            self.icon_list.extend(row_of_icons)

    def color_tiles(self):
        for x in range(settings.world_tile_width*settings.world_tile_height):
            self.map.itemconfigure(self.icon_list[x], fill=self.tile_color(self.world.tile_list[x]))
                # if tile.water_depth == 0.0:
                #     if self.map.tile_at(x=tile.xcor, y=tile.ycor-1).water_depth > 0.0:
                #         self.map.create_rectangle(tile.x_min, tile.y_min, tile.x_max, tile.y_min+self.coast_width, fill=self.coast_color, outline="")
                #     if self.map.tile_at(x=tile.xcor+1, y=tile.ycor).water_depth > 0.0:
                #         self.map.create_rectangle(tile.x_max-self.coast_width, tile.y_min, tile.x_max, tile.y_max, fill=self.coast_color, outline="")
                #     if self.map.tile_at(x=tile.xcor, y=tile.ycor+1).water_depth > 0.0:
                #         self.map.create_rectangle(tile.x_min, tile.y_max-self.coast_width, tile.x_max, tile.y_max, fill=self.coast_color, outline="")
                #     if self.map.tile_at(x=tile.xcor-1, y=tile.ycor).water_depth > 0.0:
                #         self.map.create_rectangle(tile.x_min+self.coast_width, tile.y_min, tile.x_min, tile.y_max, fill=self.coast_color, outline="")

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

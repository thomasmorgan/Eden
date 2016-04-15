from Tkinter import *
from tile import Tile
from world import World
from ui import UI
import settings
import datetime


class EdenApp():

    def __init__(self, master):
        start = datetime.datetime.now()
        self.master = master

        # create the world object
        world_start = datetime.datetime.now()
        self.world = World()
        world_stop = datetime.datetime.now()
        print world_stop - world_start

        # create the app
        master.wm_title("Eden")
        self.frame = Frame(master)
        self.frame.pack()

        # create the ui
        self.ui = UI(self.master, self, self.frame, self.world)

        stop = datetime.datetime.now()
        print stop-start

    def move_map_up(self):
        for t in self.map.tiles:
            t.ycor += 1
            if t.ycor == self.num_tiles:
                t.ycor -= self.num_tiles
        self.draw_tiles()

    def move_map_down(self):
        for t in self.map.tiles:
            t.ycor -= 1
            if t.ycor < 0:
                t.ycor += self.num_tiles
        self.draw_tiles()

    def move_map_left(self):
        for t in self.map.tiles:
            t.xcor += 1
            if t.xcor == self.num_tiles:
                t.xcor -= self.num_tiles
        self.draw_tiles()

    def move_map_right(self):
        for t in self.map.tiles:
            t.xcor -= 1
            if t.xcor < 0:
                t.xcor += self.num_tiles
        self.draw_tiles()

    def toggle_water(self):
        self.draw_water = not self.draw_water
        self.draw_tiles()

    def draw_gradient(self):
        self.draw_mode = "gradient"
        self.draw_tiles()

    def draw_temperature(self):
        self.draw_mode = "temperature"
        self.draw_tiles()

    def draw_ground(self):
        self.draw_mode = "terrain"
        self.draw_tiles()

    def step(self):
        self.map.distort_terrain(nsteps=10, type="reciprocal", random_walk=True, step_size=5, scope=0.5, change=15)
        self.map.create_oceans()
        self.draw_tiles()

    def reset_world(self):
        self.map.create_terrain(smoothness=self.smoothness)
        self.map.create_oceans()
        self.map.calculate_temperature()
        self.map.calculate_wind()
        

    # def create_tiles(self):
    #     self.map.tiles = []
    #     for i in range(pow(self.num_tiles, 2)):
    #         xcor = (i % self.num_tiles)
    #         ycor = int(i/float(self.num_tiles))
    #         self.map.tiles.append(Tile(map=self.map,
    #                                    x=xcor,
    #                                    y=ycor,
    #                                    x_min=round(xcor*self.tile_size) + self.tile_canvas_border,
    #                                    y_min=round(ycor*self.tile_size) + self.tile_canvas_border,
    #                                    x_max=round(xcor*self.tile_size) + self.tile_size + self.tile_canvas_border,
    #                                    y_max=round(ycor*self.tile_size) + self.tile_size + self.tile_canvas_border))

    def print_map(self):
        self.map.print_tile_coords()
        self.map.print_tile_distances_from(self.map.tiles[0])
        self.map.print_tile_heights()
        self.map.print_tile_temperatures()

    def draw_tiles(self):
        self.map_canvas.delete("all")
        for tile in self.map.tiles:
            color = tile.color(water=self.draw_water, mode=self.draw_mode)
            tile.rectangle = self.map_canvas.create_rectangle(
                tile.x_min,
                tile.y_min,
                tile.x_max,
                tile.y_max,
                fill=color,
                outline="")
            if tile.water_depth == 0.0:
                if self.map.tile_at(x=tile.xcor, y=tile.ycor-1).water_depth > 0.0:
                    self.map_canvas.create_rectangle(tile.x_min, tile.y_min, tile.x_max, tile.y_min+self.coast_width, fill=self.coast_color, outline="")
                if self.map.tile_at(x=tile.xcor+1, y=tile.ycor).water_depth > 0.0:
                    self.map_canvas.create_rectangle(tile.x_max-self.coast_width, tile.y_min, tile.x_max, tile.y_max, fill=self.coast_color, outline="")
                if self.map.tile_at(x=tile.xcor, y=tile.ycor+1).water_depth > 0.0:
                    self.map_canvas.create_rectangle(tile.x_min, tile.y_max-self.coast_width, tile.x_max, tile.y_max, fill=self.coast_color, outline="")
                if self.map.tile_at(x=tile.xcor-1, y=tile.ycor).water_depth > 0.0:
                    self.map_canvas.create_rectangle(tile.x_min+self.coast_width, tile.y_min, tile.x_min, tile.y_max, fill=self.coast_color, outline="")


root = Tk()
eden = EdenApp(master=root)
root.mainloop()

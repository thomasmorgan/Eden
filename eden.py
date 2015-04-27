from Tkinter import *
import math
from tile import Tile
from map import Map
import random
import datetime


class EdenApp():

    num_tiles = 100
    total_width = 750
    colors = ["red", "blue", "green"]
    tile_canvas_border = 5

    def __init__(self, master):
        start = datetime.datetime.now()
        # open the window
        master.wm_title("Eden")
        frame = Frame(master)
        frame.pack()
        # make the map
        self.create_map(master)
        self.map.create_tiles()
        self.map.distort_terrain_reciprocal(nsteps=100)
        self.map.add_water()

        # add the QUIT button
        button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        button.pack(side=LEFT)
        # self.map.print_tile_heights()
        # print "-------------------"
        # add the step button
        button2 = Button(frame, text="STEP", fg="red", command=self.step)
        button2.pack(side=LEFT)
        button2 = Button(frame, text="PRINT", fg="red", command=self.print_map)
        button2.pack(side=LEFT)

        self.draw_tiles()

        stop = datetime.datetime.now()

        print stop-start

    def step(self):
        self.map_canvas.delete("all")
        self.map.distort_terrain_reciprocal(nsteps=20, rang=4)
        # self.map.print_tile_heights()
        # print "-------------------"
        self.map.add_water()
        self.draw_tiles()

    def create_map(self, master):
        self.map = Map(total_width=self.total_width, num_tiles=self.num_tiles)
        self.map_canvas = Canvas(master, width=self.total_width + 2*self.tile_canvas_border,
                                 height=self.total_width + 2*self.tile_canvas_border, bg="yellow",
                                 highlightthickness=0)
        self.map_canvas.pack(side=LEFT)

    def print_map(self):
        self.map.print_tile_coords()
        self.map.print_tile_distances_from(self.map.tiles[49])
        self.map.print_tile_heights()

    def draw_tiles(self):
        tile_size = self.total_width/self.num_tiles
        for tile in self.map.tiles:
            self.map_canvas.create_rectangle(tile.xcor*tile_size + self.tile_canvas_border,
                                             tile.ycor*tile_size + self.tile_canvas_border,
                                             tile.xcor*tile_size + tile_size + self.tile_canvas_border,
                                             tile.ycor*tile_size + tile_size + self.tile_canvas_border,
                                             fill=tile.color())

root = Tk()
eden = EdenApp(master=root)
root.mainloop()

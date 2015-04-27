from Tkinter import *
import math
from tile import Tile
from map import Map
import random


class EdenApp():

    num_tiles = 50
    total_width = 500
    colors = ["red", "blue", "green"]
    tile_canvas_border = 5

    def __init__(self, master):
        # open the window
        master.wm_title("Eden")
        frame = Frame(master)
        frame.pack()
        # add the QUIT button
        button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        button.pack()
        # make the map
        self.create_map(master)
        self.map.create_tiles()
        # self.map.print_tile_heights()
        # print "-------------------"
        # add the step button
        button2 = Button(frame, text="STEP", fg="red", command=self.step)
        button2.pack()
        button2 = Button(frame, text="PRINT", fg="red", command=self.map.print_tile_heights)
        button2.pack()

        self.draw_tiles()

    def step(self):
        self.map_canvas.delete("all")
        self.map.generate_terrain(nsteps=20, rang=4)
        # self.map.print_tile_heights()
        # print "-------------------"
        self.draw_tiles()

    def create_map(self, master):
        self.map = Map(total_width=self.total_width, num_tiles=self.num_tiles)
        self.map_canvas = Canvas(master, width=self.total_width + 2*self.tile_canvas_border,
                                 height=self.total_width + 2*self.tile_canvas_border, bg="yellow",
                                 highlightthickness=0)
        self.map_canvas.pack()

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

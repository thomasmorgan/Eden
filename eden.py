from Tkinter import *
import math
from tile import Tile
from map import Map
import random


class EdenApp():

    num_tiles = 20
    total_width = 500
    colors = ["red", "blue", "green"]
    tile_canvas_border = 5

    def __init__(self, master):
        master.wm_title("Eden")
        frame = Frame(master)
        frame.pack()
        button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        button.pack()
        self.create_map(master)
        self.create_tiles()
        self.draw_tiles()

    def create_map(self, master):
        self.map = Map()
        self.map_canvas = Canvas(master, width=self.total_width + 2*self.tile_canvas_border,
                                 height=self.total_width + 2*self.tile_canvas_border, bg="yellow",
                                 highlightthickness=0)
        self.map_canvas.pack()

    def create_tiles(self):
        self.map.tiles = []
        for i in range(pow(self.num_tiles, 2)):
            tile_size = self.total_width/self.num_tiles
            xcor = (i % self.num_tiles)*tile_size
            ycor = int(math.floor(i/self.num_tiles)*tile_size)
            self.map.tiles.append(Tile(x=xcor, y=ycor, size=tile_size, ground_height=i))

    def draw_tiles(self):
        for tile in self.map.tiles:
            self.map_canvas.create_rectangle(tile.xcor + self.tile_canvas_border,
                                             tile.ycor + self.tile_canvas_border,
                                             tile.xcor + tile.size + self.tile_canvas_border,
                                             tile.ycor + tile.size + self.tile_canvas_border,
                                             fill=tile.color())

root = Tk()
eden = EdenApp(master=root)
root.mainloop()

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

    draw_water = True

    def __init__(self, master):
        start = datetime.datetime.now()
        # open the window
        master.wm_title("Eden")
        frame = Frame(master)
        frame.pack()
        # make the map
        self.create_map(master)
        self.map.create_tiles()
        self.map.distort_terrain_cone(nsteps=500)
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

        up_button = Button(frame, text="UP", fg="red", command=self.move_map_up)
        up_button.pack(side=LEFT)

        down_button = Button(frame, text="DOWN", fg="red", command=self.move_map_down)
        down_button.pack(side=LEFT)

        left_button = Button(frame, text="LEFT", fg="red", command=self.move_map_left)
        left_button.pack(side=LEFT)

        right_button = Button(frame, text="RIGHT", fg="red", command=self.move_map_right)
        right_button.pack(side=LEFT)

        water_button = Button(frame, text="WATER", fg="red", command=self.toggle_water)
        water_button.pack(side=LEFT)

        self.draw_tiles()

        stop = datetime.datetime.now()

        print stop-start

    def move_map_up(self):
        for t in self.map.tiles:
            t.ycor += 1
            if t.ycor == self.num_tiles:
                t.ycor -= self.num_tiles
        self.redraw_tiles()

    def move_map_down(self):
        for t in self.map.tiles:
            t.ycor -= 1
            if t.ycor < 0:
                t.ycor += self.num_tiles
        self.redraw_tiles()

    def move_map_left(self):
        for t in self.map.tiles:
            t.xcor += 1
            if t.xcor == self.num_tiles:
                t.xcor -= self.num_tiles
        self.redraw_tiles()

    def move_map_right(self):
        for t in self.map.tiles:
            t.xcor -= 1
            if t.xcor < 0:
                t.xcor += self.num_tiles
        self.redraw_tiles()

    def toggle_water(self):
        self.draw_water = not self.draw_water
        self.redraw_tiles()

    def step(self):
        self.map.distort_terrain_cone(nsteps=1)
        self.redraw_tiles()

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
                                             fill=tile.color(water=self.draw_water))

    def redraw_tiles(self):
        self.map_canvas.delete("all")
        self.map.add_water()
        self.draw_tiles()

root = Tk()
eden = EdenApp(master=root)
root.mainloop()

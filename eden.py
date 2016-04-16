from Tkinter import *
from world import World
from ui import UI


class EdenApp():

    def __init__(self, master):
        self.master = master

        # create the world object
        self.world = World()

        # create the app
        master.wm_title("Eden")
        self.frame = Frame(master)
        self.frame.pack()

        # create the ui
        self.ui = UI(self.master, self, self.frame, self.world)

    def step(self):
        self.world.step()
        self.ui.color_tiles()
        print "stepped!"

root = Tk()
eden = EdenApp(master=root)
root.mainloop()

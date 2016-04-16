from Tkinter import *
from simulation import Simulation
from ui import UI


class EdenApp():

    def __init__(self, master):
        self.master = master

        # create the simulation object
        self.simulation = Simulation()
        for x in range(500):
            print x
            self.simulation.step()

        # create the app
        master.wm_title("Eden")
        self.frame = Frame(master)
        self.frame.pack()

        # create the ui
        self.ui = UI(self.master, self, self.frame)

    def step(self):
        self.simulation.step()
        self.ui.paint_tiles()
        print "stepped!"

root = Tk()
eden = EdenApp(master=root)
root.mainloop()

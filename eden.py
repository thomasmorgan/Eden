"""The Eden app."""

from Tkinter import Frame, Tk
from simulation import Simulation
from ui import UI
import utility
from utility import log


class EdenApp():
    """The EdenApp class is the overall app.

    When it runs it creates two objects:
    The simulation, that runs the actual simulation.
    The ui, that presents visuals of the simulation on the screen.
    """

    def __init__(self, master):
        """Create the app."""
        self.master = master

        # create the simulation object
        utility.log_welcome()
        log("> Creating simulation")
        self.simulation = Simulation()
        for x in range(000):
            print x
            self.simulation.step()

        # create the app
        log("> Creating UI")
        master.wm_title("Eden")
        self.frame = Frame(master)
        self.frame.pack()

        # create the ui
        self.ui = UI(self.master, self, self.frame)

    def step(self):
        """Advance one step in time."""
        for _ in range(1000):
            print _
            self.simulation.step()
            self.ui.paint_tiles()
            self.master.update()

root = Tk()
eden = EdenApp(master=root)
root.mainloop()

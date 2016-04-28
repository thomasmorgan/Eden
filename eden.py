"""The Eden app."""

from Tkinter import Frame, Tk
from simulation import Simulation
from ui import UI
import utility
from utility import log
import operator


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

        self.create_key_bindings()

        self.running = False

    def create_key_bindings(self):
        """Set up key bindings."""
        def leftKey(event):
            self.rotate_map(-10.0)

        def rightKey(event):
            self.rotate_map(10.0)

        def spaceKey(event):
            self.toggle_running()

        self.master.bind('<Left>', leftKey)
        self.master.bind('<Right>', rightKey)

    def step(self):
        """Advance one step in time."""
        for _ in range(1000):
            print _
            self.simulation.step()
            self.ui.paint_tiles()
            self.master.update()
    def rotate_map(self, degrees):
        """Spin the map."""
        for c in self.simulation.world.cells:
            c.longitude += degrees
            if c.longitude < 0:
                c.longitude += 360.0
            elif c.longitude >= 360.0:
                c.longitude -= 360.0

        self.simulation.world.cells = sorted(
            self.simulation.world.cells,
            key=operator.attrgetter("latitude", "longitude"))
        self.ui.paint_tiles()

root = Tk()
eden = EdenApp(master=root)
root.mainloop()

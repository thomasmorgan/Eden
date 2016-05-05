"""The Eden app."""

from Tkinter import Frame, Tk
from simulation import Simulation
from ui import UI
import utility
from utility import log
from operator import attrgetter
import settings


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
        self.time = 0

        old_time_step = settings.time_step_size
        time_step_sizes = [60*60*24*365*5, 60*60*24*365, 60*60*24*30,
                           60*60*24, 60*60]
        for t in time_step_sizes:
            settings.time_step_size = t
            for _ in range(10):
                self.step()
        settings.time_step_size = old_time_step

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
        self.master.bind('<space>', spaceKey)

    def step(self):
        """Advance one step in time."""
        self.time += settings.time_step_size
        self.ui.update_time_label(self.time)
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
            key=attrgetter("latitude", "longitude"))
        self.ui.paint_tiles()

    def toggle_running(self):
        """Start/stop the simulation."""
        self.running = not self.running
        while self.running:
            self.step()


root = Tk()
eden = EdenApp(master=root)
root.mainloop()

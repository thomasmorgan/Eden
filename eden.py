"""The Eden app."""

from Tkinter import Frame, Tk
from simulation import Simulation
from ui import UI
import utility
from utility import log
from operator import attrgetter
import numpy as np
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

        # create the app
        log("> Creating UI")
        master.wm_title("Eden")
        self.frame = Frame(master)
        self.frame.grid()

        # create the ui
        self.ui = UI(self.master, self, self.frame)

        self.create_key_bindings()

        self.running = False
        self.time = 0

    def create_key_bindings(self):
        """Set up key bindings."""
        def leftKey(event):
            self.ui.camera_longitude -= 10.0
            if self.ui.camera_longitude < -180.0:
                self.ui.camera_longitude += 360.0
            self.redraw_map()

        def rightKey(event):
            self.ui.camera_longitude += 10.0
            if self.ui.camera_longitude >= 180.0:
                self.ui.camera_longitude -= 360.0
            self.redraw_map()

        def upKey(event):
            self.change_time_step(1)

        def downKey(event):
            self.change_time_step(-1)

        def spaceKey(event):
            self.toggle_running()

        self.master.bind('<Left>', leftKey)
        self.master.bind('<Right>', rightKey)
        self.master.bind('<Up>', upKey)
        self.master.bind('<Down>', downKey)
        self.master.bind('<space>', spaceKey)

    def step(self):
        """Advance one step in time."""
        self.time += settings.time_step_size
        self.ui.update_time_label(self.time)
        self.simulation.step()
        self.ui.paint_tiles()
        self.master.update()

    def redraw_map(self):
        """Spin the map."""
        self.simulation.world.cells["relative_longitude"] = self.simulation.world.cells["longitude"] - self.ui.camera_longitude
        self.simulation.world.cells["relative_longitude"] = np.array([x + 360.0 if x < -180.0 else x - 360.0 if x > 180.0 else x for x in self.simulation.world.cells["relative_longitude"]])
        self.ui.place_tiles()
        self.ui.paint_tiles()

    def change_time_step(self, direction):
        """Change the time_step_size."""
        time_steps = [
            1,
            10,
            60,
            60*10,
            60*60,
            60*60*6,
            60*60*24,
            60*60*24*7,
            60*60*24*30,
            60*60*24*365,
            60*60*24*365*10,
            60*60*24*365*50,
            60*60*24*365*100,
            60*60*24*365*500,
            60*60*24*365*1000,
            60*60*24*365*10000,
            60*60*24*365*100000,
            60*60*24*365*1000000
        ]
        step_descriptions = [
            "1s",
            "10s",
            "1 minute",
            "10 minutes",
            "1 hour",
            "6 hours",
            "1 day",
            "7 days",
            "30 days",
            "1 year",
            "10 years",
            "50 years",
            "100 years",
            "500 years",
            "1,000 years",
            "10,000 years",
            "100,000 years",
            "1,000,000 years"
        ]
        index = time_steps.index(settings.time_step_size)
        if direction > 0 and index != len(time_steps) - 1:
            settings.time_step_size = time_steps[index + 1]
            settings.time_step_description = step_descriptions[index + 1]
        elif direction < 0 and index != 0:
            settings.time_step_size = time_steps[index - 1]
            settings.time_step_description = step_descriptions[index - 1]
        self.ui.update_time_label(self.time)

    def toggle_running(self):
        """Start/stop the simulation."""
        self.running = not self.running
        while self.running:
            self.step()


root = Tk()
eden = EdenApp(master=root)
root.mainloop()

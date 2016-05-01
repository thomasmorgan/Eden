"""The simulation class."""

from world import World
from sun import Sun
from utility import log


class Simulation():
    """The simulation class executes the simulation.

    Upon initialization it creates the system - the world, sun, oceans etc.
    The step function proceeds forwards in time.
    """

    def __init__(self):
        """Create the simulation."""
        log("> Creating world")
        self.create_world()
        log("> Creating sun")
        self.create_sun()

    def create_world(self):
        """Create the world."""
        self.world = World()

    def create_sun(self):
        """Create the sun."""
        self.sun = Sun()

    def step(self):
        """Advance 1 time step."""
        self.world.conduct_energy_between_cells()
        self.world.absorb_energy_from_sun(self.sun)
        self.world.absorb_energy_from_core()
        self.world.radiate_energy()
        self.world.slosh_oceans()

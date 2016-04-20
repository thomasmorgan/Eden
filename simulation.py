from world import World
from sun import Sun
import settings


class Simulation():

    """ The simulation class executes the simulation.
    Upon initialization it creates the system - the world, sun, oceans etc.
    The step function proceeds forwards in time.
    """

    def __init__(self):
        self.create_world()
        self.create_sun()

    def create_world(self):
        """ create the world object """
        self.world = World()

    def create_sun(self):
        """ create the sun object """
        self.sun = Sun()

    def step(self):
        """ progress forward 1 time step """
        self.world.conduct_energy_between_cells()
        self.world.absorb_energy_from_sun(self.sun)
        self.world.absorb_energy_from_core()
        self.world.radiate_energy()
        self.world.calculate_temperature()

        print "****"
        print "polar cell: temp = {}, energy = {}, transfer: {}".format(self.world.cells[0].land.temperature - 273, self.world.cells[0].land.thermal_energy, self.world.cells[0].y_energy_transfer)
        half = settings.world_cell_height*settings.world_cell_width/2
        print "equatorial cell: temp = {}, energy = {}, transfer: {}".format(self.world.cells[half].land.temperature - 273, self.world.cells[half].land.thermal_energy, self.world.cells[half].y_energy_transfer)

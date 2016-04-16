from world import World
from sun import Sun


class Simulation():

    def __init__(self):
        self.create_world()
        self.create_sun()

    def create_world(self):
        self.world = World()

    def create_sun(self):
        """ create the sun object """
        self.sun = Sun()

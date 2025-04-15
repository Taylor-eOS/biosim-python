import random
import settings
from genome import make_random_genome
from brain import Brain

class Individual:
    def __init__(self, genome=None, x=0, y=0):
        self.genome = list(genome) if genome is not None else make_random_genome()
        self.brain = Brain(self.genome)
        self.x = x
        self.y = y
        self.last_dx = 0
        self.last_dy = 0

    def update(self, sensor_inputs):
        return self.brain.activate(sensor_inputs)

    def __repr__(self):
        return f"<Individual pos=({int(self.x)},{int(self.y)})>"


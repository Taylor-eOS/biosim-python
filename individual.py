from utils import make_random_genome
from brain import Brain
import random

class Individual:
    def __init__(self, genome=None, x=0.0, y=0.0):
        #Each individual has a genome and a corresponding brain.
        #If no genome is provided, generate a random one.
        self.genome = genome if genome is not None else make_random_genome()
        self.brain = Brain(self.genome)
        #Position in the simulation world.
        self.x = x
        self.y = y
        self.fitness = 0.0

    def update(self, sensor_inputs):
        #Activate the brain given sensor inputs.
        #You could later augment this with movement or other actions.
        actions = self.brain.activate(sensor_inputs)
        #For example, you could interpret actions to change the position.
        #Here, we simply update fitness as an example.
        self.fitness += sum(abs(a) for a in actions)
        return actions

    def __repr__(self):
        return f"<Individual pos=({self.x:.2f},{self.y:.2f}) fitness={self.fitness:.2f}>"


from utils import make_random_genome
from brain import Brain
import random

class Individual:
    def __init__(self, genome=None, x=0.0, y=0.0):
        self.genome = genome if genome is not None else make_random_genome()
        self.brain = Brain(self.genome)
        self.x = x
        self.y = y
        self.fitness = 0.0
        print("Action connections sensor use:", [
            (g.sourceType, g.sourceNum, g.sinkNum, g.weight) 
            for g in self.brain.action_connections])

    def update(self, sensor_inputs):
        actions = self.brain.activate(sensor_inputs)
        self.fitness += sum(abs(a) for a in actions)
        return actions

    def __repr__(self):
        return f"<Individual pos=({self.x:.2f},{self.y:.2f}) fitness={self.fitness:.2f}>"


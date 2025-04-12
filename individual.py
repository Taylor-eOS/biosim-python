from genome import make_random_genome
from brain import Brain
import random
import numpy as np

class Individual:
    def __init__(self, genome=None, x=0.0, y=0.0):
        self.genome = genome if genome is not None else make_random_genome()
        self.brain = Brain(self.genome)
        self.x = x
        self.y = y
        self.fitness = 0.0
        print("Action connections (sensor->action):", 
              self.brain.sensor_action.tolist() if self.brain.sensor_action.size else [])
        print("Action connections (neuron->action):", 
              self.brain.neuron_action.tolist() if self.brain.neuron_action.size else [])

    def update(self, sensor_inputs):
        actions = self.brain.activate(sensor_inputs)
        self.fitness += float(np.sum(np.abs(actions)))
        return actions

    def __repr__(self):
        return "<Individual pos=({:.2f},{:.2f}) fitness={:.2f}>".format(self.x, self.y, self.fitness)


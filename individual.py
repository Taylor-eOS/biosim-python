from genome import make_random_genome, gene_dtype, NUM_SENSES, MAX_NEURONS, NUM_ACTIONS
from brain import Brain
import random
import numpy as np

def mutate_genome(genome, mutation_rate=0.1):
    if random.random() < mutation_rate:
        new_gene = np.empty(1, dtype=gene_dtype)
        new_gene['sourceType'] = np.random.randint(0, 2, size=1, dtype=np.uint8)
        rand_vals = np.random.randint(0, 2, size=1, dtype=np.uint8)
        new_gene['sinkType'] = np.where(rand_vals == 0, 1, 2)
        new_gene['sourceNum'] = np.random.randint(0, 0x8000, size=1, dtype=np.uint16)
        new_gene['sinkNum'] = np.random.randint(0, 0x8000, size=1, dtype=np.uint16)
        sensor_mask = (new_gene['sourceType'] == 0)
        new_gene['sourceNum'][sensor_mask] %= NUM_SENSES
        new_gene['sourceNum'][~sensor_mask] %= MAX_NEURONS
        neuron_mask = (new_gene['sinkType'] == 1)
        new_gene['sinkNum'][neuron_mask] %= MAX_NEURONS
        new_gene['sinkNum'][~neuron_mask] %= NUM_ACTIONS
        new_gene['weight'] = np.random.uniform(-1.0, 1.0, size=1).astype(np.float32)
        genome = np.append(genome, new_gene)
    return genome

class Individual:
    def __init__(self, genome=None, x=0.0, y=0.0):
        if genome is None:
            self.genome = make_random_genome()
        else:
            self.genome = mutate_genome(genome)  # mutation on offspring genomes only
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


import random
import numpy as np
from settings import SENSOR, NEURON, ACTION, NUM_SENSES, MAX_NEURONS, NUM_ACTIONS, MUTATION_RATE
from genome import make_random_genome, gene_dtype
from brain import Brain

class Individual:
    def __init__(self, genome=None, x=0, y=0):
        if genome is None:
            self.genome = make_random_genome()
        else:
            self.genome = mutate_genome(genome)
        self.brain = Brain(self.genome)
        self.x = x
        self.y = y
        self.last_dx = 0
        self.last_dy = 0

    def update(self, sensor_inputs):
        actions = self.brain.activate(sensor_inputs)
        return actions

    def __repr__(self):
        return f"<Individual pos=({int(self.x)},{int(self.y)})>"

def mutate_genome(genome, mutation_rate=MUTATION_RATE, edit_rate=MUTATION_RATE-0.1):
    genome = genome.copy()
    if random.random() < mutation_rate:
        new_gene = np.empty(1, dtype=gene_dtype)
        new_gene['sourceType'] = np.random.randint(0, 2, dtype=np.uint8)
        rand_vals = np.random.randint(0, 2, dtype=np.uint8)
        new_gene['sinkType'] = 1 if rand_vals == 0 else 2
        new_gene['sourceNum'] = np.random.randint(0, 0x8000, dtype=np.uint16)
        new_gene['sinkNum'] = np.random.randint(0, 0x8000, dtype=np.uint16)
        if new_gene['sourceType'] == SENSOR:
            new_gene['sourceNum'] %= NUM_SENSES
        else:
            new_gene['sourceNum'] %= MAX_NEURONS
        if new_gene['sinkType'] == NEURON:
            new_gene['sinkNum'] %= MAX_NEURONS
        else:
            new_gene['sinkNum'] %= NUM_ACTIONS
        new_gene['weight'] = np.random.uniform(-1.0, 1.0)
        genome = np.append(genome, new_gene)
    if random.random() < edit_rate and len(genome) > 0:
        gene_idx = random.randint(0, len(genome) - 1)
        field = random.choice(['sourceType', 'sinkType', 'sourceNum', 'sinkNum', 'weight'])
        if field == 'sourceType':
            genome[gene_idx]['sourceType'] = random.randint(0, 1)
            genome[gene_idx]['sourceNum'] %= NUM_SENSES if genome[gene_idx]['sourceType'] == SENSOR else MAX_NEURONS
        elif field == 'sinkType':
            genome[gene_idx]['sinkType'] = random.randint(1, 2)
            genome[gene_idx]['sinkNum'] %= MAX_NEURONS if genome[gene_idx]['sinkType'] == NEURON else NUM_ACTIONS
        elif field == 'sourceNum':
            genome[gene_idx]['sourceNum'] = random.randint(0, NUM_SENSES - 1) if genome[gene_idx]['sourceType'] == SENSOR else random.randint(0, MAX_NEURONS - 1)
        elif field == 'sinkNum':
            genome[gene_idx]['sinkNum'] = random.randint(0, MAX_NEURONS - 1) if genome[gene_idx]['sinkType'] == NEURON else random.randint(0, NUM_ACTIONS - 1)
        elif field == 'weight':
            genome[gene_idx]['weight'] += np.random.uniform(-0.5, 0.5)
            genome[gene_idx]['weight'] = np.clip(genome[gene_idx]['weight'], -1.0, 1.0)
    return genome


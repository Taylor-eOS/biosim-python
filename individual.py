import random
import numpy as np
import settings
from genome import make_random_genome, gene_dtype
from brain import Brain

class Individual:
    def __init__(self, genome=None, x=0, y=0):
        if genome is None:
            self.genome = make_random_genome()
        else:
            self.genome = mutate_genome(genome)
        self.brain = Brain(self.genome)
        self.number = 0
        self.x = x
        self.y = y
        self.last_dx = 0
        self.last_dy = 0

    def update(self, sensor_inputs):
        actions = self.brain.activate(sensor_inputs)
        return actions

    def __repr__(self):
        return f"<Individual pos=({int(self.x)},{int(self.y)})>"

def mutate_genome(genome, addition_rate=settings.MUTATION_RATE, edit_rate=settings.MUTATION_RATE*0.8, removal_rate=settings.MUTATION_RATE*0.5):
    genome = genome.copy()
    if random.random() < addition_rate:
        new_gene = np.empty(1, dtype=gene_dtype)
        new_gene['sourceType'] = np.random.randint(0, 2, dtype=np.uint8)
        if new_gene['sourceType'] == settings.SENSOR:
            new_gene['sinkType'] = settings.NEURON
        else:
            new_gene['sinkType'] = settings.NEURON if random.random() < 0.7 else settings.ACTION
        new_gene['sourceNum'] = np.random.randint(0, 0x8000, dtype=np.uint16)
        new_gene['sinkNum'] = np.random.randint(0, 0x8000, dtype=np.uint16)
        new_gene['sourceNum'] %= settings.NUM_SENSES if new_gene['sourceType'] == settings.SENSOR else settings.MAX_NEURONS
        new_gene['sinkNum'] %= settings.MAX_NEURONS if new_gene['sinkType'] == settings.NEURON else settings.NUM_ACTIONS
        new_gene['weight'] = np.random.uniform(-1.0, 1.0)
        genome = np.append(genome, new_gene)
    if len(genome) > 0 and random.random() < edit_rate:
        gene_idx = random.randint(0, len(genome) - 1)
        field = random.choice(['sourceType', 'sinkType', 'sourceNum', 'sinkNum', 'weight'])
        if field == 'sourceType':
            genome[gene_idx]['sourceType'] = random.randint(0, 1)
            genome[gene_idx]['sourceNum'] %= settings.NUM_SENSES if genome[gene_idx]['sourceType'] == settings.SENSOR else settings.MAX_NEURONS
            # Force sensor genes to always connect to neurons.
            if genome[gene_idx]['sourceType'] == settings.SENSOR:
                genome[gene_idx]['sinkType'] = settings.NEURON
                genome[gene_idx]['sinkNum'] %= settings.MAX_NEURONS
        elif field == 'sinkType':
            if genome[gene_idx]['sourceType'] == settings.SENSOR:
                # Ensure sensor genes never have action as sink.
                genome[gene_idx]['sinkType'] = settings.NEURON
                genome[gene_idx]['sinkNum'] %= settings.MAX_NEURONS
            else:
                genome[gene_idx]['sinkType'] = settings.NEURON if random.random() < 0.5 else settings.ACTION
                genome[gene_idx]['sinkNum'] %= settings.MAX_NEURONS if genome[gene_idx]['sinkType'] == settings.NEURON else settings.NUM_ACTIONS
        elif field == 'sourceNum':
            genome[gene_idx]['sourceNum'] = random.randint(0, settings.NUM_SENSES - 1) if genome[gene_idx]['sourceType'] == settings.SENSOR else random.randint(0, settings.MAX_NEURONS - 1)
        elif field == 'sinkNum':
            genome[gene_idx]['sinkNum'] = random.randint(0, settings.MAX_NEURONS - 1) if genome[gene_idx]['sinkType'] == settings.NEURON else random.randint(0, settings.NUM_ACTIONS - 1)
        elif field == 'weight':
            genome[gene_idx]['weight'] = np.clip(
                genome[gene_idx]['weight'] + np.random.uniform(-0.5, 0.5), -1.0, 1.0)
    if len(genome) > 0 and random.random() < removal_rate:
        remove_idx = random.randint(0, len(genome) - 1)
        genome = np.delete(genome, remove_idx)
    return genome


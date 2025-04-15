import random
import numpy as np
import settings
from genome import make_random_genome, gene_dtype
from brain import Brain

class Individual:
    def __init__(self, genome=None, x=0, y=0):
        self.genome = genome if genome is not None else make_random_genome()
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

def random_neuron_id():
    return random.randint(0, 1000)

def mutate_genome(genome):
    genome = genome.copy()
    used_neuron_ids = set()
    for gene in genome:
        if gene['sourceType'] == settings.NEURON:
            used_neuron_ids.add(int(gene['sourceNum']))
        if gene['sinkType'] == settings.NEURON:
            used_neuron_ids.add(int(gene['sinkNum']))
    if used_neuron_ids:
        next_neuron_id = max(used_neuron_ids) + 1
    else:
        next_neuron_id = 0
    def new_neuron_id():
        return next_neuron_id
    mutation_types = ['add_connection','edit_connection','remove_connection','add_neuron_connection']
    if len(genome) == 0:
        mutation_types = ['add_connection','add_neuron_connection']
    chosen_mutation = random.choice(mutation_types)
    if chosen_mutation == 'add_connection':
        new_gene = np.empty(1, dtype=gene_dtype)
        new_gene['sourceType'] = np.random.randint(0, 2, dtype=np.uint8)
        if new_gene['sourceType'] == settings.SENSOR:
            new_gene['sinkType'] = settings.NEURON
            new_gene['sourceNum'] = np.random.randint(0, settings.NUM_SENSES, dtype=np.uint16)
            new_gene['sinkNum'] = new_neuron_id()
        else:
            new_gene['sourceNum'] = random.choice(list(used_neuron_ids)) if used_neuron_ids else 0
            if random.random() < 0.7:
                new_gene['sinkType'] = settings.NEURON
                new_gene['sinkNum'] = new_neuron_id()
            else:
                new_gene['sinkType'] = settings.ACTION
                new_gene['sinkNum'] = np.random.randint(0, settings.NUM_ACTIONS, dtype=np.uint16)
        new_gene['weight'] = np.random.uniform(-1.0, 1.0)
        genome = np.append(genome, new_gene)
    elif chosen_mutation == 'edit_connection' and len(genome) > 0:
        gene_idx = random.randint(0, len(genome) - 1)
        field = random.choice(['sourceType','sinkType','sourceNum','sinkNum','weight'])
        if field == 'sourceType':
            new_source = random.randint(0,1)
            genome[gene_idx]['sourceType'] = new_source
            if new_source == settings.SENSOR:
                genome[gene_idx]['sourceNum'] = np.random.randint(0, settings.NUM_SENSES, dtype=np.uint16)
                genome[gene_idx]['sinkType'] = settings.NEURON
                genome[gene_idx]['sinkNum'] = new_neuron_id()
            else:
                genome[gene_idx]['sourceNum'] = random.choice(list(used_neuron_ids)) if used_neuron_ids else 0
                if genome[gene_idx]['sinkType'] == settings.SENSOR:
                    genome[gene_idx]['sinkType'] = settings.NEURON
                    genome[gene_idx]['sinkNum'] = new_neuron_id()
        elif field == 'sinkType':
            if genome[gene_idx]['sourceType'] == settings.SENSOR:
                genome[gene_idx]['sinkType'] = settings.NEURON
                genome[gene_idx]['sinkNum'] = new_neuron_id()
            else:
                if random.random() < 0.7:
                    genome[gene_idx]['sinkType'] = settings.NEURON
                    genome[gene_idx]['sinkNum'] = new_neuron_id()
                else:
                    genome[gene_idx]['sinkType'] = settings.ACTION
                    genome[gene_idx]['sinkNum'] = np.random.randint(0, settings.NUM_ACTIONS, dtype=np.uint16)
        elif field == 'sourceNum':
            if genome[gene_idx]['sourceType'] == settings.SENSOR:
                genome[gene_idx]['sourceNum'] = np.random.randint(0, settings.NUM_SENSES, dtype=np.uint16)
            else:
                genome[gene_idx]['sourceNum'] = random.choice(list(used_neuron_ids)) if used_neuron_ids else 0
        elif field == 'sinkNum':
            if genome[gene_idx]['sinkType'] == settings.NEURON:
                genome[gene_idx]['sinkNum'] = new_neuron_id()
            else:
                genome[gene_idx]['sinkNum'] = np.random.randint(0, settings.NUM_ACTIONS, dtype=np.uint16)
        elif field == 'weight':
            genome[gene_idx]['weight'] = np.random.uniform(-1.0, 1.0)
    elif chosen_mutation == 'remove_connection' and len(genome) > 0:
        remove_idx = random.randint(0, len(genome) - 1)
        genome = np.delete(genome, remove_idx)
    elif chosen_mutation == 'add_neuron_connection':
        new_gene = np.empty(1, dtype=gene_dtype)
        new_gene['sourceType'] = settings.NEURON
        new_gene['sinkType'] = settings.NEURON
        new_gene['sourceNum'] = random.choice(list(used_neuron_ids)) if used_neuron_ids else 0
        new_gene['sinkNum'] = new_neuron_id()
        new_gene['weight'] = np.random.uniform(-1.0, 1.0)
        genome = np.append(genome, new_gene)
    return genome


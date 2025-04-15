import numpy as np
import random
import settings

gene_dtype = np.dtype([
    ('sourceType', np.uint8),
    ('sourceNum', np.uint16),
    ('sinkType', np.uint8),
    ('sinkNum', np.uint16),
    ('weight', np.float32)])

def make_random_genome():
    length = settings.GENOME_LENGTH
    genome = np.empty(length, dtype=gene_dtype)
    genome['sourceType'] = np.random.randint(0, 2, size=length, dtype=np.uint8)
    rand_vals = np.random.randint(0, 2, size=length, dtype=np.uint8)
    genome['sinkType'] = np.where(rand_vals == 0, settings.NEURON, settings.ACTION)
    sensor_source_mask = (genome['sourceType'] == settings.SENSOR)
    genome['sinkType'][sensor_source_mask] = settings.NEURON
    genome['sourceNum'] = np.random.randint(0, 0x8000, size=length, dtype=np.uint16)
    genome['sinkNum'] = np.random.randint(0, 0x8000, size=length, dtype=np.uint16)
    sensor_mask = (genome['sourceType'] == settings.SENSOR)
    genome['sourceNum'][sensor_mask] %= settings.NUM_SENSES
    genome['sourceNum'][~sensor_mask] %= settings.MAX_NEURONS
    neuron_mask = (genome['sinkType'] == settings.NEURON)
    genome['sinkNum'][neuron_mask] %= settings.MAX_NEURONS
    genome['sinkNum'][~neuron_mask] %= settings.NUM_ACTIONS
    genome['weight'] = np.random.uniform(-1.0, 1.0, size=length).astype(np.float32)
    return genome

def reproduce_genome(parent_genome):
    child_genome = parent_genome.copy()
    return improved_mutate_genome(child_genome)

def improved_mutate_genome(genome):
    used_neurons = set()
    for gene in genome:
        if gene['sourceType'] == settings.NEURON:
            used_neurons.add(int(gene['sourceNum']))
        if gene['sinkType'] == settings.NEURON:
            used_neurons.add(int(gene['sinkNum']))
    next_id = max(used_neurons) + 1 if used_neurons else 0
    def new_neuron_id():
        nonlocal next_id
        nid = next_id
        next_id += 1
        return nid
    # avoid mutation type that always adds new internal neuron connections
    mutation_types = ['add_connection', 'edit_connection', 'remove_connection']
    if len(genome) == 0:
        mutation_types = ['add_connection']
    chosen = random.choice(mutation_types)
    if chosen == 'add_connection':
        if random.random() < 0.5:
            # add a sensor -> neuron connection
            new_gene = np.empty(1, dtype=gene_dtype)
            new_gene['sourceType'] = settings.SENSOR
            new_gene['sourceNum'] = np.random.randint(0, settings.NUM_SENSES, dtype=np.uint16)
            new_gene['sinkType'] = settings.NEURON
            new_gene['sinkNum'] = new_neuron_id()
            new_gene['weight'] = np.random.uniform(-1.0, 1.0)
            genome = np.append(genome, new_gene)
        else:
            # add a neuron -> action connection
            new_gene = np.empty(1, dtype=gene_dtype)
            new_gene['sourceType'] = settings.NEURON
            new_gene['sourceNum'] = random.choice(list(used_neurons)) if used_neurons else 0
            new_gene['sinkType'] = settings.ACTION
            new_gene['sinkNum'] = np.random.randint(0, settings.NUM_ACTIONS, dtype=np.uint16)
            new_gene['weight'] = np.random.uniform(-1.0, 1.0)
            genome = np.append(genome, new_gene)
    elif chosen == 'edit_connection' and len(genome) > 0:
        idx = random.randint(0, len(genome)-1)
        field = random.choice(['sourceType', 'sinkType', 'sourceNum', 'sinkNum', 'weight'])
        if field == 'sourceType':
            genome[idx]['sourceType'] = random.randint(0, 1)
            if genome[idx]['sourceType'] == settings.SENSOR:
                genome[idx]['sourceNum'] = np.random.randint(0, settings.NUM_SENSES, dtype=np.uint16)
                genome[idx]['sinkType'] = settings.NEURON
                genome[idx]['sinkNum'] = new_neuron_id()
            else:
                genome[idx]['sourceNum'] = random.choice(list(used_neurons)) if used_neurons else 0
        elif field == 'sinkType':
            if genome[idx]['sourceType'] == settings.SENSOR:
                genome[idx]['sinkType'] = settings.NEURON
                genome[idx]['sinkNum'] = new_neuron_id()
            else:
                genome[idx]['sinkType'] = settings.ACTION if random.random() < 0.5 else settings.NEURON
                if genome[idx]['sinkType'] == settings.NEURON:
                    genome[idx]['sinkNum'] = new_neuron_id()
                else:
                    genome[idx]['sinkNum'] = np.random.randint(0, settings.NUM_ACTIONS, dtype=np.uint16)
        elif field == 'sourceNum':
            if genome[idx]['sourceType'] == settings.SENSOR:
                genome[idx]['sourceNum'] = np.random.randint(0, settings.NUM_SENSES, dtype=np.uint16)
            else:
                genome[idx]['sourceNum'] = random.choice(list(used_neurons)) if used_neurons else 0
        elif field == 'sinkNum':
            if genome[idx]['sinkType'] == settings.NEURON:
                genome[idx]['sinkNum'] = new_neuron_id()
            else:
                genome[idx]['sinkNum'] = np.random.randint(0, settings.NUM_ACTIONS, dtype=np.uint16)
        elif field == 'weight':
            genome[idx]['weight'] = np.random.uniform(-1.0, 1.0)
    elif chosen == 'remove_connection' and len(genome) > 0:
        idx = random.randint(0, len(genome)-1)
        genome = np.delete(genome, idx)
    return genome


import random
import settings

def make_random_genome():
    genome = []
    for _ in range(settings.GENOME_LENGTH):
        source_type = random.randint(0, 1)
        rand_val = random.randint(0, 1)
        sink_type = settings.NEURON if rand_val == 0 else settings.ACTION
        if source_type == settings.SENSOR:
            sink_type = settings.NEURON
        source_num = random.randint(0, 0x7FFF)
        sink_num = random.randint(0, 0x7FFF)
        if source_type == settings.SENSOR:
            source_num %= settings.NUM_SENSES
        else:
            source_num %= settings.MAX_NEURONS
        if sink_type == settings.NEURON:
            sink_num %= settings.MAX_NEURONS
        else:
            sink_num %= settings.NUM_ACTIONS
        weight = random.uniform(-1.0, 1.0)
        genome.append([source_type, source_num, sink_type, sink_num, weight])
    return genome

def reproduce_genome(parent_genome):
    child_genome = [gene[:] for gene in parent_genome]
    return mutate_genome(child_genome)

def mutate_genome(genome):
    used_neurons = set()
    for gene in genome:
        if gene[0] == settings.NEURON:
            used_neurons.add(gene[1])
        if gene[2] == settings.NEURON:
            used_neurons.add(gene[3])
    next_id = max(used_neurons) + 1 if used_neurons else 0
    def new_neuron_id():
        nonlocal next_id
        nid = next_id
        next_id += 1
        return nid
    mutation_types = ['add_connection', 'edit_connection', 'remove_connection']
    if len(genome) == 0:
        mutation_types = ['add_connection']
    chosen = random.choice(mutation_types)
    if chosen == 'add_connection':
        if random.random() < 0.5:
            new_gene = [settings.SENSOR,
                        random.randint(0, settings.NUM_SENSES - 1),
                        settings.NEURON,
                        new_neuron_id(),
                        random.uniform(-1.0, 1.0)]
        else:
            source_num = random.choice(list(used_neurons)) if used_neurons else 0
            new_gene = [settings.NEURON,
                        source_num,
                        settings.ACTION,
                        random.randint(0, settings.NUM_ACTIONS - 1),
                        random.uniform(-1.0, 1.0)]
        genome = list(genome)
        genome.append(new_gene)
    elif chosen == 'edit_connection' and len(genome) > 0:
        idx = random.randint(0, len(genome) - 1)
        gene = genome[idx]
        field = random.choice(['sourceType', 'sinkType', 'sourceNum', 'sinkNum', 'weight'])
        if field == 'sourceType':
            new_type = random.randint(0, 1)
            gene[0] = new_type
            if new_type == settings.SENSOR:
                gene[1] = random.randint(0, settings.NUM_SENSES - 1)
                gene[2] = settings.NEURON
                gene[3] = new_neuron_id()
            else:
                gene[1] = random.choice(list(used_neurons)) if used_neurons else 0
        elif field == 'sinkType':
            if gene[0] == settings.SENSOR:
                gene[2] = settings.NEURON
                gene[3] = new_neuron_id()
            else:
                if random.random() < 0.5:
                    gene[2] = settings.ACTION
                    gene[3] = random.randint(0, settings.NUM_ACTIONS - 1)
                else:
                    gene[2] = settings.NEURON
                    gene[3] = new_neuron_id()
        elif field == 'sourceNum':
            if gene[0] == settings.SENSOR:
                gene[1] = random.randint(0, settings.NUM_SENSES - 1)
            else:
                gene[1] = random.choice(list(used_neurons)) if used_neurons else 0
        elif field == 'sinkNum':
            if gene[2] == settings.NEURON:
                gene[3] = new_neuron_id()
            else:
                gene[3] = random.randint(0, settings.NUM_ACTIONS - 1)
        elif field == 'weight':
            gene[4] = random.uniform(-1.0, 1.0)
    elif chosen == 'remove_connection' and len(genome) > 0:
        idx = random.randint(0, len(genome) - 1)
        genome = [g for i, g in enumerate(genome) if i != idx]
    return genome


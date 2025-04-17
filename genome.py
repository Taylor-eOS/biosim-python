import random
import settings

def make_random_genome():
    genome = []
    P_SENSOR = 0.3
    P_NEURON_SINK = 0.7
    for _ in range(settings.GENOME_LENGTH):
        source_type = random.choices([settings.SENSOR, settings.NEURON], [P_SENSOR, 1 - P_SENSOR])[0]
        if source_type == settings.SENSOR:
            sink_type = settings.NEURON
        else:
            sink_type = random.choices([settings.NEURON, settings.ACTION], [P_NEURON_SINK, 1 - P_NEURON_SINK])[0]
        source_num = (random.randint(0, settings.NUM_SENSES - 1) if source_type == settings.SENSOR else random.randint(0, settings.MAX_NEURONS - 1))
        sink_num = (random.randint(0, settings.MAX_NEURONS - 1) if sink_type == settings.NEURON else random.randint(0, settings.NUM_ACTIONS - 1))
        weight = random.uniform(-1.0, 1.0)
        genome.append([source_type, source_num, sink_type, sink_num, weight])
    return genome

def reproduce_genome(parent_genome):
    child_genome = [gene[:] for gene in parent_genome]
    return mutate_genome(child_genome)

def mutate_genome(genome):
    #if random.random() > settings.MUTATION_RATE:
    #    return genome
    genome = list(genome)
    used_neurons = {g[1] for g in genome if g[0] == settings.NEURON}
    used_neurons |= {g[3] for g in genome if g[2] == settings.NEURON}
    next_id = max(used_neurons, default=-1) + 1
    def new_neuron_id():
        nonlocal next_id
        nid = next_id
        next_id += 1
        return nid
    p_edit = settings.MUTATION_RATE
    p_add = settings.MUTATION_RATE*0.2
    p_remove = settings.MUTATION_RATE*0.18
    sensor_add = 0.2
    if genome and random.random() < p_edit:
        gene = random.choice(genome)
        field = random.choice(['sourceType', 'sinkType', 'sourceNum', 'sinkNum', 'weight'])
        if field == 'sourceType':
            gene[0] = random.randint(0, 1)
            if gene[0] == settings.SENSOR:
                gene[1] = random.randint(0, settings.NUM_SENSES - 1)
                gene[2] = settings.NEURON
                gene[3] = new_neuron_id()
            else:
                gene[1] = random.choice(list(used_neurons)) if used_neurons else 0
        elif field == 'sinkType':
            if gene[0] == settings.SENSOR or random.random() < 0.5:
                gene[2] = settings.NEURON
                gene[3] = new_neuron_id()
            else:
                gene[2] = settings.ACTION
                gene[3] = random.randint(0, settings.NUM_ACTIONS - 1)
        elif field == 'sourceNum':
            gene[1] = (random.randint(0, settings.NUM_SENSES - 1)
                       if gene[0] == settings.SENSOR
                       else random.choice(list(used_neurons)) if used_neurons else 0)
        elif field == 'sinkNum':
            gene[3] = (new_neuron_id()
                       if gene[2] == settings.NEURON
                       else random.randint(0, settings.NUM_ACTIONS - 1))
        elif field == 'weight':
            gene[4] = random.uniform(-1.0, 1.0)
    if random.random() < p_add:
        if random.random() < sensor_add:
            new_gene = [settings.SENSOR,
                        random.randint(0, settings.NUM_SENSES - 1),
                        settings.NEURON,
                        new_neuron_id(),
                        random.uniform(-1.0, 1.0)]
        else:
            source = random.choice(list(used_neurons)) if used_neurons else 0
            new_gene = [settings.NEURON,
                        source,
                        settings.ACTION,
                        random.randint(0, settings.NUM_ACTIONS - 1),
                        random.uniform(-1.0, 1.0)]
        genome.append(new_gene)
    if genome and random.random() < p_remove:
        genome.pop(random.randint(0, len(genome) - 1))
    return genome


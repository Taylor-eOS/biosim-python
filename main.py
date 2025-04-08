import random
import math

# Define source/sink types
SENSOR = 0
NEURON = 1
ACTION = 2

# Parameters
NUM_SENSES = 3
NUM_ACTIONS = 2
MAX_NEURONS = 10
GENOME_INITIAL_LENGTH_MIN = 8
GENOME_INITIAL_LENGTH_MAX = 12

# Gene structure
class Gene:
    def __init__(self, sourceType, sourceNum, sinkType, sinkNum, weight):
        self.sourceType = sourceType
        self.sourceNum = sourceNum
        self.sinkType = sinkType
        self.sinkNum = sinkNum
        self.weight = weight

    @staticmethod
    def make_random_weight():
        return random.uniform(-1.0, 1.0)

def make_random_gene():
    sourceType = SENSOR if random.getrandbits(1) == 0 else NEURON
    sinkType = NEURON if random.getrandbits(1) == 0 else ACTION
    gene = Gene(sourceType,
                random.randint(0, 0x7fff),
                sinkType,
                random.randint(0, 0x7fff),
                Gene.make_random_weight())
    if gene.sourceType == NEURON:
        gene.sourceNum %= MAX_NEURONS
    else:
        gene.sourceNum %= NUM_SENSES
    if gene.sinkType == NEURON:
        gene.sinkNum %= MAX_NEURONS
    else:
        gene.sinkNum %= NUM_ACTIONS
    return gene

def make_random_genome():
    length = random.randint(GENOME_INITIAL_LENGTH_MIN, GENOME_INITIAL_LENGTH_MAX)
    return [make_random_gene() for _ in range(length)]

# Cull genes that refer to neurons that are never driven
def cull_unused_neurons(genome):
    inbound = {}
    for gene in genome:
        if gene.sinkType == NEURON:
            # Count only non-self connections as proper driving input.
            if gene.sinkNum not in inbound:
                inbound[gene.sinkNum] = 0
            if gene.sourceType == SENSOR or (gene.sourceType == NEURON and gene.sourceNum != gene.sinkNum):
                inbound[gene.sinkNum] += 1
    # Only keep those neurons that receive at least one non-self input.
    driven_neurons = {nid for nid, count in inbound.items() if count > 0}
    culled = []
    for gene in genome:
        if gene.sinkType == NEURON and gene.sinkNum not in driven_neurons:
            continue
        if gene.sourceType == NEURON and gene.sourceNum not in driven_neurons:
            continue
        culled.append(gene)
    return culled

# The Brain class: create wiring and run the network.
class Brain:
    def __init__(self, genome):
        # Cull unused neurons before wiring.
        self.genome = cull_unused_neurons(genome)
        self.neuron_connections = []
        self.action_connections = []
        self.build_wiring()

    def build_wiring(self):
        neuron_ids = set()
        # Gather neuron ids only from genes that survived culling.
        for gene in self.genome:
            if gene.sourceType == NEURON:
                neuron_ids.add(gene.sourceNum)
            if gene.sinkType == NEURON:
                neuron_ids.add(gene.sinkNum)
        remap = {}
        new_id = 0
        for nid in sorted(neuron_ids):
            remap[nid] = new_id
            new_id += 1
        self.num_neurons = new_id
        print("Remapped neurons:", remap)
        self.neuron_connections = []
        self.action_connections = []
        for gene in self.genome:
            g = Gene(gene.sourceType, gene.sourceNum, gene.sinkType, gene.sinkNum, gene.weight)
            if g.sourceType == NEURON:
                if g.sourceNum in remap:
                    g.sourceNum = remap[g.sourceNum]
                else:
                    continue
            if g.sinkType == NEURON:
                if g.sinkNum in remap:
                    g.sinkNum = remap[g.sinkNum]
                else:
                    continue
                self.neuron_connections.append(g)
            else:
                self.action_connections.append(g)
        print("Neuron connections:", [(g.sourceType, g.sourceNum, g.sinkType, g.sinkNum, round(g.weight,3)) for g in self.neuron_connections])
        print("Action connections:", [(g.sourceType, g.sourceNum, g.sinkType, g.sinkNum, round(g.weight,3)) for g in self.action_connections])
        self.neurons = [0.0] * self.num_neurons

    def activate(self, sensor_inputs, iterations=3):
        if len(sensor_inputs) != NUM_SENSES:
            raise ValueError("Expected sensor_inputs with length {}".format(NUM_SENSES))
        for it in range(iterations):
            new_neurons = [0.0] * self.num_neurons
            for conn in self.neuron_connections:
                if conn.sourceType == SENSOR:
                    source_val = sensor_inputs[conn.sourceNum]
                else:
                    source_val = self.neurons[conn.sourceNum]
                new_neurons[conn.sinkNum] += conn.weight * source_val
            new_neurons = [math.tanh(x) for x in new_neurons]
            self.neurons = new_neurons
            print("After iteration", it+1, "neuron outputs:", [round(n,3) for n in self.neurons])
        actions = [0.0] * NUM_ACTIONS
        for conn in self.action_connections:
            if conn.sourceType == SENSOR:
                source_val = sensor_inputs[conn.sourceNum]
            else:
                source_val = self.neurons[conn.sourceNum]
            actions[conn.sinkNum] += conn.weight * source_val
        actions = [math.tanh(a) for a in actions]
        print("Action outputs:", [round(a,3) for a in actions])
        return actions

if __name__ == '__main__':
    random.seed(42)
    genome = make_random_genome()
    print("Genome:")
    for g in genome:
        print(" SourceType:", "SENSOR" if g.sourceType==SENSOR else "NEURON",
              " Source:", g.sourceNum,
              " SinkType:", "NEURON" if g.sinkType==NEURON else "ACTION",
              " Sink:", g.sinkNum,
              " Weight:", round(g.weight,3))
    brain = Brain(genome)
    sensor_inputs = [0.5, -0.3, 0.8]
    print("Activating brain with sensor inputs:", sensor_inputs)
    brain.activate(sensor_inputs)


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
        self.sourceType = sourceType  # SENSOR or NEURON (for source)
        self.sourceNum = sourceNum    # if sensor, index within NUM_SENSES; if neuron, arbitrary id (will be remapped)
        self.sinkType = sinkType      # for sink: if NEURON then neuron, if ACTION then action
        self.sinkNum = sinkNum        # either neuron id (to be remapped) or action index
        self.weight = weight

    @staticmethod
    def make_random_weight():
        # random weight in a small range
        return random.uniform(-1.0, 1.0)

def make_random_gene():
    # For source: choose sensor or neuron with equal chance.
    sourceType = SENSOR if random.getrandbits(1) == 0 else NEURON
    # For sink: choose neuron (i.e., internal computation) or action with equal chance.
    sinkType = NEURON if random.getrandbits(1) == 0 else ACTION
    # Use a wide range for temporary gene numbers. Later they are reduced modulo limits.
    gene = Gene(sourceType, random.randint(0, 0x7fff), sinkType, random.randint(0, 0x7fff), Gene.make_random_weight())
    # Remap numbers immediately into valid ranges
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

# The Brain class: create wiring and run the network.
class Brain:
    def __init__(self, genome):
        self.genome = genome
        # We'll split connections into two lists:
        # one for neuron-targeting genes and one for action-targeting genes.
        self.neuron_connections = []  # connections with sinkType==NEURON
        self.action_connections = []  # connections with sinkType==ACTION
        # Build wiring with remapped neuron indices from genome
        self.build_wiring()

    def build_wiring(self):
        # We'll collect all neuron IDs that appear in the genome.
        neuron_ids = set()
        for gene in self.genome:
            if gene.sourceType == NEURON:
                neuron_ids.add(gene.sourceNum)
            if gene.sinkType == NEURON:
                neuron_ids.add(gene.sinkNum)
        # Remap neuron IDs to a compact range [0, n_neurons)
        remap = {}
        new_id = 0
        for nid in sorted(neuron_ids):
            remap[nid] = new_id
            new_id += 1
        self.num_neurons = new_id
        # For tracing
        print("Remapped neurons:", remap)

        # Store connections with remapped neuron numbers.
        self.neuron_connections = []
        self.action_connections = []
        for gene in self.genome:
            # Make a shallow copy so we can remap numbers in the copy.
            g = Gene(gene.sourceType, gene.sourceNum, gene.sinkType, gene.sinkNum, gene.weight)
            if g.sourceType == NEURON:
                if g.sourceNum in remap:
                    g.sourceNum = remap[g.sourceNum]
                else:
                    continue  # skip gene if source not remapped (shouldn't happen)
            if g.sinkType == NEURON:
                if g.sinkNum in remap:
                    g.sinkNum = remap[g.sinkNum]
                else:
                    continue
                self.neuron_connections.append(g)
            else:
                self.action_connections.append(g)
        print("Neuron connections:", [(g.sourceType, g.sourceNum, g.sinkType, g.sinkNum, round(g.weight, 2)) for g in self.neuron_connections])
        print("Action connections:", [(g.sourceType, g.sourceNum, g.sinkType, g.sinkNum, round(g.weight, 2)) for g in self.action_connections])

        # Initialize neuron outputs
        self.neurons = [0.0] * self.num_neurons

    def activate(self, sensor_inputs, iterations=3):
        # sensor_inputs: list of floats for each sensor (size NUM_SENSES)
        if len(sensor_inputs) != NUM_SENSES:
            raise ValueError("Expected sensor_inputs with length {}".format(NUM_SENSES))
        # Run recurrent updates for neurons
        for it in range(iterations):
            new_neurons = [0.0] * self.num_neurons
            # Process all connections that feed into a neuron.
            for conn in self.neuron_connections:
                if conn.sourceType == SENSOR:
                    source_val = sensor_inputs[conn.sourceNum]
                else:  # NEURON
                    source_val = self.neurons[conn.sourceNum]
                new_neurons[conn.sinkNum] += conn.weight * source_val
            # Apply tanh activation
            new_neurons = [math.tanh(x) for x in new_neurons]
            self.neurons = new_neurons
            print("After iteration", it+1, "neuron outputs:", [round(n,3) for n in self.neurons])
        # Compute action outputs using final neuron activations (one pass)
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
              " Weight:", round(g.weight, 3))
    brain = Brain(genome)
    # Dummy sensor inputs; these could be positions, distances, or other values.
    sensor_inputs = [0.5, -0.3, 0.8]
    print("Activating brain with sensor inputs:", sensor_inputs)
    brain.activate(sensor_inputs)


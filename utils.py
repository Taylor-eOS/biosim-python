import random
SENSOR = 0
NEURON = 1
ACTION = 2

#Parameters for genome and network.
NUM_SENSES = 8
NUM_ACTIONS = 8
MAX_NEURONS = 16
GENOME_INITIAL_LENGTH_MIN = 40
GENOME_INITIAL_LENGTH_MAX = 40
POPULATION_SIZE = 5

#Gene structure
class Gene:
    def __init__(self, sourceType, sourceNum, sinkType, sinkNum, weight):
        self.sourceType = sourceType    #SENSOR or NEURON (for source)
        self.sourceNum = sourceNum      #if sensor, index within NUM_SENSES; if neuron, arbitrary id (will be remapped)
        self.sinkType = sinkType        #if NEURON then neuron, if ACTION then action
        self.sinkNum = sinkNum          #either neuron id (to be remapped) or action index
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
    #Immediately remap gene values into valid ranges.
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


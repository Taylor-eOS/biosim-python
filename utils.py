import random
SENSOR = 0
NEURON = 1
ACTION = 2

NUM_SENSES = 4
NUM_ACTIONS = 2
MAX_NEURONS = 20
GENOME_INITIAL_LENGTH_MIN = 30
GENOME_INITIAL_LENGTH_MAX = 30
POPULATION_SIZE = 8

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
    #if random.random() < 0.7: #Testing genome
    #    return Gene(SENSOR, 2, ACTION, 0, random.uniform(-1.0, 1.0))
    #    return Gene(
    #        sourceType=SENSOR,
    #        sourceNum=random.choice([2, 3]),  #Only proximity/direction
    #        sinkType=ACTION,
    #        sinkNum=random.randint(0, 1),
    #        weight=random.uniform(-2.0, 2.0))

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


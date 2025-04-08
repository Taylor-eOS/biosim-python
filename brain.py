import math
from utils import SENSOR, NEURON, ACTION, NUM_SENSES, NUM_ACTIONS, MAX_NEURONS

# Cull genes that don't drive any neurons.
def cull_unused_neurons(genome):
    inbound = {}
    for gene in genome:
        if gene.sinkType == NEURON:
            if gene.sinkNum not in inbound:
                inbound[gene.sinkNum] = 0
            if gene.sourceType == SENSOR or (gene.sourceType == NEURON and gene.sourceNum != gene.sinkNum):
                inbound[gene.sinkNum] += 1
    driven_neurons = {nid for nid, count in inbound.items() if count > 0}
    culled = []
    for gene in genome:
        if gene.sinkType == NEURON and gene.sinkNum not in driven_neurons:
            continue
        if gene.sourceType == NEURON and gene.sourceNum not in driven_neurons:
            continue
        culled.append(gene)
    return culled

class Brain:
    def __init__(self, genome, cull=True):
        # Optionally cull unused genes.
        self.genome = cull_unused_neurons(genome) if cull else genome
        self.neuron_connections = []  # Those with sinkType == NEURON.
        self.action_connections = []  # Those with sinkType == ACTION.
        self.build_wiring()

    def build_wiring(self):
        # Gather neuron ids appearing in the (culled) genome.
        neuron_ids = set()
        for gene in self.genome:
            if gene.sourceType == NEURON:
                neuron_ids.add(gene.sourceNum)
            if gene.sinkType == NEURON:
                neuron_ids.add(gene.sinkNum)
        # Remap these neuron ids to consecutive numbers.
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
            # Create a shallow copy and remap neuron numbers.
            g = type(gene)(gene.sourceType, gene.sourceNum, gene.sinkType, gene.sinkNum, gene.weight)
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
        print("Neuron connections:", [(g.sourceType, g.sourceNum, g.sinkType, g.sinkNum, round(g.weight,2)) for g in self.neuron_connections])
        print("Action connections:", [(g.sourceType, g.sourceNum, g.sinkType, g.sinkNum, round(g.weight,2)) for g in self.action_connections])
        self.neurons = [0.0] * self.num_neurons

    def activate(self, sensor_inputs, iterations=3):
        # sensor_inputs should be list of floats of length NUM_SENSES.
        if len(sensor_inputs) != NUM_SENSES:
            raise ValueError("Expected {} sensor inputs".format(NUM_SENSES))
        for it in range(iterations):
            new_neurons = [0.0] * self.num_neurons
            for conn in self.neuron_connections:
                if conn.sourceType == SENSOR:
                    source_val = sensor_inputs[conn.sourceNum]
                else:
                    source_val = self.neurons[conn.sourceNum]
                new_neurons[conn.sinkNum] += conn.weight * source_val
            self.neurons = [math.tanh(x) for x in new_neurons]
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


import math
from utils import SENSOR, NEURON, ACTION, NUM_SENSES, NUM_ACTIONS, MAX_NEURONS, POPULATION_SIZE, log_file
from display_network_diagram import GraphApp

class Brain:
    def __init__(self, genome, cull=True):
        self.genome = cull_unused_neurons(genome) if cull else genome
        self.neuron_connections = []
        self.action_connections = []
        self.build_wiring()

    def build_wiring(self):
        neuron_ids = set()
        for gene in self.genome:
            if gene.sourceType == NEURON:
                neuron_ids.add(gene.sourceNum)
            if gene.sinkType == NEURON:
                neuron_ids.add(gene.sinkNum)
        #Remap these neuron ids to consecutive numbers.
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
        neuron_connections = [(g.sourceType, g.sourceNum, g.sinkType, g.sinkNum, round(g.weight,2)) for g in self.neuron_connections]
        action_connections = [(g.sourceType, g.sourceNum, g.sinkType, g.sinkNum, round(g.weight,2)) for g in self.action_connections]
        print("Neuron connections:", neuron_connections)
        print("Action connections:", action_connections)
        with open(log_file, "a") as f:
            f.write("Neuron connections: " + str(neuron_connections) + "\n")
            f.write("Action connections: " + str(action_connections) + "\n")
        #GraphApp(neuron_connections + action_connections)
        self.neurons = [0.0] * self.num_neurons

    def activate(self, sensor_inputs, iterations=2):
        #sensor_inputs should be list of floats of length NUM_SENSES.
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

def cull_unused_neurons(genome):
    #First pass: identify neurons that receive input from a sensor or from another neuron
    driven_neurons = set()
    for gene in genome:
        if gene.sinkType == NEURON:
            if gene.sourceType in (SENSOR, NEURON) and gene.sourceNum != gene.sinkNum:
                driven_neurons.add(gene.sinkNum)
    #Iteratively expand the set of active neurons by following the graph
    changed = True
    while changed:
        changed = False
        for gene in genome:
            if gene.sinkType == NEURON and gene.sourceType == NEURON:
                if gene.sourceNum in driven_neurons and gene.sinkNum not in driven_neurons:
                    driven_neurons.add(gene.sinkNum)
                    changed = True
    #Now select only genes where both source and sink are valid (or source is a sensor)
    active_genes = []
    for gene in genome:
        if gene.sinkType == ACTION:
            if gene.sourceType == SENSOR or gene.sourceNum in driven_neurons:
                active_genes.append(gene)
        elif gene.sinkType == NEURON:
            if gene.sinkNum in driven_neurons:
                if gene.sourceType == SENSOR or gene.sourceNum in driven_neurons:
                    active_genes.append(gene)
    return active_genes


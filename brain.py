import math
import settings

class Brain:
    def __init__(self, genome, cull=True):
        self.genome = self.cull_unused_neurons(genome) if cull else genome
        self.remap_neurons()
        self.build_wiring()
        self.neurons = [0.0] * self.num_neurons

    def remap_neurons(self):
        src_neurons = [g[1] for g in self.genome if g[0] == settings.NEURON]
        sink_neurons = [g[3] for g in self.genome if g[2] == settings.NEURON]
        all_neurons = sorted(set(src_neurons + sink_neurons))
        self.num_neurons = len(all_neurons)
        remap_dict = {old: new for new, old in enumerate(all_neurons)}
        for gene in self.genome:
            if gene[0] == settings.NEURON:
                gene[1] = remap_dict[gene[1]]
            if gene[2] == settings.NEURON:
                gene[3] = remap_dict[gene[3]]

    def build_wiring(self):
        self.sensor_neuron = [g for g in self.genome if g[2] == settings.NEURON and g[0] == settings.SENSOR]
        self.neuron_neuron = [g for g in self.genome if g[2] == settings.NEURON and g[0] == settings.NEURON]
        self.sensor_action = [g for g in self.genome if g[2] == settings.ACTION and g[0] == settings.SENSOR]
        self.neuron_action = [g for g in self.genome if g[2] == settings.ACTION and g[0] == settings.NEURON]

    def activate(self, sensor_inputs, iterations=2):
        sensor_inputs = list(sensor_inputs)
        for _ in range(iterations):
            new_neurons = [0.0] * self.num_neurons
            for conn in self.sensor_neuron:
                val = sensor_inputs[conn[1]] * conn[4]
                new_neurons[conn[3]] += val
            for conn in self.neuron_neuron:
                val = self.neurons[conn[1]] * conn[4]
                new_neurons[conn[3]] += val
            self.neurons = [math.tanh(x) for x in new_neurons]
        actions = [0.0] * settings.NUM_ACTIONS
        for conn in self.sensor_action:
            val = sensor_inputs[conn[1]] * conn[4]
            actions[conn[3]] += val
        for conn in self.neuron_action:
            val = self.neurons[conn[1]] * conn[4]
            actions[conn[3]] += val
        return [math.tanh(x) for x in actions]

    def cull_unused_neurons(self, genome):
        driven = set()
        for row in genome:
            if row[2] == settings.NEURON and row[0] in (settings.SENSOR, settings.NEURON) and row[1] != row[3]:
                driven.add(row[3])
        changed = True
        while changed:
            changed = False
            for row in genome:
                if row[2] == settings.NEURON and row[0] == settings.NEURON and row[1] in driven and row[3] not in driven:
                    driven.add(row[3])
                    changed = True
        valid = []
        for row in genome:
            if row[2] == settings.ACTION:
                if row[0] == settings.SENSOR or row[1] in driven:
                    valid.append(row)
            elif row[2] == settings.NEURON:
                if row[3] in driven and (row[0] == settings.SENSOR or row[1] in driven):
                    valid.append(row)
        return valid


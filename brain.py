import numpy as np
import math
import settings

class Brain:
    def __init__(self, genome, cull=True):
        self.genome = self.cull_unused_neurons(genome) if cull else genome
        self.remap_neurons()
        self.build_wiring()
        self.neurons = np.zeros(self.num_neurons, dtype=np.float32)

    def remap_neurons(self):
        src_mask = self.genome['sourceType'] == settings.NEURON
        sink_mask = self.genome['sinkType'] == settings.NEURON
        src_neurons = self.genome['sourceNum'][src_mask]
        sink_neurons = self.genome['sinkNum'][sink_mask]
        all_neurons = np.unique(np.concatenate((src_neurons, sink_neurons)).astype(np.int64))
        self.num_neurons = len(all_neurons)
        remap_dict = {old_id: new_id for new_id, old_id in enumerate(all_neurons)}
        src_vals = self.genome['sourceNum'][src_mask]
        if src_vals.size > 0:
            self.genome['sourceNum'][src_mask] = np.vectorize(remap_dict.get)(src_vals)
        self.genome['sinkNum'][sink_mask] = np.vectorize(remap_dict.get)(self.genome['sinkNum'][sink_mask])

    def build_wiring(self):
        neuron_connections = self.genome[self.genome['sinkType'] == settings.NEURON]
        self.sensor_neuron = neuron_connections[neuron_connections['sourceType'] == settings.SENSOR]
        self.neuron_neuron = neuron_connections[neuron_connections['sourceType'] == settings.NEURON]
        action_connections = self.genome[self.genome['sinkType'] == settings.ACTION]
        self.sensor_action = action_connections[action_connections['sourceType'] == settings.SENSOR]
        self.neuron_action = action_connections[action_connections['sourceType'] == settings.NEURON]

    def activate(self, sensor_inputs, iterations=2):
        sensor_inputs = np.array(sensor_inputs, dtype=np.float32)
        for _ in range(iterations):
            new_neurons = np.zeros(self.num_neurons, dtype=np.float32)
            if self.sensor_neuron.size:
                src_vals = sensor_inputs[self.sensor_neuron['sourceNum']]
                np.add.at(new_neurons, self.sensor_neuron['sinkNum'],
                          self.sensor_neuron['weight'] * src_vals)
            if self.neuron_neuron.size:
                src_vals = self.neurons[self.neuron_neuron['sourceNum']]
                np.add.at(new_neurons, self.neuron_neuron['sinkNum'],
                          self.neuron_neuron['weight'] * src_vals)
            self.neurons = np.tanh(new_neurons)
            if False: print("Neuron outputs:", ["{:.3f}".format(x) for x in np.round(self.neurons, 3)])
        actions = np.zeros(settings.NUM_ACTIONS, dtype=np.float32)
        if self.sensor_action.size:
            src_vals = sensor_inputs[self.sensor_action['sourceNum']]
            np.add.at(actions, self.sensor_action['sinkNum'],
                      self.sensor_action['weight'] * src_vals)
        if self.neuron_action.size:
            src_vals = self.neurons[self.neuron_action['sourceNum']]
            np.add.at(actions, self.neuron_action['sinkNum'],
                      self.neuron_action['weight'] * src_vals)
        actions = np.tanh(actions)
        if False: print("Action outputs:", ["{:.3f}".format(x) for x in np.round(actions, 3)])
        return actions

    def cull_unused_neurons(self, genome):
        driven = set()
        for row in genome:
            if row['sinkType'] == settings.NEURON and row['sourceType'] in (settings.SENSOR, settings.NEURON) and row['sourceNum'] != row['sinkNum']:
                driven.add(int(row['sinkNum']))
        changed = True
        while changed:
            changed = False
            for row in genome:
                if row['sinkType'] == settings.NEURON and row['sourceType'] == settings.NEURON:
                    if int(row['sourceNum']) in driven and int(row['sinkNum']) not in driven:
                        driven.add(int(row['sinkNum']))
                        changed = True
        valid = []
        for row in genome:
            if row['sinkType'] == settings.ACTION:
                if row['sourceType'] == settings.SENSOR or int(row['sourceNum']) in driven:
                    valid.append(row)
            elif row['sinkType'] == settings.NEURON:
                if int(row['sinkNum']) in driven and (row['sourceType'] == settings.SENSOR or int(row['sourceNum']) in driven):
                    valid.append(row)
        return np.array(valid, dtype=genome.dtype)


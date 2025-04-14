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
        src_neurons = self.genome['sourceNum'][self.genome['sourceType'] == settings.NEURON]
        sink_neurons = self.genome['sinkNum'][self.genome['sinkType'] == settings.NEURON]
        all_neurons = np.union1d(src_neurons, sink_neurons)
        sorted_neurons = np.sort(all_neurons)
        self.num_neurons = len(sorted_neurons)
        mapping = np.full(settings.MAX_NEURONS, -1, dtype=np.int16)
        for new_id, old_id in enumerate(sorted_neurons):
            mapping[old_id] = new_id
        neuron_src = (self.genome['sourceType'] == settings.NEURON)
        self.genome['sourceNum'][neuron_src] = mapping[self.genome['sourceNum'][neuron_src]]
        neuron_sink = (self.genome['sinkType'] == settings.NEURON)
        self.genome['sinkNum'][neuron_sink] = mapping[self.genome['sinkNum'][neuron_sink]]

    def build_wiring(self):
        neuron_connections = self.genome[self.genome['sinkType'] == settings.NEURON]
        self.sensor_neuron = neuron_connections[neuron_connections['sourceType'] == settings.SENSOR]
        self.neuron_neuron = neuron_connections[neuron_connections['sourceType'] == settings.NEURON]
        action_connections = self.genome[self.genome['sinkType'] == settings.ACTION]
        self.sensor_action = action_connections[action_connections['sourceType'] == settings.SENSOR]
        self.neuron_action = action_connections[action_connections['sourceType'] == settings.NEURON]
        if settings.PRINT_GENOME or settings.WRITE_GENOME:
            neuron_connections = np.concatenate((self.sensor_neuron, self.neuron_neuron)).tolist()
            action_connections = self.neuron_action.tolist()
        if settings.PRINT_GENOME:
            print("Neuron connections:", neuron_connections)
            print("Action connections:", action_connections)
        if settings.WRITE_GENOME:
            with open(settings.log_file, "a") as f:
                f.write("Neuron connections: " + str(neuron_connections) + "\n")
                f.write("Action connections: " + str(action_connections) + "\n\n")

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


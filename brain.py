import numpy as np
import math
from genome import SENSOR, NEURON, ACTION, NUM_SENSES, NUM_ACTIONS, MAX_NEURONS, log_file

class Brain:
    def __init__(self, genome, cull=True):
        self.genome = self.cull_unused_neurons(genome) if cull else genome
        self.remap_neurons()
        self.build_wiring()
        self.neurons = np.zeros(self.num_neurons, dtype=np.float32)

    def remap_neurons(self):
        src_neurons = self.genome['sourceNum'][self.genome['sourceType'] == NEURON]
        sink_neurons = self.genome['sinkNum'][self.genome['sinkType'] == NEURON]
        all_neurons = np.union1d(src_neurons, sink_neurons)
        sorted_neurons = np.sort(all_neurons)
        self.num_neurons = len(sorted_neurons)
        mapping = np.full(MAX_NEURONS, -1, dtype=np.int16)
        for new_id, old_id in enumerate(sorted_neurons):
            mapping[old_id] = new_id
        neuron_src = (self.genome['sourceType'] == NEURON)
        self.genome['sourceNum'][neuron_src] = mapping[self.genome['sourceNum'][neuron_src]]
        neuron_sink = (self.genome['sinkType'] == NEURON)
        self.genome['sinkNum'][neuron_sink] = mapping[self.genome['sinkNum'][neuron_sink]]

    def build_wiring(self):
        neuron_connections = self.genome[self.genome['sinkType'] == NEURON]
        self.sensor_neuron = neuron_connections[neuron_connections['sourceType'] == SENSOR]
        self.neuron_neuron = neuron_connections[neuron_connections['sourceType'] == NEURON]
        action_connections = self.genome[self.genome['sinkType'] == ACTION]
        self.sensor_action = action_connections[action_connections['sourceType'] == SENSOR]
        self.neuron_action = action_connections[action_connections['sourceType'] == NEURON]
        print("Neuron connections (sensor->neuron):", self.sensor_neuron.tolist())
        print("Neuron connections (neuron->neuron):", self.neuron_neuron.tolist())
        print("Action connections (sensor->action):", self.sensor_action.tolist())
        print("Action connections (neuron->action):", self.neuron_action.tolist())
        
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
            print("Neuron outputs:", np.round(self.neurons, 3).tolist())
        actions = np.zeros(NUM_ACTIONS, dtype=np.float32)
        if self.sensor_action.size:
            src_vals = sensor_inputs[self.sensor_action['sourceNum']]
            np.add.at(actions, self.sensor_action['sinkNum'],
                      self.sensor_action['weight'] * src_vals)
        if self.neuron_action.size:
            src_vals = self.neurons[self.neuron_action['sourceNum']]
            np.add.at(actions, self.neuron_action['sinkNum'],
                      self.neuron_action['weight'] * src_vals)
        actions = np.tanh(actions)
        print("Action outputs:", np.round(actions, 3).tolist())
        return actions

    def cull_unused_neurons(self, genome):
        driven = set()
        for row in genome:
            if row['sinkType'] == NEURON and row['sourceType'] in (SENSOR, NEURON) and row['sourceNum'] != row['sinkNum']:
                driven.add(int(row['sinkNum']))
        changed = True
        while changed:
            changed = False
            for row in genome:
                if row['sinkType'] == NEURON and row['sourceType'] == NEURON:
                    if int(row['sourceNum']) in driven and int(row['sinkNum']) not in driven:
                        driven.add(int(row['sinkNum']))
                        changed = True
        valid = []
        for row in genome:
            if row['sinkType'] == ACTION:
                if row['sourceType'] == SENSOR or int(row['sourceNum']) in driven:
                    valid.append(row)
            elif row['sinkType'] == NEURON:
                if int(row['sinkNum']) in driven and (row['sourceType'] == SENSOR or int(row['sourceNum']) in driven):
                    valid.append(row)
        return np.array(valid, dtype=genome.dtype)


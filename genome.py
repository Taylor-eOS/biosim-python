import numpy as np
import random
from settings import SENSOR, NEURON, ACTION, NUM_SENSES, NUM_ACTIONS, MAX_NEURONS, GENOME_LENGTH

gene_dtype = np.dtype([
    ('sourceType', np.uint8),
    ('sourceNum', np.uint8),
    ('sinkType', np.uint8),
    ('sinkNum', np.uint8),
    ('weight', np.float32)])

def make_random_genome():
    length = GENOME_LENGTH
    genome = np.empty(length, dtype=gene_dtype)
    genome['sourceType'] = np.random.randint(0, 2, size=length, dtype=np.uint8)
    rand_vals = np.random.randint(0, 2, size=length, dtype=np.uint8)
    genome['sinkType'] = np.where(rand_vals == 0, NEURON, ACTION)
    sensor_source_mask = (genome['sourceType'] == SENSOR)
    genome['sinkType'][sensor_source_mask] = NEURON
    genome['sourceNum'] = np.random.randint(0, 0x8000, size=length, dtype=np.uint16)
    genome['sinkNum'] = np.random.randint(0, 0x8000, size=length, dtype=np.uint16)
    sensor_mask = (genome['sourceType'] == SENSOR)
    genome['sourceNum'][sensor_mask] %= NUM_SENSES
    genome['sourceNum'][~sensor_mask] %= MAX_NEURONS
    neuron_mask = (genome['sinkType'] == NEURON)
    genome['sinkNum'][neuron_mask] %= MAX_NEURONS
    genome['sinkNum'][~neuron_mask] %= NUM_ACTIONS
    genome['weight'] = np.random.uniform(-1.0, 1.0, size=length).astype(np.float32)
    return genome


import numpy as np
import random
import settings

gene_dtype = np.dtype([
    ('sourceType', np.uint8),
    ('sourceNum', np.uint8),
    ('sinkType', np.uint8),
    ('sinkNum', np.uint8),
    ('weight', np.float32)])

def make_random_genome():
    length = settings.GENOME_LENGTH
    genome = np.empty(length, dtype=gene_dtype)
    genome['sourceType'] = np.random.randint(0, 2, size=length, dtype=np.uint8)
    rand_vals = np.random.randint(0, 2, size=length, dtype=np.uint8)
    genome['sinkType'] = np.where(rand_vals == 0, settings.NEURON, settings.ACTION)
    sensor_source_mask = (genome['sourceType'] == settings.SENSOR)
    genome['sinkType'][sensor_source_mask] = settings.NEURON
    genome['sourceNum'] = np.random.randint(0, 0x8000, size=length, dtype=np.uint16)
    genome['sinkNum'] = np.random.randint(0, 0x8000, size=length, dtype=np.uint16)
    sensor_mask = (genome['sourceType'] == settings.SENSOR)
    genome['sourceNum'][sensor_mask] %= settings.NUM_SENSES
    genome['sourceNum'][~sensor_mask] %= settings.MAX_NEURONS
    neuron_mask = (genome['sinkType'] == settings.NEURON)
    genome['sinkNum'][neuron_mask] %= settings.MAX_NEURONS
    genome['sinkNum'][~neuron_mask] %= settings.NUM_ACTIONS
    genome['weight'] = np.random.uniform(-1.0, 1.0, size=length).astype(np.float32)
    return genome


import random
from individual import Individual
from settings import POPULATION_SIZE, DEBUG

class Simulation:
    def __init__(self, population_size=POPULATION_SIZE):
        self.population_size = population_size
        self.generation = 0
        self.current_step = 0
        self.init_population()

    def init_population(self):
        self.population = []
        for _ in range(self.population_size):
            ind = Individual(x=random.uniform(0, 100), y=random.uniform(0, 100))
            self.population.append(ind)

    def step(self, get_sensor_inputs=None):
        for ind in self.population:
            sensor_inputs = get_sensor_inputs(ind) if get_sensor_inputs else [ind.x/100, ind.y/100]
            actions = ind.update(sensor_inputs)
            dx = 1 if actions[0] > 0.5 else -1 if actions[0] < -0.5 else 0
            dy = 1 if actions[1] > 0.5 else -1 if actions[1] < -0.5 else 0
            ind.x = max(1, min(99, ind.x + dx))
            ind.y = max(1, min(99, ind.y + dy))
            if DEBUG: print(f"Individual at ({ind.x:.1f}, {ind.y:.1f}) moved by: ({dx}, {dy})")

    def update(self, generation_steps, sensor_callback=None):
        self.step(get_sensor_inputs=sensor_callback)
        self.current_step += 1
        if self.current_step >= generation_steps:
            survivors = self.get_survivors()
            print(f"Generation {self.generation} survivors: {len(survivors)}, {len(survivors)/self.population_size*100:.0f}%")
            if not survivors:
                survivors = self.population[:]
                print("No survivors on right half. Using full population for reproduction.")
            new_population = []
            while len(new_population) < self.population_size:
                parent = random.choice(survivors)
                child = Individual(x=random.uniform(0, 100), y=random.uniform(0, 100), genome=parent.genome)
                new_population.append(child)
            self.population = new_population
            self.generation += 1
            self.current_step = 0

    def get_survivors(self):
        #return [ind for ind in self.population if ind.x > 85]
        return [ind for ind in self.population if 40 < ind.x < 60]


import random
import settings
from individual import Individual

class Simulation:
    def __init__(self):
        self.generation = 0
        self.current_step = 0
        self.survival_rate = 0
        self.training_stage = 0
        self.init_population()

    def init_population(self):
        self.population = []
        for _ in range(settings.POPULATION_SIZE):
            ind = Individual(x=random.randint(5, 95), y=random.randint(5, 95))
            self.population.append(ind)

    def step(self, get_sensor_inputs=None):
        for ind in self.population:
            sensor_inputs = get_sensor_inputs(ind) if get_sensor_inputs else [ind.x/100, ind.y/100]
            actions = ind.update(sensor_inputs)
            dx = 1 if actions[0] > 0.5 else -1 if actions[0] < -0.5 else 0
            dy = 1 if actions[1] > 0.5 else -1 if actions[1] < -0.5 else 0
            ind.x = max(1, min(99, ind.x + dx))
            ind.y = max(1, min(99, ind.y + dy))
            ind.last_dx = dx
            ind.last_dy = dy
            if False: print(f"Individual at ({ind.x:.1f}, {ind.y:.1f}) moved by: ({dx}, {dy})")

    def update(self, generation_steps, sensor_callback=None):
        self.step(get_sensor_inputs=sensor_callback)
        self.current_step += 1
        if self.current_step >= generation_steps:
            survivors = self.get_survivors()
            self.survival_rate = len(survivors) / settings.POPULATION_SIZE
            print(f"Generation {self.generation} survivors: {len(survivors)}, {self.survival_rate*100:.0f}%")
            if not survivors:
                survivors = self.population[:]
                #print("No survivors")
            new_population = []
            while len(new_population) < settings.POPULATION_SIZE:
                parent = random.choice(survivors)
                child = Individual(x=random.randint(5, 95), y=random.randint(5, 95), genome=parent.genome)
                new_population.append(child)
            self.population = new_population
            self.generation += 1
            self.current_step = 0

    def get_survivors(self):
        def meets_criteria(ind):
            #return ind.x > 80
            #return 80 < ind.x < 98
            if self.training_stage == 0:
                return 32 < ind.x < 68 and 32 < ind.y < 68
            elif self.training_stage == 1:
                return 36 < ind.x < 64 and 36 < ind.y < 64
            elif self.training_stage == 2:
                return 40 < ind.x < 60 and 40 < ind.y < 60
        if self.survival_rate > 0.9 and self.training_stage < 3:
            self.training_stage += 1
            print(f"Set training stage to {self.training_stage}")
        return [ind for ind in self.population if meets_criteria(ind)]


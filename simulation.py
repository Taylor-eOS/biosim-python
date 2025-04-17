import random
import settings
from individual import Individual
from genome import reproduce_genome

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
            if len(actions) > 2 and actions[2] > 0.8:
                dx, dy = 0, 0
            ind.x = max(1, min(99, ind.x + dx))
            ind.y = max(1, min(99, ind.y + dy))
            ind.last_dx = dx
            ind.last_dy = dy

    def update(self, generation_steps, sensor_callback=None):
        self.step(get_sensor_inputs=sensor_callback)
        self.current_step += 1
        if self.current_step >= generation_steps:
            survivors = self.get_survivors()
            self.survival_rate = len(survivors) / settings.POPULATION_SIZE
            print(f"Generation {self.generation} survivors: {len(survivors)}, {self.survival_rate*100:.0f}%")
            if settings.PRINT_GENOME or settings.WRITE_GENOME:
                example = survivors[0] if survivors else self.population[0]
                example_genome = example.genome
                if settings.PRINT_GENOME:
                    print(f"Example genome for generation {self.generation}:", example_genome)
                if settings.WRITE_GENOME:
                    with open(settings.log_file, "w") as f:
                        f.write(f"Example genome for generation {self.generation}: {example_genome}\n")
            if not survivors:
                survivors = self.population[:]
                if False: print("No survivors")
            new_population = []
            while len(new_population) < settings.POPULATION_SIZE:
                parent = random.choice(survivors)
                child_genome = reproduce_genome(parent.genome)
                child = Individual(
                    x=random.randint(5, 95),
                    y=random.randint(5, 95),
                    genome=child_genome)
                new_population.append(child)
            self.population = new_population
            self.generation += 1
            self.current_step = 0

    def get_survivors(self):
        def meets_criteria(ind):
            #return ind.x > 75
            return 40 < ind.x < 60
            #if self.training_stage == 0:
            #    return 30 < ind.x < 70
            #elif self.training_stage == 1:
            #    return 40 < ind.x < 60 and 20 < ind.y < 80
            #elif self.training_stage == 2:
            #    return 42 < ind.x < 58 and 30 < ind.y < 70
        #if self.survival_rate >= 0.95 and self.training_stage <= 2:
        #    self.training_stage += 1
        #    print(f"Set training stage to {self.training_stage}")
        return [ind for ind in self.population if meets_criteria(ind)]


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
            if actions[2] > 0.8:
                dx, dy = 0, 0
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
            if settings.PRINT_GENOME or settings.WRITE_GENOME:
                example = survivors[0] if survivors else self.population[0]
                example_genome = example.genome.tolist()
                if settings.PRINT_GENOME:
                    print(f"Example Genome for Generation {self.generation}:", example_genome)
                if settings.WRITE_GENOME:
                    with open(settings.log_file, "a") as f:
                        f.write("Example Genome for Generation " + str(self.generation) + ": " +
                                str(example_genome) + "\n")
            if not survivors:
                survivors = self.population[:]
                if False: print("No survivors")
            new_population = []
            new_population = []
            while len(new_population) < settings.POPULATION_SIZE:
                parent = random.choice(survivors)
                child_genome = reproduce_genome(parent.genome)
                child = Individual(x=random.randint(5, 95), y=random.randint(5, 95), genome=child_genome)
                new_population.append(child)
            self.population = new_population
            self.generation += 1
            self.current_step = 0

    def get_survivors(self):
        def meets_criteria(ind):
            #return ind.x > 75
            #return 80 < ind.x < 98
            return 40 < ind.x < 60
        #    if self.training_stage == 0:
        #        return 32 < ind.x < 68 and 32 < ind.y < 68
        #    elif self.training_stage == 1:
        #        return 36 < ind.x < 64 and 36 < ind.y < 64
        #    elif self.training_stage == 2:
        #        return 40 < ind.x < 60 and 40 < ind.y < 60
        #if self.survival_rate > 0.9 and self.training_stage < 3:
        #    self.training_stage += 1
        #    print(f"Set training stage to {self.training_stage}")
        return [ind for ind in self.population if meets_criteria(ind)]


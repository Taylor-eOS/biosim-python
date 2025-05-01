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
        self.food_position = (random.randint(1, 99), random.randint(1, 99))
        self.init_population()

    def init_population(self):
        self.population = []
        for _ in range(settings.POPULATION_SIZE):
            ind = Individual(x=random.randint(5, 95), y=random.randint(5, 95))
            self.population.append(ind)

    def step(self, get_sensor_inputs=None):
        for ind in self.population:
            if get_sensor_inputs:
                sensor_inputs = get_sensor_inputs(
                    ind=ind,
                    population=self.population,
                    step=self.current_step,
                    food_position=self.food_position)
            else:
                sensor_inputs = [
                    ind.x/100, 
                    ind.y/100,
                    (self.food_position[0] - ind.x)/100,
                    (self.food_position[1] - ind.y)/100]
            actions = ind.update(sensor_inputs)
            dx = 1 if actions[0] > 0.5 else -1 if actions[0] < -0.5 else 0
            dy = 1 if actions[1] > 0.5 else -1 if actions[1] < -0.5 else 0
            #if len(actions) > 2 and actions[2] > 0.8: dx, dy = 0, 0
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
            print(f"Generation {self.generation}, stage {self.training_stage}, survivors: {len(survivors)}, {self.survival_rate*100:.0f}%")
            STAGE_THRESHOLDS = [0.9, 0.9, 0.9]  #Survival rates needed for each stage
            if (self.training_stage < len(STAGE_THRESHOLDS) and 
                self.survival_rate >= STAGE_THRESHOLDS[self.training_stage]):
                self.training_stage += 1
                print(f"Advanced to training stage {self.training_stage}")
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
            self.food_position = (random.randint(1, 99), random.randint(1, 99))
            self.generation += 1
            self.current_step = 0

    def get_survivors(self):
        #return self.filter_population(self.right_side_criteria)
        #return self.filter_population(self.center_x_criteria)
        #return self.filter_population(self.narrowing_criteria)
        return self.filter_population(self.food_criteria)

    def filter_population(self, criteria):
        return [ind for ind in self.population if criteria(ind)]

    def right_side_criteria(self, ind):
        return ind.x > 80

    def center_x_criteria(self, ind):
        return 40 < ind.x < 60

    def narrowing_criteria(self, ind):
        #Stage 0-2 use same thresholds as food_criteria
        stage_config = [
            (30, 70, 0, 100),   #Stage 0: Wide X range
            (40, 60, 20, 80),    #Stage 1: Narrower X, some Y
            (42, 58, 30, 70)]     #Stage 2: Tight X/Y
        if self.training_stage >= len(stage_config):
            return ind.x > 75  #Final stage
        x_min, x_max, y_min, y_max = stage_config[self.training_stage]
        return x_min < ind.x < x_max and y_min < ind.y < y_max

    def food_criteria(self, ind):
        thresholds = [850, 600, 450]
        current_threshold = thresholds[min(self.training_stage, len(thresholds)-1)]
        dx = ind.x - self.food_position[0]
        dy = ind.y - self.food_position[1]
        return dx*dx + dy*dy < current_threshold


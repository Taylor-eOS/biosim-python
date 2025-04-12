import random
from individual import Individual
from genome import NUM_SENSES, POPULATION_SIZE

class Simulation:
    def __init__(self, population_size=POPULATION_SIZE):
        self.population = []
        self.population_size = population_size
        self.generation = 0
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
            print(f"Individual at ({ind.x:.1f}, {ind.y:.1f}) moved by: ({dx}, {dy})")

    def run_generation(self, steps=5):
        print(f"Running generation {self.generation}")
        for _ in range(steps):
            self.step()
        for ind in self.population:
            print(ind)
        self.generation += 1

if __name__ == '__main__':
    import random
    #random.seed(42)
    sim = Simulation(population_size=POPULATION_SIZE)
    for _ in range(1):
        sim.run_generation(steps=1)


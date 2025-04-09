import random
from individual import Individual
from utils import NUM_SENSES, POPULATION_SIZE

class Simulation:
    def __init__(self, population_size=POPULATION_SIZE):
        self.population = []
        self.population_size = population_size
        self.generation = 0
        self.init_population()

    def init_population(self):
        self.population = []
        for _ in range(self.population_size):
            #Random initial positions; here x,y in [0,100] for example.
            ind = Individual(x=random.uniform(0, 100), y=random.uniform(0, 100))
            self.population.append(ind)

    def step(self):
        #Simulate one time step.
        #For now, each individual gets same dummy sensor input.
        sensor_inputs = [random.uniform(-1, 1) for _ in range(NUM_SENSES)]
        print("Sensor inputs:", sensor_inputs)
        for ind in self.population:
            actions = ind.update(sensor_inputs)
            #You would normally update the individual's state based on actions.
            #For example, adjust position or other properties here.
            #In this example, we just print the actions.
            print(f"Individual at ({ind.x:.1f},{ind.y:.1f}) did actions: {actions}")

    def run_generation(self, steps=5):
        print(f"Running generation {self.generation}")
        for _ in range(steps):
            self.step()
        #At the end of a generation you might rank individuals,
        #perform selection and reproduction to create the next generation.
        #For now, we simply print fitness values.
        for ind in self.population:
            print(ind)
        self.generation += 1

if __name__ == '__main__':
    import random
    random.seed(42)
    sim = Simulation(population_size=POPULATION_SIZE)
    #Run a few generations.
    for _ in range(2):
        sim.run_generation(steps=1)


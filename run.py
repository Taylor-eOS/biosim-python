import pygame
import math
from settings import log_file, SPEED, GENERATION_STEPS, VISUAL_MODE
from simulation import Simulation

def get_sensor_inputs(ind, population):
    sensors = [(ind.x - 50) / 50.0, (ind.y - 50) / 50.0]
    def calculate_closest_distance_and_dx():
        closest_distance = 1.0
        closest_dx = 0.0
        for other in population:
            if other != ind:
                dx = other.x - ind.x
                dy = other.y - ind.y
                distance = math.sqrt(dx * dx + dy * dy) / 50.0
                if distance < closest_distance:
                    closest_distance = distance
                    closest_dx = dx / 50.0
        return closest_distance, closest_dx
    closest_distance, closest_dx = calculate_closest_distance_and_dx()
    sensors.extend([1.0 - closest_distance, closest_dx])
    return sensors

def main():
    with open(log_file, "w"):
        pass
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    sim = Simulation()
    running = True
    generation_steps = GENERATION_STEPS
    visual_mode = VISUAL_MODE
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    visual_mode = not visual_mode
        if visual_mode:
            sim.update(generation_steps, sensor_callback=lambda ind: get_sensor_inputs(ind, sim.population))
            screen.fill((255, 255, 255))
            for ind in sim.population:
                pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 8)), 5)
            pygame.display.flip()
            clock.tick(SPEED)
        else:
            sim.update(generation_steps, sensor_callback=lambda ind: get_sensor_inputs(ind, sim.population))
            if sim.current_step == GENERATION_STEPS-1: #Just finished a generation, display one frame to see the result
                screen.fill((255, 255, 255))
                for ind in sim.population:
                    pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 6)), 5)
                pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()


import pygame
import math
from genome import log_file
from simulation import Simulation

def get_sensor_inputs(ind, population):
    sensors = [
        (ind.x - 50) / 50.0,
        (ind.y - 50) / 50.0]
    closest_distance = 1.0
    closest_dx = 0.0
    for other in population:
        if other != ind:
            dx = other.x - ind.x
            dy = other.y - ind.y
            distance = math.sqrt(dx*dx + dy*dy) / 50.0
            if distance < closest_distance:
                closest_distance = distance
                closest_dx = dx / 50.0
    sensors.extend([1.0 - closest_distance, closest_dx])
    return sensors

def main():
    with open(log_file, "w"):
        pass
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    sim = Simulation()
    running = True
    generation_steps = 80
    visual_mode = True  #set to False for max-speed CPU mode

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    visual_mode = not visual_mode
                    print("Visual mode:", visual_mode
        if visual_mode:
            sim.update(generation_steps, sensor_callback=lambda ind: get_sensor_inputs(ind, sim.population))
            screen.fill((255, 255, 255))
            for ind in sim.population:
                pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 6)), 5)
            pygame.display.flip()
            clock.tick(40)
        else:
            # Run entire generation instantly, no rendering
            sim.update(generation_steps, sensor_callback=lambda ind: get_sensor_inputs(ind, sim.population))
            if sim.current_step == 0:
                # just finished a generation, display one frame to see the result
                screen.fill((255, 255, 255))
                for ind in sim.population:
                    pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 6)), 5)
                pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()


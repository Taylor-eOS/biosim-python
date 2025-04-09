import pygame
import math
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
    print(f"closest_distance {closest_distance:.3f}, closest_dx {closest_dx:.3f}")
    return sensors

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    sim = Simulation()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        sim.step(lambda ind: get_sensor_inputs(ind, sim.population))
        screen.fill((255, 255, 255))
        for ind in sim.population:
            pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 6)), 5)
        pygame.display.flip()
        clock.tick(5)
    pygame.quit()

if __name__ == "__main__":
    main()


import pygame
import math
import settings
from simulation import Simulation

def get_sensor_inputs(ind, population, step):
    sensors = [
        (ind.x - 50) / 50.0, #Position, 1
        (ind.y - 50) / 50.0] #2
    sensors.extend([
        ind.last_dx, #Last movement, 3
        ind.last_dy, #4
        step/settings.GENERATION_STEPS]) #Step count, 5
    #Nearest neighbor detection
    closest_distance = 1.0
    angle_normalized = 0.0
    nearby_count = 0
    for other in population:
        if other != ind:
            dx = other.x - ind.x
            dy = other.y - ind.y
            distance = math.sqrt(dx*dx + dy*dy)
            # Count individuals within 10-unit range
            if distance <= 15:
                nearby_count += 1
            # Normalize distance for nearest neighbor calculation
            normalized_distance = distance / math.sqrt(98**2 + 98**2)
            if normalized_distance < closest_distance:
                closest_distance = normalized_distance
                if normalized_distance > 0.01: #Only calculate angle if meaningful distance
                    angle = math.atan2(dy, dx) #Returns radians
                    angle_normalized = angle / math.pi #Normalized to [-1, 1]
    sensors.extend([
        1.0 - closest_distance, #Distance to nearest neighbor (0=far, 1=touching), 6
        angle_normalized, #Direction to nearest neighbor, 7
        nearby_count / settings.POPULATION_SIZE]) #Normalized count of nearby individuals, 8
    if settings.WRITE_SENSOR_OUTPUT: print(sensors)
    return sensors

def main():
    if settings.WRITE_GENOME:
        with open(settings.log_file, "w"):
            pass
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    sim = Simulation()
    running = True
    generation_steps = settings.GENERATION_STEPS
    visual_mode = settings.VISUAL_MODE
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    visual_mode = not visual_mode
        if visual_mode:
            sim.update(generation_steps, sensor_callback=lambda ind: get_sensor_inputs(ind, sim.population, sim.current_step))
            screen.fill((255, 255, 255))
            for ind in sim.population:
                pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 8)), 5)
            pygame.display.flip()
            clock.tick(settings.SPEED)
        else:
            sim.update(generation_steps, sensor_callback=lambda ind: get_sensor_inputs(ind, sim.population, sim.current_step))
            if True:
                if sim.current_step == settings.GENERATION_STEPS-1:
                    screen.fill((255, 255, 255))
                    for ind in sim.population:
                        pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 8)), 5)
                    pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()


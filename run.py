import pygame
import math
import settings
from simulation import Simulation

def get_sensor_inputs(ind, population, step, food_position):
    sensors = [
        (ind.x - 50)/50.0,  #0: X position
        (ind.y - 50)/50.0]    #1: Y position
    #Food position relative to agent
    sensors.extend([
        (food_position[0] - ind.x)/100.0,  #2: Food X vector
        (food_position[1] - ind.y)/100.0])   #3: Food Y vector
    #Movement and timing
    sensors.extend([
        ind.last_dx,                     #4: Last X movement
        ind.last_dy,                     #5: Last Y movement
        step/settings.GENERATION_STEPS])  #6: Time
    #Social sensing
    closest_distance = 1.0
    angle_normalized = 0.0
    nearby_count = 0
    for other in population:
        if other != ind:
            dx = other.x - ind.x
            dy = other.y - ind.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance <= 15:
                nearby_count += 1
            normalized_distance = distance/math.sqrt(98**2 + 98**2)
            if normalized_distance < closest_distance:
                closest_distance = normalized_distance
                if normalized_distance > 0.01:
                    angle = math.atan2(dy, dx)
                    angle_normalized = angle/math.pi
    sensors.extend([
        1.0 - closest_distance,          #7: Proximity to nearest
        angle_normalized,                #8: Direction to nearest
        nearby_count/settings.POPULATION_SIZE])  #9: Crowding
    if settings.WRITE_SENSOR_OUTPUT: 
        print(sensors)
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
            sim.update(generation_steps, sensor_callback=lambda ind, population, step, food_position: get_sensor_inputs(ind, population, step, food_position))
            screen.fill((255, 255, 255))
            for ind in sim.population:
                pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 8)), 5)
            pygame.display.flip()
            clock.tick(settings.SPEED)
        else:
            sim.update(generation_steps, sensor_callback=lambda ind, population, step, food_position: get_sensor_inputs(ind, population, step, food_position))
            if True:
                if sim.current_step == settings.GENERATION_STEPS-1:
                    screen.fill((255, 255, 255))
                    for ind in sim.population:
                        pygame.draw.circle(screen, (0, 0, 0), (int(ind.x * 8), int(ind.y * 8)), 5)
                    pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()


import pygame
from simulation import Simulation

def get_normalized_position_inputs(ind):
    return [(ind.x - 50) / 50.0, (ind.y - 50) / 50.0]

def apply_discrete_movement(ind, actions):
    if actions[0] > 0.5:
        ind.x += 1
        print(f"move x+ ({ind.x:.1f},{ind.y:.1f})")
    elif actions[0] < -0.5:
        ind.x -= 1
        print(f"move x- ({ind.x:.1f},{ind.y:.1f})")
    if actions[1] > 0.5:
        ind.y += 1
        print(f"move y+ ({ind.x:.1f},{ind.y:.1f})")
    elif actions[1] < -0.5:
        ind.y -= 1
        print(f"move y- ({ind.x:.1f},{ind.y:.1f})")

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
        sim.step(get_sensor_inputs=get_normalized_position_inputs)
        screen.fill((255, 255, 255))
        for ind in sim.population:
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(ind.x * 8), int(ind.y * 6)), 5)
        pygame.display.flip()
        clock.tick(20)
    pygame.quit()

if __name__ == "__main__":
    main()


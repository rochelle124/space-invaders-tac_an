import pygame

from managers.game_manager import GameManager

pygame.init()
pygame.mixer.init() # Initialized sound mixer for background music

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders by Tac-an, Rochelle Cate T.")

game = GameManager(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
clock = pygame.time.Clock()   
running = True

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    game.update(events)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
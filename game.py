import pygame
from config import config, save_config


pygame.init() 

WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 50
flags = pygame.FULLSCREEN if config["fullscreen"] else 0
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
pygame.display.set_caption("Issekill")

def show_intro(screen):
    clock = pygame.time.Clock()
    black = pygame.Surface((WIDTH, HEIGHT))
    black.fill((0, 0, 0))

    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 11500: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        screen.blit(black, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def run_game(screen):
    from platformer import run_game as run_platformer
    run_platformer(screen)


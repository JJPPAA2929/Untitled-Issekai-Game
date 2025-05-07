import pygame
from config import config, save_config

def toggle_fullscreen():
    config["fullscreen"] = not config["fullscreen"]
    save_config()

def recreate_screen():
    from game import WIDTH, HEIGHT
    flags = pygame.FULLSCREEN if config["fullscreen"] else 0
    return pygame.display.set_mode((WIDTH, HEIGHT), flags)
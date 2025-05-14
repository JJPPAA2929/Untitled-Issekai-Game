import pygame
import sys
from game import screen
from menu import main_menu
from game import show_intro
pygame.mixer.init()
pygame.mixer.music.load("assets/music/Menu Theme.mp3")
pygame.mixer.music.play(-1) 

show_intro(screen)
main_menu()

pygame.quit()
sys.exit()
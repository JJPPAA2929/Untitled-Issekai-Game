import pygame
from config import config

hurt_sounds = [
    pygame.mixer.Sound("assets/audio/hurt1.mp3"),
    pygame.mixer.Sound("assets/audio/hurt2.mp3"),
    pygame.mixer.Sound("assets/audio/hurt3.mp3")
]

hit_sounds = [
    pygame.mixer.Sound("assets/audio/bloody hit4.mp3"),
    pygame.mixer.Sound("assets/audio/bloody hit3.mp3"),
    pygame.mixer.Sound("assets/audio/bloody hit2.mp3")
]

kill_sounds = [
    pygame.mixer.Sound("assets/audio/kill sound1.mp3"),
    pygame.mixer.Sound("assets/audio/kill sound2.mp3"),
    pygame.mixer.Sound("assets/audio/kill sound3.mp3"),
    pygame.mixer.Sound("assets/audio/kill sound4.mp3")
]

def apply_sfx_volume():
    volume = config["sound_volume"]
    for sound in hurt_sounds + hit_sounds + kill_sounds:
        sound.set_volume(volume)
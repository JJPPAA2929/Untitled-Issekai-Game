import pygame
from settings import recreate_screen
from config import save_config, config
from game import WIDTH, HEIGHT
from cutscene import play_cutscene
from platformer import run_game
from ui_settings import open_settings  # Импорт нового интерфейса

# Применение настроек экрана
screen_flags = pygame.FULLSCREEN if config.get("fullscreen", False) else 0
screen = pygame.display.set_mode((WIDTH, HEIGHT), screen_flags)

DARK_GRAY = (30, 30, 30)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)

class Button:
    def __init__(self, text, pos, callback, font):
        self.text = text
        self.pos = pos
        self.callback = callback
        self.font = font
        self.hovered = False
        self.update_surface()

    def update_surface(self):
        color = WHITE if self.hovered else GRAY
        self.text_surf = self.font.render(self.text, True, color)
        self.rect = self.text_surf.get_rect(center=self.pos)

    def draw(self, surface):
        surface.blit(self.text_surf, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            self.update_surface()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

def apply_volumes():
    pygame.mixer.music.set_volume(config.get("music_volume", 0.5))
    pygame.mixer.set_num_channels(16)
    for i in range(16):
        pygame.mixer.Channel(i).set_volume(config.get("sound_volume", 0.5))

def main_menu():
    apply_volumes()
    running = True
    font = pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 48)

    def start_game():
        pygame.mixer.music.stop()
        play_cutscene(screen)
        run_game(screen)

    buttons = [
        Button("PLAY", (WIDTH // 2, 450), start_game, font),
        Button("OPTIONS", (WIDTH // 2, 550), lambda: open_settings(screen), font),
        Button("EXIT", (WIDTH // 2, 650), lambda: (save_config(), pygame.quit()), font)
    ]

    while running:
        screen.fill(DARK_GRAY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_config()
                running = False
            for btn in buttons:
                btn.handle_event(event)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
import pygame
from settings import toggle_fullscreen, recreate_screen
from config import config, save_config
from audio import apply_sfx_volume

WIDTH, HEIGHT = 1280, 720

DARK_GRAY = (30, 30, 30)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
RED = (200, 50, 50)

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

class Slider:
    def __init__(self, x, y, width, value, callback):
        self.rect = pygame.Rect(x, y, width, 10)
        self.value = value
        self.callback = callback
        self.dragging = False

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        knob_x = self.rect.x + int(self.value * self.rect.width)
        pygame.draw.circle(surface, RED, (knob_x, self.rect.centery), 8)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            self.value = max(0.0, min(1.0, rel_x / self.rect.width))
            self.callback(self.value)

def open_settings(screen):
    running = True
    global_screen = screen
    font = pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 48)
    small_font = pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 36)

    def back_to_menu():
        save_config()
        nonlocal running
        running = False

    def toggle_and_update():
        toggle_fullscreen()
        recreate_screen()
        fullscreen_button.text = f"ПОЛНОЭКРАННЫЙ: {'ВКЛ' if config['fullscreen'] else 'ВЫКЛ'}"
        fullscreen_button.update_surface()

    def set_music_volume(vol):
        config["music_volume"] = round(vol, 2)
        pygame.mixer.music.set_volume(config["music_volume"])

    def set_sound_volume(vol):
        config["sound_volume"] = round(vol, 2)
        apply_sfx_volume()


    music_slider = Slider(WIDTH // 2 - 150, 320, 300, config["music_volume"], set_music_volume)
    sound_slider = Slider(WIDTH // 2 - 150, 380, 300, config["sound_volume"], set_sound_volume)


    fullscreen_button = Button(
        f"ПОЛНОЭКРАННЫЙ: {'ВКЛ' if config['fullscreen'] else 'ВЫКЛ'}",
        (WIDTH // 2, 450),
        toggle_and_update,
        small_font
    )

    back_button = Button("НАЗАД", (WIDTH // 2, 530), back_to_menu, small_font)

    buttons = [fullscreen_button, back_button]

    while running:
        screen.fill(DARK_GRAY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_config()
                pygame.quit()
                exit()
            for btn in buttons:
                btn.handle_event(event)
            music_slider.handle_event(event)
            sound_slider.handle_event(event)

        for btn in buttons:
            btn.draw(screen)

    
        music_label = small_font.render("МУЗЫКА", True, WHITE)
        screen.blit(music_label, music_label.get_rect(center=(WIDTH // 2, 290)))

        sound_label = small_font.render("ЗВУКИ", True, WHITE)
        screen.blit(sound_label, sound_label.get_rect(center=(WIDTH // 2, 350)))

        music_slider.draw(screen)
        sound_slider.draw(screen)
        music_percent = int(music_slider.value * 100)
        music_value_text = small_font.render(f"{music_percent}%", True, WHITE)
        screen.blit(music_value_text, (music_slider.rect.right + 10, music_slider.rect.y - 10))


        sound_percent = int(sound_slider.value * 100)
        sound_value_text = small_font.render(f"{sound_percent}%", True, WHITE)
        screen.blit(sound_value_text, (sound_slider.rect.right + 10, sound_slider.rect.y - 10))
        pygame.display.flip()
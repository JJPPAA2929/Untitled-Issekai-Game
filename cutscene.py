import pygame
from game import WIDTH, HEIGHT
import time

dialogue = [
    {
        "name": "...",
        "portrait": "npc.png",
        "text": "........"
    },
    {
        "name": "...",
        "portrait": "npc.png",
        "text": "Wake up."
    },
    {
        "name": "...",
        "portrait": "npc.png",
        "text": "Wake up."
    },
    {
        "name": "...",
        "portrait": "npc.png",
        "text": "You need to wake up."
    },
    {
        "name": "...",
        "portrait": "npc.png",
        "text": "Rise and shine."
    }
]
def draw_typing_text(surface, text, font, color, rect, speed=30):
    x, y = rect.topleft
    line = ''
    words = text.split(' ')
    lines = []
    for word in words:
        test_line = line + word + ' '
        if font.size(test_line)[0] < rect.width:
            line = test_line
        else:
            lines.append(line)
            line = word + ' '
    lines.append(line)


    for i, line in enumerate(lines):
        printed = ''
        for char in line:
            printed += char
            rendered = font.render(printed, True, color)
            text_line_rect = pygame.Rect(x, y + i * font.get_height(), rect.width, font.get_height())
            pygame.draw.rect(surface, (20, 20, 20), text_line_rect) 
            surface.blit(rendered, (x, y + i * font.get_height()))
            pygame.display.update(text_line_rect)
            pygame.time.delay(speed)


def load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        return pygame.Surface((64, 64))  # Пустышка если файла нет

def play_cutscene(screen):
    font = pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 32)
    name_font = pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 24)
   
   
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((255, 255, 255))
    for alpha in range(255, -1, -5):
        screen.fill((0, 0, 0))
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)


    current_index = 0
    clock = pygame.time.Clock()

    while current_index < len(dialogue):
        d = dialogue[current_index]
        portrait = load_image(f"assets/portraits/{d['portrait']}")
        waiting_for_input = False
        text_rect = pygame.Rect(150, HEIGHT - 110, WIDTH - 160, 90)


        screen.fill((0, 0, 0))
        dialogue_panel_rect = pygame.Rect(0, HEIGHT - 150, WIDTH, 150)
        pygame.draw.rect(screen, (20, 20, 20), dialogue_panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), dialogue_panel_rect, 2)

        # Отрисовка портрета внутри панели
        portrait = pygame.transform.scale(portrait, (100, 100))  # подгоняем под панель
        portrait_pos = (30, HEIGHT - 130)
        screen.blit(portrait, portrait_pos)

        # Отрисовка имени
        name_surf = name_font.render(d["name"], True, (255, 255, 255))
        screen.blit(name_surf, (150, HEIGHT - 130))

        # Подготовка прямоугольника для текста
        text_rect = pygame.Rect(150, HEIGHT - 100, WIDTH - 170, 80)

        pygame.display.update()

        draw_typing_text(screen, d["text"], font, (255, 255, 255), text_rect)


        pygame.draw.polygon(screen, (255, 255, 255),
                            [(WIDTH // 2 - 5, HEIGHT - 10), (WIDTH // 2 + 5, HEIGHT - 10), (WIDTH // 2, HEIGHT - 5)])
        pygame.display.flip()

        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting_for_input = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    waiting_for_input = False

            clock.tick(60)

        current_index += 1

    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((255, 255, 255))
    for alpha in range(0, 256, 5):  # шаг можно менять для скорости
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)
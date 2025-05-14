import pygame
from game import WIDTH, HEIGHT
from config import config
import pygame.mixer
# Оригинальный размер антагониста
ORIGINAL_SPRITE_SIZE = (3180, 5000)
CREEPY_MUSIC = "assets/audio/Darkness.mp3"
NORMAL_MUSIC = "assets/audio/Green Forest.mp3"


dialogue = [
    {"name": "...", "portrait": "npc.png", "text": "........"},
    {"name": "...", "portrait": "npc.png", "text": "Прокидайся."},
    {"name": "...", "portrait": "npc.png", "text": "Негайно."},
    {"name": "...", "portrait": "npc.png", "text": "Тобі треба вставати."},
    {"name": "...", "portrait": "npc.png", "text": "Прокинься."},
    {"name": "???", "portrait": "face_100.png", "text": "...", "sprite_state": "sleep"},
    {"name": "???", "portrait": "face_100.png", "text": "...", "sprite_state": "sleep"},
    {"name": "???", "portrait": "face_100.png", "text": "Це де я?", "sprite_state": "awake"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Де ліжко моє...", "sprite_state": "annoyed"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Треба знайти шлях до моєї хати.", "sprite_state": "awake"},
    {"name": "Труня", "portrait": "face_100.png", "text": "О, там хтось гуляє. Піду спитаю де я.", "sprite_state": "interested"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Привіт дядя, підскажіть де я зараз.", "sprite_state": "smile"},
    {"name": "???", "portrait": "enemy.png", "text": "ВБИТИ.", "enemy_speaks": True},
    {"name": "Труня", "portrait": "face_100.png", "text": "Який ти некультурний.", "sprite_state": "careless"}
]

def preload_resources():
    resources = {
        "fonts": {
            "main": pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 32),
            "name": pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 24)
        },
        "images": {
            "background": pygame.transform.scale(
                pygame.image.load("assets/images/cutscene1.jpg").convert(), (WIDTH, HEIGHT)),
            "antagonist": {},
            "enemy": None
        },
        "portraits": {}
    }

    scale_factor = HEIGHT / ORIGINAL_SPRITE_SIZE[1]
    scaled_size = (int(ORIGINAL_SPRITE_SIZE[0] * scale_factor), HEIGHT)

    sprite_states = {
        "sleep": "antagonist9.png",
        "awake": "antagonist1.png",
        "interested": "antagonist2.png",
        "smile": "antagonist3.png",
        "careless": "antagonist4.png",
        "annoyed": "antagonist5.png",
        "angry": "antagonist6.png",
        "hurt": "antagonist7.png",
        "enemy": "enemy.png"
    }

    for state, filename in sprite_states.items():
        img = pygame.image.load(f"assets/sprites/{filename}").convert_alpha()
        resources["images"]["antagonist"][state] = pygame.transform.scale(img, scaled_size)

    # Загрузка спрайта врага (того же размера)
    enemy_img = pygame.image.load("assets/sprites/enemy.png").convert_alpha()
    resources["images"]["enemy"] = pygame.transform.scale(enemy_img, scaled_size)

    for entry in dialogue:
        portrait = entry["portrait"]
        if portrait not in resources["portraits"]:
            if portrait == "enemy.png":
                img = pygame.image.load("assets/portraits/enemy.png").convert_alpha()
            else:
                img = pygame.image.load(f"assets/portraits/{portrait}").convert_alpha()
            resources["portraits"][portrait] = pygame.transform.scale(img, (100, 100))

    return resources

def play_music(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(config.get("music_volume", 0.5))
    pygame.mixer.music.play(-1)

def draw_dialogue(screen, resources, entry, sprite_state, antagonist_state, show_enemy):
    
    if entry["text"] != "Прокинься." and not antagonist_state:
        screen.fill((0, 0, 0))
    else:
        screen.blit(resources["images"]["background"], (0, 0))
        if antagonist_state:
            sprite = resources["images"]["antagonist"].get(antagonist_state)
            screen.blit(sprite, (50, HEIGHT - sprite.get_height()))
        if show_enemy:
            enemy = resources["images"]["enemy"]
            screen.blit(enemy, (WIDTH - enemy.get_width() - 50, HEIGHT - enemy.get_height()))

    # Текстовая панель всегда видна
    pygame.draw.rect(screen, (20, 20, 20), (0, HEIGHT - 150, WIDTH, 150))
    pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT - 150, WIDTH, 150), 2)

    portrait = resources["portraits"][entry["portrait"]]
    screen.blit(portrait, (30, HEIGHT - 130))

    name_surf = resources["fonts"]["name"].render(entry["name"], True, (255, 255, 255))
    screen.blit(name_surf, (150, HEIGHT - 130))

    text_rect = pygame.Rect(150, HEIGHT - 100, WIDTH - 170, 80)
    words = entry["text"].split(' ')
    lines = []
    line = ''
    for word in words:
        test = line + word + ' '
        if resources["fonts"]["main"].size(test)[0] < text_rect.width:
            line = test
        else:
            lines.append(line)
            line = word + ' '
    lines.append(line)

    for i, l in enumerate(lines):
        rendered = resources["fonts"]["main"].render(l, True, (255, 255, 255))
        screen.blit(rendered, (text_rect.x, text_rect.y + i * resources["fonts"]["main"].get_height()))

    pygame.draw.polygon(screen, (255, 255, 255),
                        [(WIDTH // 2 - 5, HEIGHT - 10), (WIDTH // 2 + 5, HEIGHT - 10), (WIDTH // 2, HEIGHT - 5)])
    pygame.display.flip()

def fade(screen, to_black=True):
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((0, 0, 0))
    alpha_range = range(0, 256, 5) if to_black else range(255, -1, -5)
    for alpha in alpha_range:
        surf.set_alpha(alpha)
        screen.blit(surf, (0, 0))
        pygame.display.update()
        pygame.time.delay(15)

def play_cutscene(screen):
    resources = preload_resources()
    clock = pygame.time.Clock()
    antagonist_state = None
    show_enemy = False

    pygame.mixer.init()
    play_music("assets/music/Darkness.mp3")

    fade(screen, to_black=False)

    for i, entry in enumerate(dialogue):
        if i == 5:
            play_music("assets/music/Green Forest.mp3")
        elif i == 12:
            pygame.mixer.music.stop()

        sprite_state = entry.get("sprite_state")
        if sprite_state:
            antagonist_state = sprite_state

        if entry.get("enemy_speaks", False):
            show_enemy = True

        draw_dialogue(screen, resources, entry, sprite_state, antagonist_state, show_enemy)

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    waiting = False
            clock.tick(60)

    fade(screen, to_black=True)
    screen.fill((0, 0, 0))
    pygame.display.flip()
    pygame.time.delay(1000)
    pygame.mixer.music.stop()
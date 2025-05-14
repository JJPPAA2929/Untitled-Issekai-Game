import pygame
from game import WIDTH, HEIGHT
from config import config
from menu import main_menu
ORIGINAL_SPRITE_SIZE = (3180, 5000)
DIALOGUE_MUSIC = "assets/music/Corrupted Knight.mp3"
ENDING_MUSIC = "assets/music/Trunya.mp3"
from game import show_intro
dialogue = [
    {"name": "Труня", "portrait": "face_100.png", "text": "От би додомцю... Наїмся як слідує.", "sprite_state": "annoyed"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Тільки зараз набью мордяку тому дідьку...", "sprite_state": "annoyed"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Де цей чобіт сталевий...", "sprite_state": "interested"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Обана.", "sprite_state": "knight", "show_knight": True},
    {"name": "Труня", "portrait": "face_100.png", "text": "То це - ти хуліган про якого говорять?", "sprite_state": "smile"},
]

def preload_resources():
    resources = {
        "fonts": {
            "main": pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 32),
            "name": pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 24),
            "big": pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 72)
        },
        "images": {
            "background": pygame.transform.scale(
                pygame.image.load("assets/images/Cathedral.jpg").convert(), (WIDTH, HEIGHT)),
            "characters": {}
        },
        "portraits": {}
    }

    scale_factor = HEIGHT / ORIGINAL_SPRITE_SIZE[1]
    scaled_size = (int(ORIGINAL_SPRITE_SIZE[0] * scale_factor), HEIGHT)

    sprite_states = {
        "awake": "antagonist1.png",
        "annoyed": "antagonist5.png",
        "interested": "antagonist2.png",
        "careless": "antagonist4.png",
        "smile": "antagonist3.png",
        "knight": "Knight.png"
    }

    for state, filename in sprite_states.items():
        img = pygame.image.load(f"assets/sprites/{filename}").convert_alpha()
        resources["images"]["characters"][state] = pygame.transform.scale(img, scaled_size)

    for entry in dialogue:
        portrait = entry["portrait"]
        if portrait not in resources["portraits"]:
            img = pygame.image.load(f"assets/portraits/{portrait}").convert_alpha()
            resources["portraits"][portrait] = pygame.transform.scale(img, (100, 100))

    return resources

def draw_dialogue(screen, resources, entry, trunya_sprite, knight_sprite):
    screen.blit(resources["images"]["background"], (0, 0))

    if trunya_sprite:
        screen.blit(trunya_sprite, (50, HEIGHT - trunya_sprite.get_height()))
    if knight_sprite:
        screen.blit(knight_sprite, (WIDTH - knight_sprite.get_width() - 50, HEIGHT - knight_sprite.get_height()))

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

def show_the_end(screen, font):
    clock = pygame.time.Clock()
    text = font.render("ПРОДОВЖЕННЯ СЛІДУЄ", True, (255, 255, 255))
    alpha = 0
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill((0, 0, 0))

    pygame.mixer.music.load(ENDING_MUSIC)
    pygame.mixer.music.set_volume(config.get("music_volume", 0.5))
    pygame.mixer.music.play(-1)

    while alpha < 255:
        surface.set_alpha(alpha)
        screen.blit(surface, (0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(50)
        alpha += 5
        clock.tick(60)

    pygame.time.delay(3000)

def play_cutscene3(screen):
    pygame.mixer.init()
    pygame.mixer.music.load(DIALOGUE_MUSIC)
    pygame.mixer.music.set_volume(config.get("music_volume", 0.5))
    pygame.mixer.music.play(-1)

    resources = preload_resources()
    clock = pygame.time.Clock()
    trunya_sprite = resources["images"]["characters"]["annoyed"]
    knight_sprite = None

    screen.fill((0, 0, 0))
    pygame.display.flip()
    fade(screen, to_black=False)

    for entry in dialogue:
        if "sprite_state" in entry:
            trunya_sprite = resources["images"]["characters"].get(entry["sprite_state"])

        if entry.get("show_knight"):
            knight_sprite = resources["images"]["characters"].get("knight")

        draw_dialogue(screen, resources, entry, trunya_sprite, knight_sprite)

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    waiting = False
            clock.tick(60)

    fade(screen, to_black=True)
    pygame.mixer.music.stop()
    screen.fill((0, 0, 0))
    pygame.display.flip()
    pygame.time.delay(1000)

    show_the_end(screen, resources["fonts"]["big"])
    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/Menu Theme.mp3")
    pygame.mixer.music.play(-1) 
    show_intro
    main_menu()
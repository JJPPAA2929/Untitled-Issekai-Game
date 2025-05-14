import pygame
from game import WIDTH, HEIGHT
from config import config

ORIGINAL_SPRITE_SIZE = (3180, 5000)
MUSIC_PATH = "assets/music/Trunya.mp3"

dialogue = [
    {"name": "Труня", "portrait": "face_100.png", "text": "Хай мама приїде... Хай мама прийде-е-е...", "sprite_state": "annoyed"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Хай мама мене додому забере.", "sprite_state": "annoyed"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Там шось в кустах... Баба-а-а-ай.", "sprite_state": "interested"},
    {"name": "Труня", "portrait": "face_100.png", "text": "О. Шановна, добрий день", "sprite_state": "dorothy1", "show_dorothy": True},
    {"name": "Труня", "portrait": "face_100.png", "text": "Прошу не бийте, скажіть куди я загуляв.", "sprite_state": "careless"},
    {"name": "???", "portrait": "dorothy.png", "text": "Не бійся, бити не буду, зразу отак і з'їм.", "sprite_state": "dorothy2"},
    {"name": "Труня", "portrait": "face_100.png", "text": "А рот не порветься?", "sprite_state": "smile"},
    {"name": "???", "portrait": "dorothy.png", "text": "Стули пельку, хлопчик", "sprite_state": "dorothy1"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Та ладно тобі. Хто тебе так?", "sprite_state": "awake"},
    {"name": "???", "portrait": "dorothy.png", "text": "Хахах~, ти шо, з печери виліз, чи як? Як Груг блін", "sprite_state": "dorothy2"},
    {"name": "???", "portrait": "dorothy.png", "text": "В Королівстві всі з глузду поз'їзжали, б'ють, убивають...", "sprite_state": "dorothy3"},
    {"name": "???", "portrait": "dorothy.png", "text": "А заради чого - не знаю.", "sprite_state": "dorothy3"},
    {"name": "???", "portrait": "dorothy.png", "text": "От мене командир гвардії так і помутозив.", "sprite_state": "dorothy2"},
    {"name": "???", "portrait": "dorothy.png", "text": "Та і допомогти нікому, ніхто відповідати насиллям не вміє...", "sprite_state": "dorothy2"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Ааа, поняв. Ну я пішов тоді.", "sprite_state": "careless"},
    {"name": "???", "portrait": "dorothy.png", "text": "Та ну ти йолоп зовсім? ", "sprite_state": "dorothy1"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Та ну я хатку свою шукаю, додому хочу.", "sprite_state": "annoyed"},
    {"name": "Труня", "portrait": "face_100.png", "text": "А тут серед ліса прокинувся, і як поналітали!", "sprite_state": "interested"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Так що, пані, нічим допомогти не зможу", "sprite_state": "awake"},
    {"name": "???", "portrait": "dorothy.png", "text": "Якщо підеш наб'єш мордяки в королівстві...", "sprite_state": "dorothy3"},
    {"name": "???", "portrait": "dorothy.png", "text": "То я піду і погуляю з тобою~", "sprite_state": "dorothy4"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Доречі, де то королівство?", "sprite_state": "awake"},
    {"name": "???", "portrait": "dorothy.png", "text": "Ось там, по тропинці ідеш і його найдеш", "sprite_state": "dorothy4"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Поняв. Ну я пішов тоді.", "sprite_state": "awake"},
    {"name": "Труня", "portrait": "face_100.png", "text": "Бай-бай, дівка якої ім'я не знаю.", "sprite_state": "smile"},
    {"name": "???", "portrait": "dorothy.png", "text": "Бувай, бувай...", "sprite_state": "dorothy2", "hide_trunya": True},
    {"name": "???", "portrait": "dorothy.png", "text": "Якщо що, ховати я тебе не буду.", "sprite_state": "dorothy3"}
]

def preload_resources():
    resources = {
        "fonts": {
            "main": pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 32),
            "name": pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 24)
        },
        "images": {
            "background": pygame.transform.scale(
                pygame.image.load("assets/images/grim-forest.jpg").convert(), (WIDTH, HEIGHT)),
            "characters": {}
        },
        "portraits": {}
    }

    scale_factor = HEIGHT / ORIGINAL_SPRITE_SIZE[1]
    scaled_size = (int(ORIGINAL_SPRITE_SIZE[0] * scale_factor), HEIGHT)

    sprite_states = {
        # Труня
        "awake": "antagonist1.png",
        "annoyed": "antagonist5.png",
        "interested": "antagonist2.png",
        "careless": "antagonist4.png",
        "smile": "antagonist3.png",
        # Дороти
        "dorothy1": "dorothy1.png",
        "dorothy2": "dorothy2.png",
        "dorothy3": "dorothy3.png",
        "dorothy4": "dorothy4.png"
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

def draw_dialogue(screen, resources, entry, trunya_sprite, dorothy_sprite):
    screen.blit(resources["images"]["background"], (0, 0))

    if trunya_sprite:
        screen.blit(trunya_sprite, (50, HEIGHT - trunya_sprite.get_height()))
    if dorothy_sprite:
        screen.blit(dorothy_sprite, (WIDTH - dorothy_sprite.get_width() - 50, HEIGHT - dorothy_sprite.get_height()))

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

def play_cutscene2(screen):
    pygame.mixer.init()
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.set_volume(config.get("music_volume", 0.5))
    pygame.mixer.music.play(-1)

    resources = preload_resources()
    clock = pygame.time.Clock()
    trunya_sprite = resources["images"]["characters"]["annoyed"]  # стартовое лицо
    dorothy_sprite = None

    screen.fill((0, 0, 0))
    pygame.display.flip()
    fade(screen, to_black=False)

    for entry in dialogue:
        if "hide_trunya" in entry and entry["hide_trunya"]:
            trunya_sprite = None
        elif "sprite_state" in entry and "dorothy" not in entry["sprite_state"]:
            trunya_sprite = resources["images"]["characters"].get(entry["sprite_state"])

        if entry.get("show_dorothy"):
            dorothy_sprite = resources["images"]["characters"].get(entry["sprite_state"])
        elif "sprite_state" in entry and "dorothy" in entry["sprite_state"]:
            dorothy_sprite = resources["images"]["characters"].get(entry["sprite_state"])

        draw_dialogue(screen, resources, entry, trunya_sprite, dorothy_sprite)

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
import pygame
from game import TILE_SIZE
from audio import apply_sfx_volume

heal_image = pygame.transform.scale(
    pygame.image.load("assets/textures/heal.png").convert_alpha(), (64, 64)
)
boost_image = pygame.transform.scale(
    pygame.image.load("assets/textures/boost.png").convert_alpha(), (64, 64)
)

class Item:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def apply(self, player):
        pass

class HealItem(Item):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, player):
        player.health = min(player.max_health, player.health + 30)
        #apply_sfx_volume("heal.wav")

class BoostItem(Item):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, player):
        player.boost_active = True
        player.boost_end_time = pygame.time.get_ticks() + 15000
        #apply_sfx_volume("boost.wav")
import pygame
import random
from audio import apply_sfx_volume
import pygame
from game import TILE_SIZE

heal_image = pygame.image.load("assets/textures/heal.jpg").convert_alpha()
boost_image = pygame.image.load("assets/textures/boost.jpg").convert_alpha()
class Item:
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.image = image

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def apply(self, player):
        pass

class HealItem(Item):
    def __init__(self, x, y):
        super().__init__(x, y, heal_image)

    def apply(self, player):
        player.health = min(player.max_health, player.health + 30)


class BoostItem(Item):
    def __init__(self, x, y):
        super().__init__(x, y, boost_image)

    def apply(self, player):
        player.boost_active = True
        player.boost_end_time = pygame.time.get_ticks() + 15000  # 15 секунд

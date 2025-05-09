import pygame
from items import HealItem, BoostItem, heal_image, boost_image

TILE_SIZE = 64

# Загрузка текстур
ground_img = pygame.transform.scale(pygame.image.load("assets/textures/ground.png").convert_alpha(), (64, 64))
flying_ground_img = pygame.transform.scale(pygame.image.load("assets/textures/flying-ground.png").convert_alpha(), (64, 32))
dirt_img = pygame.transform.scale(pygame.image.load("assets/textures/dirt.png").convert_alpha(), (64, 64))
tree_img = pygame.transform.scale(pygame.image.load("assets/textures/tree.png").convert_alpha(), (192, 256))
house_img = pygame.transform.scale(pygame.image.load("assets/textures/house.png").convert_alpha(), (192, 256))

class EnemySpawn:
    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.symbol = symbol

class GameMap:
    def __init__(self, filename, heal_image, boost_image):
        self.platforms = []
        self.player_spawn = None
        self.enemy_spawns = []
        self.items = []
        self.decorations = []  # Объекты, сквозь которые можно проходить

        with open(filename, 'r') as file:
            data = file.readlines()

        for row_index, row in enumerate(data):
            for col_index, tile in enumerate(row.strip()):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if tile == "G":
                    self.platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "P":
                    self.player_spawn = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                elif tile in ("M", "R"):
                    self.enemy_spawns.append(EnemySpawn(x, y, tile))
                elif tile == "H":
                    self.items.append(HealItem(x + TILE_SIZE // 4, y + TILE_SIZE // 24, heal_image))
                elif tile == "B":
                    self.items.append(BoostItem(x + TILE_SIZE // 4, y + TILE_SIZE // 24, boost_image))
                elif tile == "F":
                    self.decorations.append(("flying", x, y))
                    self.platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE // 2))
                elif tile == "D":
                    self.decorations.append(("dirt", x, y))
                elif tile == "T":
                    self.decorations.append(("tree", x, y))
                elif tile == "S":  # Дом
                    self.decorations.append(("house", x, y))

    def get_player_spawn(self):
        return self.player_spawn

    def get_enemy_spawns(self):
        return self.enemy_spawns

    def get_items(self):
        return self.items

    def draw(self, surface, camera_x):
        # Рисуем платформы (G)
        for platform in self.platforms:
            surface.blit(ground_img, (platform.x - camera_x, platform.y))

        for kind, x, y in self.decorations:
            if kind == "flying":
                surface.blit(flying_ground_img, (x - camera_x, y))
            elif kind == "dirt":
                surface.blit(dirt_img, (x - camera_x, y))
            elif kind == "tree":
                surface.blit(tree_img, (x - camera_x - 64, y - 192))  # центрируем по 3 блокам, поднимаем на 3 блока
            elif kind == "house":
                surface.blit(house_img, (x - camera_x - 64, y - 192)) 
import pygame
from items import HealItem, BoostItem, heal_image, boost_image

TILE_SIZE = 64

ground_img = pygame.transform.scale(pygame.image.load("assets/textures/ground.png").convert_alpha(), (64, 64))
flying_ground_img = pygame.transform.scale(pygame.image.load("assets/textures/flying-ground.png").convert_alpha(), (64, 32))
dirt_img = pygame.transform.scale(pygame.image.load("assets/textures/dirt.png").convert_alpha(), (64, 64))
tree_img = pygame.transform.scale(pygame.image.load("assets/textures/tree.png").convert_alpha(), (192, 256))
house_img = pygame.transform.scale(pygame.image.load("assets/textures/house.png").convert_alpha(), (192, 256))
background_img = pygame.transform.scale(pygame.image.load("assets/images/level1bg.jpg").convert(), (1280, 720))
spike_img = pygame.transform.scale(pygame.image.load("assets/textures/spikes.png").convert_alpha(), (64, 64))
stone_img = pygame.transform.scale(pygame.image.load("assets/textures/stone.png").convert_alpha(), (64, 64))
half_stone_img = pygame.transform.scale(pygame.image.load("assets/textures/stone.png").convert_alpha(), (64, 32))
door_img = pygame.transform.scale(pygame.image.load("assets/textures/door.png").convert_alpha(), (64, 64))

class EnemySpawn:
    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.symbol = symbol

class GameMap:
    def __init__(self, filename, heal_image, boost_image):
        self.doors = []
        self.stones = []
        self.half_stones = []
        self.spikes = []
        self.ground_platforms = []
        self.flying_platforms = []
        self.player_spawn = None
        self.enemy_spawns = []
        self.barriers = []
        self.items = []
        self.decorations = []  # Объекты, сквозь которые можно проходить
        self.barrier = pygame.Rect(-TILE_SIZE, 0, TILE_SIZE, 10000)
        self.ground_platforms.append(self.barrier)
        self.right_barrier = pygame.Rect(-TILE_SIZE, 0, TILE_SIZE, 10000)
        self.ground_platforms.append(self.right_barrier)
        with open(filename, 'r') as file:
            data = file.readlines()

        for row_index, row in enumerate(data):
            for col_index, tile in enumerate(row.strip()):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if tile == "G":
                    self.ground_platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "P":
                    self.player_spawn = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                elif tile in ("M", "R"):
                    self.enemy_spawns.append(EnemySpawn(x, y, tile))
                elif tile == "H":
                    self.items.append(HealItem(x + TILE_SIZE // 4, y + TILE_SIZE // 24, heal_image))
                elif tile == "B":
                    self.items.append(BoostItem(x + TILE_SIZE // 4, y + TILE_SIZE // 24, boost_image))
                elif tile == "F":
                    self.flying_platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE // 2))
                    self.decorations.append(("flying", x, y))
                elif tile == "X":
                    self.barriers.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))    
                elif tile == "D":
                    self.decorations.append(("dirt", x, y))
                elif tile == "T":
                    self.decorations.append(("tree", x, y))
                elif tile == "S":  
                    self.decorations.append(("house", x, y))
                elif tile == "L":  
                    self.spikes.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "Z":  
                    self.doors.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "Y":  
                    self.stones.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                    self.ground_platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "s":  
                    self.half_stones.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE // 2))
                    self.ground_platforms.append(pygame.Rect(x, y + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE // 2))

    def get_player_spawn(self):
        return self.player_spawn

    def get_enemy_spawns(self):
        return self.enemy_spawns

    def get_items(self):
        return self.items

    def draw(self, surface, camera_x):
        for platform in self.ground_platforms:
            surface.blit(ground_img, (platform.x - camera_x, platform.y))

        for platform in self.flying_platforms:
            surface.blit(flying_ground_img, (platform.x - camera_x, platform.y))

        for kind, x, y in self.decorations:
            if kind == "flying":
                surface.blit(flying_ground_img, (x - camera_x, y))
            elif kind == "dirt":
                surface.blit(dirt_img, (x - camera_x, y))
            elif kind == "tree":
                surface.blit(tree_img, (x - camera_x - 64, y - 192))
            elif kind == "house":
                surface.blit(house_img, (x - camera_x - 64, y - 192))

        for spike in self.spikes:
            surface.blit(spike_img, (spike.x - camera_x, spike.y))

        for item in self.items:
            item.draw(surface, camera_x)
        for stone in self.stones:
            surface.blit(stone_img, (stone.x - camera_x, stone.y))
        for half in self.half_stones:
            surface.blit(half_stone_img, (half.x - camera_x, half.y))
        for door in self.doors:
            surface.blit(door_img, (door.x - camera_x, door.y))
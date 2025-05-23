import pygame

TILE_SIZE = 64

class EnemySpawn:
    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.symbol = symbol

class GameMap:
    def __init__(self, filename):
        self.platforms = []
        self.player_spawn = None
        self.enemy_spawns = []

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

    def get_player_spawn(self):
        return self.player_spawn

    def get_enemy_spawns(self):
        return self.enemy_spawns

    def draw(self, surface, camera_x):
        for platform in self.platforms:
            pygame.draw.rect(surface, (0, 200, 0), 
                             (platform.x - camera_x, platform.y, 
                              platform.width, platform.height))


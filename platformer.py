import pygame
import random
import os
import math
from game import WIDTH, HEIGHT, screen
from map import GameMap
from ui_settings import open_settings, config
from audio import hurt_sounds, hit_sounds, kill_sounds, apply_sfx_volume
pygame.mixer.init()


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 80)
        self.color = (255, 0, 0)
        self.vel_y = 0
        self.jump = False
        self.on_ground = False
        self.health = 100
        self.max_health = 100
        self.attack_cooldown = 0
        self.facing_right = True
        self.attacking = False
        self.attack_frame = 0

    def take_damage(self, amount):
        self.health -= amount
        random.choice(hurt_sounds).play()

    def update(self, keys, enemies, game_map):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -5
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            dx = 5
            self.facing_right = True

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False

        if keys[pygame.K_f] and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_frame = 10
            self.attack_cooldown = 20
            self.attack(enemies)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.attacking:
            self.attack_frame -= 1
            if self.attack_frame <= 0:
                self.attacking = False

        self.vel_y += 0.5
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += dx
        for platform in game_map.platforms:
            if self.rect.colliderect(platform):
                if dx > 0:
                    self.rect.right = platform.left
                elif dx < 0:
                    self.rect.left = platform.right

        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if dx > 0:
                    self.rect.right = enemy.rect.left
                elif dx < 0:
                    self.rect.left = enemy.rect.right

        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in game_map.platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.bottom
                    self.vel_y = 0

    def attack(self, enemies):
        attack_rect = pygame.Rect(0, 0, 70, 60)
        if self.facing_right:
            attack_rect.midleft = self.rect.midright
        else:
            attack_rect.midright = self.rect.midleft

        for enemy in enemies:
            if attack_rect.colliderect(enemy.rect):
                enemy.take_damage(10)
                random.choice(hit_sounds).play()

    def draw(self, surface, camera_x):
        pygame.draw.rect(surface, self.color, 
                        (self.rect.x - camera_x, self.rect.y, 
                         self.rect.width, self.rect.height))

        if self.attacking:
            attack_rect = pygame.Rect(0, 0, 70, 60)
            if self.facing_right:
                attack_rect.midleft = (self.rect.midright[0] - camera_x, self.rect.midright[1])
            else:
                attack_rect.midright = (self.rect.midleft[0] - camera_x, self.rect.midleft[1])
            pygame.draw.rect(surface, (255, 255, 0), attack_rect, 2)

class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 10, 5)
        self.direction = direction
        self.speed = 7

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, surface, camera_x):
        pygame.draw.rect(surface, (255, 255, 0), 
                         (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))

    def off_screen(self):
        return (self.rect.x < 0 or self.rect.x > WIDTH or
                self.rect.y < 0 or self.rect.y > HEIGHT)

class Enemy:
    def __init__(self, x, y, enemy_type="melee"):
        self.rect = pygame.Rect(x, y, 50, 80)
        self.color = (0, 0, 255) if enemy_type == "melee" else (255, 0, 255)
        self.type = enemy_type
        self.health = 50
        self.attack_cooldown = 0
        self.direction = -1
        self.speed = 2
        self.vel_y = 0
        self.on_ground = False
        self.bullets = []

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def update(self, player, game_map):
        if self.health <= 0:
            return

        self.vel_y += 0.5
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in game_map.platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.bottom
                    self.vel_y = 0

        if self.type == "melee":
            if self.rect.x < player.rect.x:
                self.direction = 1
            else:
                self.direction = -1
            self.rect.x += self.direction * self.speed

            for platform in game_map.platforms:
                if self.rect.colliderect(platform):
                    if self.direction > 0:
                        self.rect.right = platform.left
                    else:
                        self.rect.left = platform.right

            if self.attack_cooldown <= 0 and self.rect.colliderect(player.rect):
                player.take_damage(10)
                self.attack_cooldown = 60

        elif self.type == "ranged":
            if self.attack_cooldown <= 0:
                self.shoot(player)
                self.attack_cooldown = 90

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.colliderect(player.rect):
                player.take_damage(5)
                self.bullets.remove(bullet)
            elif bullet.off_screen():
                self.bullets.remove(bullet)

    def shoot(self, player):
        direction = pygame.math.Vector2(player.rect.centerx - self.rect.centerx,
                                        player.rect.centery - self.rect.centery)
        direction = direction.normalize()
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
        self.bullets.append(bullet)

    def draw(self, surface, camera_x):
        pygame.draw.rect(surface, self.color, 
                         (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))
        for bullet in self.bullets:
            bullet.draw(surface, camera_x)

class UI:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 100, 100), (20, 20, 100, 100))
        health_width = 300 * (self.player.health / self.player.max_health)
        pygame.draw.rect(surface, (255, 0, 0), (130, 50, 300, 30))
        pygame.draw.rect(surface, (0, 255, 0), (130, 50, health_width, 30))
        pygame.draw.rect(surface, (255, 255, 255), (130, 50, 300, 30), 2)

def run_game(screen):
    clock = pygame.time.Clock()
    game_map = GameMap("level1.map")
    player = Player(*game_map.get_player_spawn().topleft)
    ui = UI(player)

    enemies = []
    for spawn in game_map.get_enemy_spawns():
        enemy_type = "melee" if spawn.symbol == "M" else "ranged"
        enemies.append(Enemy(spawn.x, spawn.y, enemy_type))

    paused = False
    font = pygame.font.Font(None, 48)
    pause_options = ["Продолжить", "Настройки", "Выход"]
    selected_option = 0

    camera_x = 0
    running = True

    while running:
        screen.fill((100, 100, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                elif paused:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(pause_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(pause_options)
                    elif event.key == pygame.K_RETURN:
                        if pause_options[selected_option] == "Продолжить":
                            paused = False
                        elif pause_options[selected_option] == "Настройки":
                            open_settings(screen)
                        elif pause_options[selected_option] == "Выход":
                            pygame.quit()
                            exit()

        keys = pygame.key.get_pressed()
        if not paused:
            player.update(keys, enemies, game_map)
            for i, enemy in enumerate(enemies[:]):
                enemy.update(player, game_map)
                for j in range(i + 1, len(enemies)):
                    other = enemies[j]
                    if enemy.rect.colliderect(other.rect):
                        if enemy.rect.centerx < other.rect.centerx:
                            enemy.rect.right = other.rect.left
                        else:
                            enemy.rect.left = other.rect.right
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    random.choice(kill_sounds).play()

        camera_x = player.rect.x - WIDTH // 3
        game_map.draw(screen, camera_x)

        for enemy in enemies:
            enemy.draw(screen, camera_x)

        player.draw(screen, camera_x)
        ui.draw(screen)

        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            for i, option in enumerate(pause_options):
                color = (255, 255, 0) if i == selected_option else (255, 255, 255)
                text = font.render(option, True, color)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

        pygame.display.flip()
        clock.tick(60)

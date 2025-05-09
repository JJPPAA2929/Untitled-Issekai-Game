import pygame
import random
import os
import math
from game import WIDTH, HEIGHT, screen
from map import GameMap
from ui_settings import open_settings, config
from audio import hurt_sounds, hit_sounds, kill_sounds, apply_sfx_volume
from items import HealItem, BoostItem
import items
from blood import BloodParticle, BloodStain

blood_group = pygame.sprite.Group()

blood_image = pygame.image.load("assets/blood/blood-splash1.png").convert_alpha()
pygame.mixer.init()

blood_stain_images = [pygame.image.load(os.path.join("assets", "blood", f"blood-stain{i}.png")).convert_alpha()
    for i in range(1, 3)
]
blood_splashes = [pygame.image.load(os.path.join("assets", "blood", f"blood-splash{i}.png")) for i in range(1, 6)]
blood_drops = [pygame.image.load(os.path.join("assets", "blood", f"blood-drop{i}.png")) for i in range(1, 3)]


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y + 16, 50, 95)
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
        self.boost_active = False
        self.boost_end_time = 0

        # Загрузка спрайтов
        self.idle_frames = [pygame.transform.scale(pygame.image.load("assets/sprites/antagonist-idle.png").convert_alpha(), (75, 96))]
        self.walk_frames = [pygame.transform.scale(pygame.image.load(f"assets/sprites/antagonist-walking{i}.png").convert_alpha(), (75, 96)) for i in range(1, 3)]
        self.attack_left_frames = [pygame.transform.scale(pygame.image.load(f"assets/sprites/antagonist-attackingleft{i}.png").convert_alpha(), (75, 96)) for i in range(1, 5)]
        self.attack_right_frames = [pygame.transform.scale(pygame.image.load(f"assets/sprites/antagonist-attackingright{i}.png").convert_alpha(), (75, 96)) for i in range(1, 5)]

        self.idle_frame = self.idle_frames[0]
        self.walk_index = 0
        self.walk_timer = 0
        self.frame_index = 0
        self.frame_timer = 0
        self.animation_speed = 0.5
        self.attack_timer = 0
        self.attack_frames = []
        self.attack_frame_index = 0
        self.current_attack_frames = []

        self.image = self.idle_frame
        self.mask = pygame.mask.from_surface(self.image)


    def take_damage(self, amount):
        self.health -= amount
        random.choice(hurt_sounds).play()

    def update(self, keys, enemies, game_map, blood_particles, blood_image):
        speed = 8 if self.boost_active else 5
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            dx = speed
            self.facing_right = True
        if dx != 0:
            self.walk_timer += 1
            if self.walk_timer >= 5:  
                self.walk_index = (self.walk_index + 1) % len(self.walk_frames)
                self.walk_timer = 0
        else:
            self.walk_index = 0
            self.walk_timer = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False

        if keys[pygame.K_f] and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_frame = 10
            self.attack_cooldown = 10
            self.attack(enemies, blood_particles, blood_image)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.frame_timer += 1

        if self.attacking:
            self.attack_timer += self.animation_speed
            if self.attack_timer >= 1:
                self.attack_frame_index += 1
                self.attack_timer = 0
            if self.attack_frame_index >= len(self.current_attack_frames):
                self.attacking = False
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                if self.frame_timer >= self.animation_speed:
                    self.frame_timer = 0
                    self.frame_index = (self.frame_index + 1) % len(self.walk_frames)
            else:
                self.frame_index = 0
                self.frame_timer = 0

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
        if self.boost_active and pygame.time.get_ticks() > self.boost_end_time:
            self.boost_active = False
        self.frame_timer += 1

        anim_speed = 5
        if self.attacking:
            attack_frames = random.choice([self.attack_left_frames, self.attack_right_frames]) if self.frame_timer == 1 else self.current_attack_frames
            self.current_attack_frames = attack_frames
            self.image = attack_frames[self.frame_timer // anim_speed % len(attack_frames)]
        elif dx != 0:
            self.image = self.walk_frames[self.frame_timer // anim_speed % len(self.walk_frames)]
        else:
            self.image = self.idle_frames[0]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)



    def attack(self, enemies, blood_particles, blood_image):
        self.attacking = True
        self.attack_timer = 0
        self.attack_frame_index = 0

    
        if random.choice([True, False]):
            self.current_attack_frames = self.attack_left_frames
        else:
            self.current_attack_frames = self.attack_right_frames


        attack_rect = pygame.Rect(0, 0, 70, 60)
        if self.facing_right:
            attack_rect.topleft = (self.rect.right - 10, self.rect.top + 30)
        else:
            attack_rect.topright = (self.rect.left + 10, self.rect.top + 30)

        for enemy in enemies:
            if attack_rect.colliderect(enemy.rect):
                damage = 20 if self.boost_active else 10
                enemy.take_damage(damage)
                for _ in range(2):
                    particle = BloodParticle(enemy.rect.centerx, enemy.rect.centery, random.choice(blood_splashes))
                    blood_particles.append(particle)

                random.choice(hit_sounds).play()

    def draw(self, surface, camera_x):
        if self.attacking and self.current_attack_frames:
            frame = self.current_attack_frames[self.attack_frame_index % len(self.current_attack_frames)]
        elif self.rect.x != 0 and len(self.walk_frames) > 0:
            frame = self.walk_frames[self.walk_index % len(self.walk_frames)]
        else:
            frame = self.idle_frame

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        x = self.rect.x - camera_x
        y = self.rect.y
        surface.blit(frame, (x, y))
        self.mask = pygame.mask.from_surface(frame)

        attack_rect = pygame.Rect(0, 0, 40, 30)
        if self.facing_right:
            attack_rect.midleft = (self.rect.right, self.rect.centery - 10)
        else:
            attack_rect.midright = (self.rect.left, self.rect.centery - 10)


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
        self.boost_icon = pygame.transform.scale(
            pygame.image.load("assets/textures/boost.png").convert_alpha(), (32, 32)
        )

        self.face_images = {
            "100": pygame.image.load("assets/portraits/face_100.png").convert_alpha(),
            "75": pygame.image.load("assets/portraits/face_75.png").convert_alpha(),
            "50": pygame.image.load("assets/portraits/face_50.png").convert_alpha(),
            "25": pygame.image.load("assets/portraits/face_25.png").convert_alpha(),
            "dead": pygame.image.load("assets/portraits/face_dead.png").convert_alpha(),
        }

    def get_face_image(self):
        hp = self.player.health
        if hp <= 0:
            return self.face_images["dead"]
        elif hp <= 25:
            return self.face_images["25"]
        elif hp <= 50:
            return self.face_images["50"]
        elif hp <= 75:
            return self.face_images["75"]
        else:
            return self.face_images["100"]

    def draw(self, surface):
        # Портрет
        face_img = self.get_face_image()
        face_img = pygame.transform.scale(face_img, (128, 110))  # Масштаб 100x100
        surface.blit(face_img, (5, 5))

        # Полоса HP
        health_width = 300 * (self.player.health / self.player.max_health)
        pygame.draw.rect(surface, (255, 0, 0), (130, 50, 300, 30))
        pygame.draw.rect(surface, (0, 255, 0), (130, 50, health_width, 30))
        pygame.draw.rect(surface, (255, 255, 255), (130, 50, 300, 30), 2)

        # Иконка буста
        if self.player.boost_active and pygame.time.get_ticks() < self.player.boost_end_time:
            surface.blit(self.boost_icon, (130 + 310, 48))


def draw_stains(surface, stains, blood_image, camera_x):
    for stain in stains:
        surface.blit(stain.image, (stain.x - camera_x, stain.y))

def run_game(screen):
    heal_image = pygame.transform.scale(pygame.image.load("assets/textures/heal.png").convert_alpha(), (64, 64))
    boost_image = pygame.transform.scale(pygame.image.load("assets/textures/boost.png").convert_alpha(), (64, 64))
    game_map = GameMap("level1.map", heal_image, boost_image)
    global blood_stains
    clock = pygame.time.Clock()
    player = Player(*game_map.get_player_spawn().topleft)
    ui = UI(player)
    blood_stains = []
    blood_particles = []
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
        for particle in blood_particles[:]:
            particle.update(game_map.platforms, blood_stains)
            if particle.on_ground:
                blood_particles.remove(particle)
        keys = pygame.key.get_pressed()
        if not paused:
            for item in game_map.items[:]:
                if player.rect.colliderect(item.rect):
                    item.apply(player)
                    game_map.items.remove(item)

           
            for item in game_map.items:
                item.draw(screen, camera_x)

            player.update(keys, enemies, game_map, blood_particles, blood_image)
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
                    stain_img = random.choice(blood_stain_images)
                    stain = BloodStain(enemy.rect.centerx, enemy.rect.bottom, stain_img)
                    blood_stains.append(stain)
                    enemies.remove(enemy)
                    random.choice(kill_sounds).play()

        camera_x = player.rect.x - WIDTH // 3
        game_map.draw(screen, camera_x)
        draw_stains(screen, blood_stains, blood_image, camera_x)
        for particle in blood_particles:
            particle.draw(screen, camera_x)

        for enemy in enemies:
            enemy.draw(screen, camera_x)

        player.draw(screen, camera_x)
        ui.draw(screen)
        if player.boost_active and pygame.time.get_ticks() < player.boost_end_time:
            red_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2  # от 0 до 1
            max_alpha = int(160 * pulse)  # максимум прозрачности пульсации

            for i in range(40):
                alpha = int(max_alpha * (1 - i / 40))
                pygame.draw.rect(red_overlay, (100, 0, 0, alpha), (i, 0, 1, HEIGHT))
                pygame.draw.rect(red_overlay, (100, 0, 0, alpha), (WIDTH - i, 0, 1, HEIGHT))
                pygame.draw.rect(red_overlay, (100, 0, 0, alpha), (0, i, WIDTH, 1))
                pygame.draw.rect(red_overlay, (100, 0, 0, alpha), (0, HEIGHT - i, WIDTH, 1))
            screen.blit(red_overlay, (0, 0))
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
        
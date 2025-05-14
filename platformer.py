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

pygame.mixer.init()
background_music = "assets/music/Red Forest.mp3"
pygame.mixer.music.load(background_music)
pygame.mixer.music.set_volume(config.get("music_volume", 0.5))
pygame.mixer.music.play(-1)

background_img = pygame.transform.scale(
    pygame.image.load("assets/images/level1bg.jpg").convert(), (1280, 720)
)

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
        self.dead = False

        
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
        if self.dead:
            return
        self.health -= amount
        random.choice(hurt_sounds).play()
        if self.health <= 0:
            self.dead = True

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
            self.attack_cooldown = 20
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
        for platform in game_map.ground_platforms + game_map.flying_platforms + game_map.barriers:
            if self.rect.colliderect(platform):
                if dx > 0:
                    self.rect.right = platform.left
                elif dx < 0:
                    self.rect.left = platform.right


        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in game_map.ground_platforms + game_map.flying_platforms + game_map.barriers:
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
        self.direction = direction.normalize()  
        self.speed = 3
        
        self.image = pygame.transform.scale(
            pygame.image.load("assets/sprites/bullet.png").convert_alpha(),
            (20, 10)  
        )
        
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.rotated_image = pygame.transform.rotate(self.image, angle)

    def update(self, paused=False):
        if not paused:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed

    def draw(self, surface, camera_x):
        if -500 < self.rect.x - camera_x < WIDTH + 500:
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def off_screen(self, camera_x):
        screen_left = camera_x
        screen_right = camera_x + 1280
        screen_top = 0
        screen_bottom = 720
        
        return (self.rect.right < screen_left - 100 or
                self.rect.left > screen_right + 100 or
                self.rect.bottom < screen_top - 100 or
                self.rect.top > screen_bottom + 100)
    
class Enemy:
    def __init__(self, x, y, enemy_type="melee"):
        self.rect = pygame.Rect(x, y, 50, 80)
        self.type = enemy_type
        self.health = 50
        self.direction = -1
        self.speed = 3
        self.vel_y = 0
        self.on_ground = False
        self.bullets = []
        self.attack_cooldown = random.randint(60, 90)
        
        
        if enemy_type == "melee":
            self.image = pygame.transform.scale(
                pygame.image.load("assets/sprites/melee-enemy1.png").convert_alpha(), 
                (50, 80)
            )
        else:  
            self.image = pygame.transform.scale(
                pygame.image.load("assets/sprites/ranged-enemy.png").convert_alpha(),
                (50, 80)
            )
            
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def update(self, player, game_map, camera_x):
        enemy_on_screen = (self.rect.right > camera_x - 100 and 
                      self.rect.left < camera_x + 1280 + 100)
    
        if not enemy_on_screen:
            return  
        
        self.vel_y += 0.5
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in game_map.ground_platforms + game_map.flying_platforms:
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

            for platform in game_map.ground_platforms + game_map.flying_platforms:
                if self.rect.colliderect(platform):
                    if self.direction > 0:
                        self.rect.right = platform.left
                    else:
                        self.rect.left = platform.right

            if self.attack_cooldown <= 0 and self.rect.colliderect(player.rect):
                player.take_damage(5)
                self.attack_cooldown = 60

        if self.type == "ranged":
            if self.attack_cooldown <= 0:
                self.shoot(player)
                self.attack_cooldown = 220 
            else:
                self.attack_cooldown -= 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.colliderect(player.rect):
                player.take_damage(10)
                self.bullets.remove(bullet)


    def shoot(self, player):
        direction = pygame.math.Vector2(player.rect.centerx - self.rect.centerx,
                                    player.rect.centery - self.rect.centery)
        if direction.length() > 0:
            direction = direction.normalize()
            
            spawn_x = self.rect.centerx + direction.x * 30
            spawn_y = self.rect.centery + direction.y * 30
            bullet = Bullet(spawn_x, spawn_y, direction)
            self.bullets.append(bullet)
            

    def draw(self, surface, camera_x):
        if self.direction > 0:  
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))
        else:  
            flipped = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped, (self.rect.x - camera_x, self.rect.y))

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
        face_img = self.get_face_image()
        face_img = pygame.transform.scale(face_img, (128, 110))  # Масштаб 100x100
        surface.blit(face_img, (5, 5))

        health_width = 300 * (self.player.health / self.player.max_health)
        pygame.draw.rect(surface, (255, 0, 0), (130, 50, 300, 30))
        pygame.draw.rect(surface, (0, 255, 0), (130, 50, health_width, 30))
        pygame.draw.rect(surface, (255, 255, 255), (130, 50, 300, 30), 2)

        if self.player.boost_active and pygame.time.get_ticks() < self.player.boost_end_time:
            surface.blit(self.boost_icon, (130 + 310, 48))


def draw_stains(surface, stains, blood_image, camera_x):
    for stain in stains:
        surface.blit(stain.image, (stain.x - camera_x, stain.y))

def run_game(screen, level="level1"):
    heal_image = pygame.transform.scale(pygame.image.load("assets/textures/heal.png").convert_alpha(), (64, 64))
    boost_image = pygame.transform.scale(pygame.image.load("assets/textures/boost.png").convert_alpha(), (64, 64))
    if level == "level1":
        background_music = "assets/music/Red Forest.mp3"
        background_img_path = "assets/images/level1bg.jpg"
        map_file = "level1.map"
    elif level == "level2":
        background_music = "assets/music/Castle Intruder.mp3"
        background_img_path = "assets/images/castle-bg.jpg"
        map_file = "level2.map"

    pygame.mixer.music.load(background_music)
    pygame.mixer.music.set_volume(config.get("music_volume", 0.5))
    pygame.mixer.music.play(-1)

    background_img = pygame.transform.scale(pygame.image.load(background_img_path).convert(), (WIDTH, HEIGHT))
    game_map = GameMap(map_file, heal_image, boost_image)
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
    death_camera_x = None
    font = pygame.font.Font(None, 48)
    pause_options = ["Продолжить", "Настройки", "Выход"]
    selected_option = 0
    
    camera_x = 0
    running = True
    show_controls = True
    controls_start_time = pygame.time.get_ticks()
    controls_duration = 5000  
    controls_surface = pygame.Surface((300, 100), pygame.SRCALPHA)

    font_small = pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 24)
    control_lines = [
        "Управление:",
        "← → — движение",
        "Space — прыжок",
        "F — атака",
        "ESC — пауза"
    ]

    for i, line in enumerate(control_lines):
        text = font_small.render(line, True, (255, 255, 255))
        controls_surface.blit(text, (10, 10 + i * 20))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif paused:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(pause_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(pause_options)
                    elif event.key == pygame.K_RETURN:
                        if pause_options[selected_option] == "Продолжить":
                            paused = False
                            pygame.mixer.music.unpause()
                        elif pause_options[selected_option] == "Настройки":
                            open_settings(screen)
                        elif pause_options[selected_option] == "Выход":
                            pygame.quit()
                            exit()
                elif player.dead and event.key == pygame.K_r:
                    pygame.mixer.music.stop()
                    run_game(screen, level=level)
                    return
                
        for particle in blood_particles[:]:
            particle.update(game_map.ground_platforms + game_map.flying_platforms, blood_stains)
            if particle.on_ground:
                blood_particles.remove(particle)
        keys = pygame.key.get_pressed()
        if not paused:
            for item in game_map.items[:]:
                if player.rect.colliderect(item.rect):
                    item.apply(player)
                    game_map.items.remove(item)

        if not paused and not player.dead:
            keys = pygame.key.get_pressed()
            player.update(keys, enemies, game_map, blood_particles, blood_image)
            for spike in game_map.spikes:
                if player.rect.colliderect(spike):
                    player.health -= 100
                    player.dead = True
            for i, enemy in enumerate(enemies[:]):
                enemy.update(player, game_map, camera_x)
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
            for door in game_map.doors:
                if player.rect.colliderect(door):
                    fade = pygame.Surface((WIDTH, HEIGHT))
                    fade.fill((255, 255, 255))
                    for alpha in range(0, 256, 5):
                        fade.set_alpha(alpha)
                        screen.blit(fade, (0, 0))
                        pygame.display.update()
                        pygame.time.delay(15)

                    pygame.mixer.music.stop()

                    if level == "level1":
                        from cutscene2 import play_cutscene2
                        play_cutscene2(screen)
                        run_game(screen, level="level2")
                    elif level == "level2":
                        from cutscene3 import play_cutscene3
                        play_cutscene3(screen)
                        from menu import main_menu
                        main_menu()
                    return
                    
            for enemy in enemies:
                for bullet in enemy.bullets[:]:
                    bullet.update(paused)
                    if bullet.off_screen(camera_x):  
                        enemy.bullets.remove(bullet)

            for item in game_map.items[:]:
                if player.rect.colliderect(item.rect):
                    item.apply(player)
                    game_map.items.remove(item)

            camera_x = player.rect.x - WIDTH // 3

        screen.blit(background_img, (0, 0))
        game_map.draw(screen, camera_x)
        draw_stains(screen, blood_stains, blood_image, camera_x)
        
        for particle in blood_particles[:]:
            particle.update(game_map.ground_platforms + game_map.flying_platforms, blood_stains)
            particle.draw(screen, camera_x)
            if particle.on_ground:
                blood_particles.remove(particle)

        for enemy in enemies:
            enemy.draw(screen, camera_x)
            for bullet in enemy.bullets:
                bullet.draw(screen, camera_x)

        if not player.dead:
            player.draw(screen, camera_x)

        ui.draw(screen)


        if player.boost_active and pygame.time.get_ticks() < player.boost_end_time:
            red_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2  
            max_alpha = int(160 * pulse) 

            for i in range(40):
                alpha = int(max_alpha * (1 - i / 40))
                pygame.draw.rect(red_overlay, (100, 0, 0, alpha), (i, 0, 1, HEIGHT))
                pygame.draw.rect(red_overlay, (100, 0, 0, alpha), (WIDTH - i, 0, 1, HEIGHT))
                pygame.draw.rect(red_overlay, (100, 0, 0, alpha), (0, i, WIDTH, 1))
                pygame.draw.rect(red_overlay, (100, 0, 0, alpha), (0, HEIGHT - i, WIDTH, 1))
            screen.blit(red_overlay, (0, 0))
        if player.dead:
            if death_camera_x is None:
                death_camera_x = camera_x
                for _ in range(40):
                    blood_particles.append(BloodParticle(player.rect.centerx, player.rect.centery, random.choice(blood_splashes)))
            
            death_font = pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 72)
            restart_font = pygame.font.Font("assets/fonts/HomeVideo-Regular.otf", 36)
            
            death_text = death_font.render("YOU DIED", True, (255, 0, 0))
            restart_text = restart_font.render("Press R to Restart", True, (255, 255, 255))
            
            blink = (pygame.time.get_ticks() // 500) % 2 == 0
            
            screen.blit(death_text, (WIDTH//2 - death_text.get_width()//2, HEIGHT//2 - 60))
            if blink:
                screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            for i, option in enumerate(pause_options):
                color = (255, 255, 0) if i == selected_option else (255, 255, 255)
                text = font.render(option, True, color)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

        sun_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        sun_overlay.fill((255, 255, 200, 25))
        screen.blit(sun_overlay, (0, 0))
        if show_controls:
            elapsed = pygame.time.get_ticks() - controls_start_time
            if elapsed >= controls_duration:
                alpha = max(255 - int((elapsed - controls_duration) / 5), 0)
                if alpha <= 0:
                    show_controls = False
                else:
                    temp_surface = pygame.Surface((300, 110), pygame.SRCALPHA)
                    temp_surface.fill((20, 20, 20, 200))  # фон с альфой
                    for i, line in enumerate(control_lines):
                        text = font_small.render(line, True, (255, 255, 255))
                        temp_surface.blit(text, (10, 10 + i * 20))
                    temp_surface.set_alpha(alpha)
                    screen.blit(temp_surface, (WIDTH - 320, 20))
            else:
                temp_surface = pygame.Surface((300, 110), pygame.SRCALPHA)
                temp_surface.fill((20, 20, 20, 200))  # фон с альфой
                for i, line in enumerate(control_lines):
                    text = font_small.render(line, True, (255, 255, 255))
                    temp_surface.blit(text, (10, 10 + i * 20))
                screen.blit(temp_surface, (WIDTH - 320, 20))
        pygame.display.flip()
        clock.tick(60)
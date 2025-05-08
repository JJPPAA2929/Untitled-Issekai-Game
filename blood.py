import pygame
import random

# Загрузка спрайтов
splash_images = [
    pygame.image.load(f"assets/blood/blood-splash{i}.png").convert_alpha()
    for i in range(1, 12)
]
stain_images = [
    pygame.image.load(f"assets/blood/blood-stain{i}.png").convert_alpha()
    for i in range(1, 14)
]

class BloodParticle:
    def __init__(self, x, y, image, scale=48):
        self.image = pygame.transform.scale(image, (scale, scale))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = [random.uniform(-9, 9), random.uniform(-12, -9)]
        self.gravity = 0.3
        self.on_ground = False
        self.timer = 120
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, platforms, blood_stains):
        if not self.on_ground:
            self.velocity[1] += self.gravity
            self.rect.x += int(self.velocity[0])
            self.rect.y += int(self.velocity[1])

            for platform in platforms:
                if self.rect.colliderect(platform):
                    # только если кровь падает сверху на платформу
                    if self.rect.bottom - self.velocity[1] <= platform.top:
                        self.on_ground = True
                        stain_img = random.choice(stain_images)
                        stain = BloodStain(self.rect.x, platform.top - 8, stain_img)
                        blood_stains.append(stain)
                    else:
                        self.timer=0

        self.timer -= 1
        return self.timer > 0

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class BloodStain:
    def __init__(self, x, y, image):
        self.image = pygame.transform.scale(image, (64, 64))
        self.x = x
        self.y = y

import pygame

pygame.init()

W, H = 1920, 1080
bg = pygame.Surface((W, H))

# Тёмный фон
bg.fill((15, 12, 10))

# Пол (каменные плиты)
for y in range(600, H, 40):
    shade = 50 if (y // 40) % 2 == 0 else 40
    pygame.draw.rect(bg, (shade, shade - 5, shade - 10), (0, y, W, 20))
    pygame.draw.line(bg, (30, 28, 25), (0, y), (W, y), 1)

# Левая стена
pygame.draw.rect(bg, (35, 30, 25), (0, 0, 300, 600))
# Правая стена
pygame.draw.rect(bg, (35, 30, 25), (W - 300, 0, 300, 600))

# Камни на стенах
import random
random.seed(42)
for _ in range(20):
    x = random.randint(10, 270) if random.random() < 0.5 else random.randint(W - 290, W - 20)
    y = random.randint(10, 580)
    w, h = random.randint(40, 80), random.randint(25, 50)
    shade = random.randint(45, 60)
    pygame.draw.rect(bg, (shade, shade - 5, shade - 10), (x, y, w, h))
    pygame.draw.rect(bg, (25, 22, 18), (x, y, w, h), 2)

# Факелы
for side_x in [250, W - 270]:
    for fy in [120, 300, 480]:
        # Держатель
        pygame.draw.rect(bg, (80, 60, 20), (side_x, fy - 5, 20, 8))
        # Огонь (простая форма)
        flame_x = side_x + 25
        pygame.draw.circle(bg, (255, 180, 30), (flame_x, fy - 10), 12)
        pygame.draw.circle(bg, (255, 220, 60), (flame_x, fy - 15), 7)
        pygame.draw.circle(bg, (255, 140, 10), (flame_x, fy - 5), 8)
        # Свечение
        for r in range(30, 80, 15):
            alpha = 40 - r // 2
            if alpha > 0:
                glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 150, 30, max(0, alpha)), (r, r), r)
                bg.blit(glow, (flame_x - r, fy - r))

# Затемнение по бокам
dark_left = pygame.Surface((400, H), pygame.SRCALPHA)
for x in range(400):
    alpha = 200 - x // 2
    if alpha > 0:
        pygame.draw.line(dark_left, (0, 0, 0, min(200, alpha)), (x, 0), (x, H))
bg.blit(dark_left, (0, 0))

dark_right = pygame.Surface((400, H), pygame.SRCALPHA)
for x in range(400):
    alpha = 200 - x // 2
    if alpha > 0:
        pygame.draw.line(dark_right, (0, 0, 0, min(200, alpha)), (x, 0), (x, H))
bg.blit(dark_right, (W - 400, 0))

# Верхняя арка
pygame.draw.rect(bg, (25, 20, 15), (300, 0, W - 600, 80))
pygame.draw.ellipse(bg, (15, 12, 10), (400, -40, W - 800, 200))

pygame.image.save(bg, "images/menu_bg.png")
print("menu_bg.png создан!")
import pygame

pygame.init()

floor = pygame.Surface((64, 64))

# Базовый цвет
floor.fill((100, 95, 85))


import random
random.seed(42)

for _ in range(12):
    x = random.randint(0, 60)
    y = random.randint(0, 60)
    w = random.randint(10, 25)
    h = random.randint(8, 20)
    shade = random.randint(80, 120)
    color = (shade, shade - 5, shade - 15)
    pygame.draw.rect(floor, color, (x, y, w, h))
    pygame.draw.rect(floor, (60, 55, 45), (x, y, w, h), 1)

# Трещины
for _ in range(5):
    x1, y1 = random.randint(0, 60), random.randint(0, 60)
    x2, y2 = x1 + random.randint(-10, 10), y1 + random.randint(-10, 10)
    pygame.draw.line(floor, (50, 45, 35), (x1, y1), (x2, y2), 1)

pygame.image.save(floor, "images/floor.png")
print("floor.png создана!")
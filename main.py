import pygame
import sys
import random

pygame.init()

# текстуры для игры
try:
    player_img = pygame.image.load("images/player.png")
    player_img = pygame.transform.scale(player_img, (30, 30))
except:
    player_img = None

enemy_imgs = {}
try:
    enemy_imgs['normal'] = pygame.transform.scale(pygame.image.load('images/enemy_normal.png'), (24, 24))
    enemy_imgs['fast'] = pygame.transform.scale(pygame.image.load('images/enemy_fast.png'), (24, 24))
    enemy_imgs['tank'] = pygame.transform.scale(pygame.image.load('images/enemy_tank.png'), (30, 30))
    enemy_imgs['shooter'] = pygame.transform.scale(pygame.image.load('images/enemy_shooter.png'), (24, 24))
except:
    enemy_imgs = {}
try:
    bullet_img = pygame.transform.scale(pygame.image.load('images/bullet.png'), (8, 8))
except:
    bullet_img = None
try:
    coin_img = pygame.transform.scale(pygame.image.load('images/coin.png'), (14, 14))
except:
    coin_img = None
try:
    floor_img = pygame.image.load('images/floor.png')
    floor_img = pygame.transform.scale(floor_img, (64, 64))
except:
    floor_img = None

# Окно
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Alone")
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (255, 255, 0)
GRAY = (40, 40, 40)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 50)

# Игрок
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 4
player_radius = 15
player_hp = 100
player_max_hp = 100

# Оружие
bullets = []
enemy_bullets = []
attack_cooldown = 0
attack_speed = 30
bullet_speed = 8
bullet_damage = 25

# Опыт
xp = 0
level = 1
xp_to_level = 50
level_up_choices = []
choosing = False

# Монеты
coins = []
total_coins = 0

# Враги и волны
enemies = []
wave = 1
enemies_in_wave = 10
enemies_spawned = 0
enemies_killed_wave = 0
spawn_timer = 0
wave_delay = 0
boss = None
boss_spawned = False
enemies_to_boss = 100

# Меню
in_menu = True
game_over = False
in_shop = False

# Шрифт
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)


def spawn_enemy():
    side = random.randint(0, 3)
    if side == 0:
        ex, ey = random.randint(0, WIDTH), -20
    elif side == 1:
        ex, ey = random.randint(0, WIDTH), HEIGHT + 20
    elif side == 2:
        ex, ey = -20, random.randint(0, HEIGHT)
    else:
        ex, ey = WIDTH + 20, random.randint(0, HEIGHT)

    enemy_type = random.choices(
        ["normal", "fast", "tank", "shooter"],
        weights=[50, 25, 15, 10],
        k=1
    )[0]

    if enemy_type == "normal":
        hp = random.randint(20, 30)
        speed = random.uniform(2, 3)
        color = RED
    elif enemy_type == "fast":
        hp = 15
        speed = random.uniform(4, 5)
        color = ORANGE
    elif enemy_type == "tank":
        hp = 80
        speed = random.uniform(1, 1.5)
        color = (150, 30, 30)
    else:  # shooter
        hp = 25
        speed = 1.5
        color = PURPLE

    enemies.append([ex, ey, hp, hp, speed, enemy_type, 0])


def spawn_boss():
    global boss, boss_spawned
    boss = [WIDTH // 2, -50, 500, 500, 1.5]
    boss_spawned = True


def get_level_up_choices():
    choices = [
        {"name": "+20 Max HP", "effect": "max_hp", "value": 20},
        {"name": "+Speed", "effect": "speed", "value": 1},
        {"name": "+Attack Speed", "effect": "attack_speed", "value": -5},
        {"name": "+Damage", "effect": "damage", "value": 10},
        {"name": "+Bullet Speed", "effect": "bullet_speed", "value": 2},
        {"name": "Heal 30 HP", "effect": "heal", "value": 30},
    ]
    return random.sample(choices, 3)


def apply_choice(choice):
    global player_max_hp, player_hp, player_speed, attack_speed, bullet_damage, bullet_speed
    if choice["effect"] == "max_hp":
        player_max_hp += choice["value"]
        player_hp = min(player_hp + choice["value"], player_max_hp)
    elif choice["effect"] == "speed":
        player_speed += choice["value"]
    elif choice["effect"] == "attack_speed":
        attack_speed = max(5, attack_speed + choice["value"])
    elif choice["effect"] == "damage":
        bullet_damage += choice["value"]
    elif choice["effect"] == "bullet_speed":
        bullet_speed += choice["value"]
    elif choice["effect"] == "heal":
        player_hp = min(player_hp + choice["value"], player_max_hp)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and (in_menu or game_over):
                # Полный сброс
                player_x, player_y = WIDTH // 2, HEIGHT // 2
                player_hp = 100
                player_max_hp = 100
                player_speed = 4
                attack_speed = 30
                bullet_speed = 8
                bullet_damage = 25
                enemy_bullets.clear()
                enemies.clear()
                bullets.clear()
                coins.clear()
                xp = 0
                level = 1
                xp_to_level = 50
                wave = 1
                enemies_in_wave = 10
                enemies_spawned = 0
                enemies_killed_wave = 0
                spawn_timer = 0
                wave_delay = 0
                boss = None
                boss_spawned = False
                enemies_to_boss = 100
                total_coins = 0
                choosing = False
                in_menu = False
                game_over = False
                in_shop = False
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if choosing:
                if event.key == pygame.K_1 and len(level_up_choices) >= 1:
                    apply_choice(level_up_choices[0])
                    choosing = False
                if event.key == pygame.K_2 and len(level_up_choices) >= 2:
                    apply_choice(level_up_choices[1])
                    choosing = False
                if event.key == pygame.K_3 and len(level_up_choices) >= 3:
                    apply_choice(level_up_choices[2])
                    choosing = False

    # Меню
    if in_menu:
        screen.fill(BLACK)
        title = big_font.render("ALONE", True, WHITE)
        start = font.render("Press SPACE to start", True, GRAY)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        screen.blit(start, start.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        pygame.display.flip()
        clock.tick(60)
        continue

    # Магаз
    if in_shop:
        screen.fill(BLACK)
        shop_title = big_font.render("SHOP", True, YELLOW)
        coins_text = font.render(f"Coins: {total_coins}", True, WHITE)
        continue_text = font.render("Press SPACE to continue", True, GRAY)
        screen.blit(shop_title, shop_title.get_rect(center=(WIDTH // 2, 200)))
        screen.blit(coins_text, coins_text.get_rect(center=(WIDTH // 2, 300)))
        screen.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, 400)))
        pygame.display.flip()
        clock.tick(60)
        continue

    #ИГра
    if not game_over and not choosing and not in_shop:
        # Управление
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        player_x += dx * player_speed
        player_y += dy * player_speed
        player_x = max(player_radius, min(WIDTH - player_radius, player_x))
        player_y = max(player_radius, min(HEIGHT - player_radius, player_y))

        # Авто-атака в направлении мыши
        attack_cooldown -= 1
        if (enemies or boss) and attack_cooldown <= 0:
            mx, my = pygame.mouse.get_pos()
            edx = mx - player_x
            edy = my - player_y
            dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
            bullets.append([player_x, player_y, edx / dist * bullet_speed, edy / dist * bullet_speed])
            attack_cooldown = attack_speed

        # Движение пуль
        for b in bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[0] < 0 or b[0] > WIDTH or b[1] < 0 or b[1] > HEIGHT:
                bullets.remove(b)

        # пули врагов
        for b in enemy_bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[0] < 0 or b[0] > WIDTH or b[1] < 0 or b[1] > HEIGHT:
                enemy_bullets.remove(b)
            elif abs(b[0] - player_x) < 15 and abs(b[1] - player_y) < 15:
                enemy_bullets.remove(b)
                player_hp -= 10

        # Спавн врагов по волнам
        if not boss_spawned:
            if wave_delay > 0:
                wave_delay -= 1
            elif enemies_spawned < enemies_in_wave:
                spawn_timer += 1
                if spawn_timer > max(15, 60 - level * 2):
                    spawn_timer = 0
                    spawn_enemy()
                    enemies_spawned += 1
            elif len(enemies) == 0 and not boss:
                wave += 1
                enemies_in_wave = 10 + wave * 3
                enemies_spawned = 0
                enemies_killed_wave = 0
                wave_delay = 60

        # Движение врагов
        for e in enemies[:]:
            edx = player_x - e[0]
            edy = player_y - e[1]
            dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
            e[0] += edx / dist * e[4]
            e[1] += edy / dist * e[4]

            if abs(e[0] - player_x) < 20 and abs(e[1] - player_y) < 20:
                if len(e) > 5 and e[5] == 'shooter':
                    e[6] += 1
                    if e[6] > 120:
                        e[6] = 0
                        edx = player_x - e[0]
                        edy = player_y - e[1]
                        dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
                        enemy_bullets.append([e[0], e[1], edx/dist * 4, edy/dist * 4])
                player_hp -= 1
                if player_hp <= 0:
                    game_over = True

        # Движение босса
        if boss:
            edx = player_x - boss[0]
            edy = player_y - boss[1]
            dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
            boss[0] += edx / dist * boss[4]
            boss[1] += edy / dist * boss[4]

            if abs(boss[0] - player_x) < 30 and abs(boss[1] - player_y) < 30:
                player_hp -= 3
                if player_hp <= 0:
                    game_over = True

        # Попадание пуль во врагов
        for b in bullets[:]:
            for e in enemies[:]:
                if abs(b[0] - e[0]) < 15 and abs(b[1] - e[1]) < 15:
                    if b in bullets:
                        bullets.remove(b)
                    e[2] -= bullet_damage
                    if e[2] <= 0:
                        if e in enemies:
                            enemies.remove(e)
                            xp += 10
                            enemies_killed_wave += 1
                            if random.random() < 0.5:
                                coins.append([e[0], e[1]])
                            if enemies_killed_wave >= enemies_to_boss and not boss_spawned:
                                spawn_boss()
                    break

        # Попадание пуль в босса
        if boss:
            for b in bullets[:]:
                if abs(b[0] - boss[0]) < 40 and abs(b[1] - boss[1]) < 40:
                    if b in bullets:
                        bullets.remove(b)
                    boss[2] -= bullet_damage
                    if boss[2] <= 0:
                        boss = None
                        boss_spawned = False
                        enemies_killed_wave = 0
                        xp += 200
                        for _ in range(10):
                            coins.append([random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)])
                        total_coins += 100
                        enemies_to_boss += 50
                        in_shop = True
                    break

        # Сбор монет
        for c in coins[:]:
            if abs(c[0] - player_x) < 25 and abs(c[1] - player_y) < 25:
                coins.remove(c)
                total_coins += 1

        # Проверка уровня
        if xp >= xp_to_level:
            level += 1
            xp -= xp_to_level
            xp_to_level = int(xp_to_level * 1.5)
            if level % 10 == 0:
                level_up_choices = get_level_up_choices()
                choosing = True

    # Рисовка
    # Фон с текстурой
    if floor_img:
        for fx in range(0, WIDTH, 64):
            for fy in range(0, HEIGHT, 64):
                screen.blit(floor_img, (fx, fy))
    else:
        screen.fill(GRAY)

    for c in coins:
        if coin_img:
            screen.blit(coin_img, (c[0] - 7, c[1] - 7))
        else:
            pygame.draw.circle(screen, YELLOW, (int(c[0]), int(c[1])), 6)

    for e in enemies:
        enemy_type = e[5] if len(e) > 5 else "normal"
        if enemy_type in enemy_imgs:
            screen.blit(enemy_imgs[enemy_type], (e[0] - 12, e[1] - 12))
        else:
            enemy_color = RED
            if enemy_type == "fast":
                enemy_color = ORANGE
            elif enemy_type == "tank":
                enemy_color = (150, 30, 30)
            elif enemy_type == "shooter":
                enemy_color = PURPLE
            pygame.draw.circle(screen, enemy_color, (int(e[0]), int(e[1])), 12)
        # HP бар
        bar_w, bar_h = 30, 4
        bx, by = e[0] - bar_w // 2, e[1] - 18
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (e[2] / e[3]), bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    if boss:
        pygame.draw.circle(screen, PURPLE, (int(boss[0]), int(boss[1])), 35)
        pygame.draw.circle(screen, WHITE, (int(boss[0]), int(boss[1])), 35, 3)
        bar_w, bar_h = 70, 6
        bx, by = boss[0] - bar_w // 2, boss[1] - 45
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (boss[2] / boss[3]), bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    for b in bullets:
        if bullet_img:
            screen.blit(bullet_img, (b[0] - 4, b[1] - 4))
        else:
            pygame.draw.circle(screen, YELLOW, (int(b[0]), int(b[1])), 4)
    for b in enemy_bullets:
        pygame.draw.circle(screen, PURPLE, (int(b[0]), int(b[1])), 5)

    if not game_over:
        if player_img:
            screen.blit(player_img, (player_x - 15, player_y - 15))
        else:
            pygame.draw.circle(screen, BLUE, (int(player_x), int(player_y)), player_radius)
            pygame.draw.circle(screen, WHITE, (int(player_x), int(player_y)), player_radius, 2)
        bar_w, bar_h = 40, 5
        bx, by = player_x - bar_w // 2, player_y - player_radius - 10
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (player_hp / player_max_hp), bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    # Интерфейс
    hp_text = font.render(f"HP: {int(player_hp)}/{player_max_hp}", True, WHITE)
    lvl_text = font.render(f"LVL: {level} | XP: {xp}/{xp_to_level}", True, WHITE)
    coins_text = font.render(f"Coins: {total_coins}", True, YELLOW)
    wave_text = font.render(f"Wave: {wave} | Enemies: {len(enemies)}/{enemies_in_wave}", True, ORANGE)
    screen.blit(hp_text, (10, 10))
    screen.blit(lvl_text, (10, 40))
    screen.blit(coins_text, (10, 70))
    screen.blit(wave_text, (10, 100))

    # Объявление волны
    if wave_delay > 0:
        wave_announce = big_font.render(f"WAVE {wave}", True, YELLOW)
        screen.blit(wave_announce, wave_announce.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    if choosing:
        dark = pygame.Surface((WIDTH, HEIGHT))
        dark.set_alpha(180)
        dark.fill(BLACK)
        screen.blit(dark, (0, 0))
        choice_text = big_font.render("CHOOSE UPGRADE", True, YELLOW)
        screen.blit(choice_text, choice_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
        for i, c in enumerate(level_up_choices):
            txt = font.render(f"[{i + 1}] {c['name']}", True, WHITE)
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40)))

    if game_over:
        over_text = big_font.render("GAME OVER", True, RED)
        restart = font.render("Press SPACE to restart", True, GRAY)
        screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        screen.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

    pygame.display.flip()
    clock.tick(60)
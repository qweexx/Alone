import pygame
import sys
import random

pygame.init()

# Окно
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Alone")
clock = pygame.time.Clock()

# Карта и камера
MAP_WIDTH = 4000
MAP_HEIGHT = 3000
camera_x = 0
camera_y = 0

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
    heal_img = pygame.transform.scale(pygame.image.load('images/heal.png'), (20, 20))
except:
    heal_img = None
try:
    floor_img = pygame.image.load('images/floor.png')
    floor_img = pygame.transform.scale(floor_img, (64, 64))
except:
    floor_img = None
try:
    menu_bg_img = pygame.image.load('images/menu_bg.png')
    menu_bg_img = pygame.transform.scale(menu_bg_img, (WIDTH, HEIGHT))
except:
    menu_bg_img = None
try:
    chest_img = pygame.image.load('images/chest.png')
    chest_img = pygame.transform.scale(chest_img, (30, 30))
except:
    chest_img = None
try:
    boss_img = pygame.image.load('images/boss.png')
    boss_img = pygame.transform.scale(boss_img, (70, 70))
except:
    boss_img = None
try:
    shield_img = pygame.image.load('images/shield.png')
    shield_img = pygame.transform.scale(shield_img, (20, 20))
except:
    shield_img = None

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
player_x = MAP_WIDTH // 2
player_y = MAP_HEIGHT // 2
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

# Монеты, зелья, сундуки, щит
coins = []
heals = []
chests = []
player_shield = 0
total_coins = 0

# Магазин
shop_items = [
    {"name": "Heal 50 HP", "cost": 30, "effect": "heal", "value": 50},
    {"name": "+5 Max HP", "cost": 50, "effect": "max_hp", "value": 5},
    {"name": "+1 Speed", "cost": 40, "effect": "speed", "value": 1},
    {"name": "+10 Damage", "cost": 60, "effect": "damage", "value": 10},
    {"name": "Faster Attack", "cost": 45, "effect": "attack_speed", "value": -3},
]
shop_selected = 0

# Враги и волны
enemies = []
wave = 1
enemies_in_wave = 10
enemies_spawned = 0
enemies_killed_wave = 0
total_kills = 0
spawn_timer = 0
wave_delay = 0
boss = None
boss_spawned = False
enemies_to_boss = 100

# Меню
in_menu = True
game_over = False
in_shop = False

# Пауза
paused = False

# Шрифт
try:
    font = pygame.font.Font("font.ttf", 24)
    big_font = pygame.font.Font("font.ttf", 48)
    small_font = pygame.font.Font("font.ttf", 16)
except:
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)
    small_font = pygame.font.Font(None, 24)

# Язык
lang = "ru"
texts = {
    "ru": {
        "title": "ОДИН",
        "start": "ПРОБЕЛ чтобы начать",
        "shop": "МАГАЗИН",
        "coins": "Монеты",
        "continue": "ПРОБЕЛ чтобы продолжить",
        "choose": "ВЫБЕРИ УЛУЧШЕНИЕ",
        "wave": "Волна",
        "boss_in": "До босса",
        "hp": "HP",
        "lvl": "УР",
        "game_over": "ИГРА ОКОНЧЕНА",
        "restart": "ПРОБЕЛ чтобы начать заново",
        "up_down_buy": "СТРЕЛКИ - выбор | ENTER - купить | ПРОБЕЛ - выход",
        "enemies": "Врагов",
        "lang_hint": "L - язык",
    },
    "en": {
        "title": "ALONE",
        "start": "Press SPACE to start",
        "shop": "SHOP",
        "coins": "Coins",
        "continue": "Press SPACE to continue",
        "choose": "CHOOSE UPGRADE",
        "wave": "Wave",
        "boss_in": "Boss in",
        "hp": "HP",
        "lvl": "LVL",
        "game_over": "GAME OVER",
        "restart": "Press SPACE to restart",
        "up_down_buy": "UP/DOWN - choose | ENTER - buy | SPACE - leave",
        "enemies": "Enemies",
        "lang_hint": "L - language",
    }
}

def t(key):
    return texts[lang][key]

# Скины
skins = [
    {"name": "Knight", "img": "player.png", "cost": 0, "unlocked": True},
    {"name": "Mage", "img": "player_mage.png", "cost": 100, "unlocked": False},
    {"name": "Archer", "img": "player_archer.png", "cost": 200, "unlocked": False},
    {"name": "Berserk", "img": "player_berserk.png", "cost": 500, "unlocked": False},
]
current_skin = 0
in_skins = False
skin_selected = 0

def load_skins():
    try:
        with open('skins.txt', 'r') as f:
            data = f.read().strip().split(',')
            for i, val in enumerate(data):
                if i < len(skins):
                    skins[i]['unlocked'] = (val == '1')
    except:
        pass

def save_skins():
    with open('skins.txt', 'w') as f:
        f.write(','.join(['1' if s['unlocked'] else '0' for s in skins]))

load_skins()

# загрузка картинок скинов
for s in skins:
    try:
        s["image"] = pygame.image.load(f"images/{s['img']}")
        s["image"] = pygame.transform.scale(s["image"], (30, 30))
    except:
        s["image"] = player_img


def spawn_enemy():
    margin = 50
    side = random.randint(0, 3)
    if side == 0:
        ex = random.randint(int(camera_x) - margin, int(camera_x) + WIDTH + margin)
        ey = camera_y - margin
    elif side == 1:
        ex = random.randint(int(camera_x) - margin, int(camera_x) + WIDTH + margin)
        ey = camera_y + HEIGHT + margin
    elif side == 2:
        ex = camera_x - margin
        ey = random.randint(int(camera_y) - margin, int(camera_y) + HEIGHT + margin)
    else:
        ex = camera_x + WIDTH + margin
        ey = random.randint(int(camera_y) - margin, int(camera_y) + HEIGHT + margin)

    ex = max(0, min(MAP_WIDTH, ex))
    ey = max(0, min(MAP_HEIGHT, ey))

    enemy_type = random.choices(
        ["normal", "fast", "tank", "shooter"],
        weights=[50, 25, 15, 10],
        k=1
    )[0]

    wave_bonus = min(wave, 20)
    hp_mult = 1 + wave_bonus * 0.3
    spd_mult = 1 + wave_bonus * 0.05

    if enemy_type == "normal":
        hp = int(random.randint(20, 30) * hp_mult)
        speed = random.uniform(2, 3) * spd_mult
    elif enemy_type == "fast":
        hp = int(15 * hp_mult)
        speed = random.uniform(4, 5) * spd_mult
    elif enemy_type == "tank":
        hp = int(80 * hp_mult)
        speed = random.uniform(1, 1.5) * spd_mult
    else:
        hp = int(25 * hp_mult)
        speed = 1.5 * spd_mult

    enemies.append([ex, ey, hp, hp, speed, enemy_type, 0])


def spawn_boss():
    global boss, boss_spawned
    boss = [camera_x + WIDTH // 2, camera_y - 50, 500, 500, 1.5]
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
            if in_skins:
                if event.key == pygame.K_UP and skin_selected > 0:
                    skin_selected -= 1
                if event.key == pygame.K_DOWN and skin_selected < len(skins) - 1:
                    skin_selected += 1
                if event.key == pygame.K_RETURN:
                    s = skins[skin_selected]
                    if s["unlocked"]:
                        current_skin = skin_selected
                    elif total_coins >= s["cost"]:
                        s["unlocked"] = True
                        total_coins -= s["cost"]
                        current_skin = skin_selected
                        save_skins()
            if in_shop:
                if event.key == pygame.K_UP:
                    shop_selected = (shop_selected - 1) % len(shop_items)
                if event.key == pygame.K_DOWN:
                    shop_selected = (shop_selected + 1) % len(shop_items)
                if event.key == pygame.K_RETURN:
                    item = shop_items[shop_selected]
                    if total_coins >= item["cost"]:
                        total_coins -= item["cost"]
                        apply_choice(item)
                if event.key == pygame.K_SPACE:
                    in_shop = False
            if event.key == pygame.K_SPACE and (in_menu or game_over) and not in_skins and not in_shop:
                player_x, player_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
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
                heals.clear()
                chests.clear()
                player_shield = 0
                paused = False
                xp = 0
                level = 1
                xp_to_level = 50
                wave = 1
                enemies_in_wave = 10
                enemies_spawned = 0
                enemies_killed_wave = 0
                total_kills = 0
                spawn_timer = 0
                wave_delay = 0
                boss = None
                boss_spawned = False
                enemies_to_boss = 100
                total_coins = 0
                shop_selected = 0
                choosing = False
                in_menu = False
                game_over = False
                in_shop = False
            if event.key == pygame.K_ESCAPE:
                if in_skins:
                    in_skins = False
                    in_menu = True
                elif in_shop:
                    in_shop = False
                elif in_menu:
                    pygame.quit()
                    sys.exit()
                elif not game_over and not in_menu:
                    paused = not paused
                else:
                    in_menu = True
                    game_over = False
            if event.key == pygame.K_p and not in_menu and not game_over and not in_shop and not in_skins:
                paused = not paused
            if event.key == pygame.K_l and in_menu:
                lang = "ru" if lang == "en" else "en"
            if event.key == pygame.K_4 and in_menu:
                in_skins = True
                in_menu = False
                skin_selected = current_skin
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

    if in_skins:
        screen.fill(BLACK)
        skin_title = font.render("SKINS", True, YELLOW)
        screen.blit(skin_title, skin_title.get_rect(center=(WIDTH // 2, 60)))
        for i, s in enumerate(skins):
            color = WHITE if i == skin_selected else GRAY
            if not s["unlocked"]:
                txt = f"{s['name']} - {s['cost']} coins"
            else:
                txt = f"{s['name']} - OWNED"
            line = font.render(txt, True, color)
            screen.blit(line, line.get_rect(center=(WIDTH // 2, 120 + i * 50)))
        hint = font.render("UP/DOWN - choose | ENTER - select/buy | ESC - back", True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 50)))
        pygame.display.flip()
        clock.tick(60)
        continue

    if in_menu:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(BLACK)
        menu_bg = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 150, 500, 300)
        pygame.draw.rect(screen, (20, 20, 30, 200), menu_bg)
        pygame.draw.rect(screen, (80, 80, 100), menu_bg, 3)
        title = big_font.render(t("title"), True, YELLOW)
        title_shadow = big_font.render(t("title"), True, (100, 80, 0))
        screen.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 - 67)))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))
        start = font.render(t("start"), True, WHITE)
        lang_text = small_font.render(t("lang_hint"), True, GRAY)
        skins_btn = small_font.render("[4] SKINS", True, GRAY)
        screen.blit(start, start.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        screen.blit(lang_text, lang_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        screen.blit(skins_btn, skins_btn.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))
        pygame.display.flip()
        clock.tick(60)
        continue

    if in_shop:
        screen.fill(BLACK)
        shop_title = big_font.render(t("shop"), True, YELLOW)
        coins_text = font.render(f"{t('coins')}: {total_coins}", True, WHITE)
        screen.blit(shop_title, shop_title.get_rect(center=(WIDTH // 2, 100)))
        screen.blit(coins_text, coins_text.get_rect(center=(WIDTH // 2, 150)))
        for i, item in enumerate(shop_items):
            color = WHITE if i == shop_selected else GRAY
            if total_coins < item["cost"]:
                color = RED
            item_text = font.render(f"{item['name']} - {item['cost']} {t('coins').lower()}", True, color)
            screen.blit(item_text, item_text.get_rect(center=(WIDTH // 2, 220 + i * 50)))
        hint = font.render(t("up_down_buy"), True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 50)))
        pygame.display.flip()
        clock.tick(60)
        continue

    if not game_over and not choosing and not in_shop and not paused:
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
        player_x = max(player_radius, min(MAP_WIDTH - player_radius, player_x))
        player_y = max(player_radius, min(MAP_HEIGHT - player_radius, player_y))

        camera_x = player_x - WIDTH // 2
        camera_y = player_y - HEIGHT // 2

        camera_x = max(0, min(MAP_WIDTH - WIDTH, camera_x))
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, camera_y))

        attack_cooldown -= 1
        if (enemies or boss) and attack_cooldown <= 0:
            mx, my = pygame.mouse.get_pos()
            wx = mx + camera_x
            wy = my + camera_y
            edx = wx - player_x
            edy = wy - player_y
            dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
            bullets.append([player_x, player_y, edx / dist * bullet_speed, edy / dist * bullet_speed])
            attack_cooldown = attack_speed

        for b in bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[0] < 0 or b[0] > MAP_WIDTH or b[1] < 0 or b[1] > MAP_HEIGHT:
                bullets.remove(b)

        for b in enemy_bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[0] < 0 or b[0] > MAP_WIDTH or b[1] < 0 or b[1] > MAP_HEIGHT:
                enemy_bullets.remove(b)
            elif abs(b[0] - player_x) < 15 and abs(b[1] - player_y) < 15:
                enemy_bullets.remove(b)
                if player_shield > 0:
                    player_shield -= 1
                else:
                    player_hp -= 10
                    if player_hp <= 0:
                        game_over = True

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

        if random.randint(0, 2700) < 1 and not boss_spawned:
            cx = random.randint(100, MAP_WIDTH - 100)
            cy = random.randint(100, MAP_HEIGHT - 100)
            chests.append([cx, cy])

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
                        enemy_bullets.append([e[0], e[1], edx / dist * 4, edy / dist * 4])
                if player_shield > 0:
                    player_shield -= 1
                else:
                    player_hp -= 1
                    if player_hp <= 0:
                        game_over = True

        if boss:
            edx = player_x - boss[0]
            edy = player_y - boss[1]
            dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
            boss[0] += edx / dist * boss[4]
            boss[1] += edy / dist * boss[4]
            if abs(boss[0] - player_x) < 30 and abs(boss[1] - player_y) < 30:
                if player_shield > 0:
                    dmg = min(3, player_shield)
                    player_shield -= dmg
                    if 3 - dmg > 0:
                        player_hp -= (3 - dmg)
                else:
                    player_hp -= 3
                if player_hp <= 0:
                    game_over = True

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
                            total_kills += 1
                            if random.random() < 0.4:
                                coins.append([e[0], e[1]])
                            if random.random() < 0.08:
                                heals.append([e[0], e[1]])
                            if total_kills >= enemies_to_boss and not boss_spawned:
                                spawn_boss()
                    break

        if boss:
            for b in bullets[:]:
                if abs(b[0] - boss[0]) < 40 and abs(b[1] - boss[1]) < 40:
                    if b in bullets:
                        bullets.remove(b)
                    boss[2] -= bullet_damage
                    if boss[2] <= 0:
                        boss = None
                        boss_spawned = False
                        total_kills = 0
                        xp += 200
                        for _ in range(10):
                            coins.append([random.randint(100, MAP_WIDTH - 100), random.randint(100, MAP_HEIGHT - 100)])
                        total_coins += 100
                        enemies_to_boss += 50
                        in_shop = True
                    break

        for c in coins[:]:
            if abs(c[0] - player_x) < 25 and abs(c[1] - player_y) < 25:
                coins.remove(c)
                total_coins += 1

        for h in heals[:]:
            if abs(h[0] - player_x) < 25 and abs(h[1] - player_y) < 25:
                heals.remove(h)
                player_hp = min(player_hp + 15, player_max_hp)

        for ch in chests[:]:
            if abs(ch[0] - player_x) < 35 and abs(ch[1] - player_y) < 35:
                chests.remove(ch)
                player_shield += 10
                for _ in range(5):
                    coins.append([ch[0] + random.randint(-20, 20), ch[1] + random.randint(-20, 20)])

        if xp >= xp_to_level:
            level += 1
            xp -= xp_to_level
            xp_to_level = int(xp_to_level * 1.5)
            if level % 10 == 0:
                level_up_choices = get_level_up_choices()
                choosing = True

    # Рисовка
    if floor_img:
        start_x = int(camera_x // 64) * 64
        start_y = int(camera_y // 64) * 64
        for fx in range(start_x - 64, int(camera_x) + WIDTH + 64, 64):
            for fy in range(start_y - 64, int(camera_y) + HEIGHT + 64, 64):
                if 0 <= fx < MAP_WIDTH and 0 <= fy < MAP_HEIGHT:
                    screen.blit(floor_img, (fx - camera_x, fy - camera_y))
    else:
        screen.fill(GRAY)

    panel = pygame.Rect(5, 5, 250, 115)
    pygame.draw.rect(screen, (0, 0, 0, 180), panel)
    pygame.draw.rect(screen, (80, 80, 100), panel, 2)

    for c in coins:
        sx, sy = c[0] - camera_x, c[1] - camera_y
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            if coin_img:
                screen.blit(coin_img, (sx - 7, sy - 7))
            else:
                pygame.draw.circle(screen, YELLOW, (int(sx), int(sy)), 6)

    for h in heals:
        sx, sy = h[0] - camera_x, h[1] - camera_y
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            if heal_img:
                screen.blit(heal_img, (sx - 10, sy - 10))
            else:
                pygame.draw.circle(screen, (255, 100, 100), (int(sx), int(sy)), 8)

    for ch in chests:
        sx, sy = ch[0] - camera_x, ch[1] - camera_y
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            if chest_img:
                screen.blit(chest_img, (sx - 15, sy - 15))
            else:
                pygame.draw.rect(screen, (139, 90, 40), (sx - 15, sy - 15, 30, 30))
                pygame.draw.rect(screen, YELLOW, (sx - 15, sy - 15, 30, 30), 2)

    for e in enemies:
        sx, sy = e[0] - camera_x, e[1] - camera_y
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            enemy_type = e[5] if len(e) > 5 else "normal"
            if enemy_type in enemy_imgs:
                screen.blit(enemy_imgs[enemy_type], (sx - 12, sy - 12))
            else:
                enemy_color = RED
                if enemy_type == "fast": enemy_color = ORANGE
                elif enemy_type == "tank": enemy_color = (150, 30, 30)
                elif enemy_type == "shooter": enemy_color = PURPLE
                pygame.draw.circle(screen, enemy_color, (int(sx), int(sy)), 12)
            bar_w, bar_h = 30, 4
            bx, by = sx - bar_w // 2, sy - 18
            pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
            pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (e[2] / e[3]), bar_h))
            pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    if boss:
        sx, sy = boss[0] - camera_x, boss[1] - camera_y
        if boss_img:
            screen.blit(boss_img, (sx - 35, sy - 35))
        else:
            pygame.draw.circle(screen, PURPLE, (int(sx), int(sy)), 35)
            pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), 35, 3)
        bar_w, bar_h = 70, 6
        bx, by = sx - bar_w // 2, sy - 45
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (boss[2] / boss[3]), bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    for b in bullets:
        sx, sy = b[0] - camera_x, b[1] - camera_y
        if bullet_img:
            screen.blit(bullet_img, (sx - 4, sy - 4))
        else:
            pygame.draw.circle(screen, YELLOW, (int(sx), int(sy)), 4)

    for b in enemy_bullets:
        sx, sy = b[0] - camera_x, b[1] - camera_y
        pygame.draw.circle(screen, PURPLE, (int(sx), int(sy)), 5)

    if not game_over:
        sx, sy = player_x - camera_x, player_y - camera_y
        skin_img = skins[current_skin].get("image", player_img)
        if skin_img:
            screen.blit(skin_img, (sx - 15, sy - 15))
        else:
            pygame.draw.circle(screen, BLUE, (int(sx), int(sy)), player_radius)
            pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), player_radius, 2)
        bar_w, bar_h = 40, 5
        bx, by = sx - bar_w // 2, sy - player_radius - 10
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (player_hp / player_max_hp), bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    lvl_text = font.render(f"{t('lvl')}: {level}", True, WHITE)
    coins_text = font.render(f"{t('coins')}: {total_coins}", True, YELLOW)
    wave_text = font.render(f"{t('wave')}: {wave}", True, ORANGE)
    boss_text = font.render(f"{t('boss_in')}: {enemies_to_boss - total_kills}", True, ORANGE)
    screen.blit(lvl_text, (15, 15))
    screen.blit(coins_text, (15, 42))
    screen.blit(wave_text, (15, 69))
    if player_shield > 0:
        shield_text = font.render(f"Shield: {player_shield}", True, (100, 150, 255))
        screen.blit(shield_text, (15, 96))

    if wave_delay > 0:
        wave_announce = big_font.render(f"{t('wave')} {wave}", True, YELLOW)
        screen.blit(wave_announce, wave_announce.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    if paused:
        dark = pygame.Surface((WIDTH, HEIGHT))
        dark.set_alpha(150)
        dark.fill(BLACK)
        screen.blit(dark, (0, 0))
        pause_text = big_font.render("PAUSE", True, YELLOW)
        screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    if choosing:
        dark = pygame.Surface((WIDTH, HEIGHT))
        dark.set_alpha(180)
        dark.fill(BLACK)
        screen.blit(dark, (0, 0))
        choice_text = big_font.render(t("choose"), True, YELLOW)
        screen.blit(choice_text, choice_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
        for i, c in enumerate(level_up_choices):
            txt = font.render(f"[{i + 1}] {c['name']}", True, WHITE)
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40)))

    if game_over:
        over_text = big_font.render(t("game_over"), True, RED)
        restart = font.render(t("restart"), True, GRAY)
        screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        screen.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

    pygame.display.flip()
    clock.tick(60)
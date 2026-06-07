import pygame
import sys
import random
import socket
import threading
import json

pygame.init()
pygame.mixer.init()

# Окно
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Alone')
clock = pygame.time.Clock()

# Карта и камера
MAP_WIDTH = 4000
MAP_HEIGHT = 3000
camera_x = 0
camera_y = 0
auto_aim = False

# цвет
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (255, 255, 0)
GRAY = (40, 40, 40)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 50)

# звук
sound_volume = 0.5
try:
    shoot_sound = pygame.mixer.Sound('sounds/shoot.wav')
    shoot_sound.set_volume(sound_volume)
except:
    shoot_sound = None

# шрифт
try:
    font = pygame.font.Font('font.ttf', 18)
    big_font = pygame.font.Font('font.ttf', 40)
    small_font = pygame.font.Font('font.ttf', 12)
except:
    font = pygame.font.Font(None, 28)
    big_font = pygame.font.Font(None, 56)
    small_font = pygame.font.Font(None, 18)

# язык
lang = 'ru'
texts = {
    'ru': {
        'title': 'ОДИН', 'start': 'ИГРАТЬ', 'shop': 'МАГАЗИН', 'coins': 'Монеты',
        'wave': 'Волна', 'lvl': 'УР', 'game_over': 'ИГРА ОКОНЧЕНА', 'restart': 'ПРОБЕЛ - заново',
        'choose': 'ВЫБЕРИ УЛУЧШЕНИЕ', 'weapon_select': 'ВЫБЕРИ ОРУЖИЕ',
        'pause': 'ПАУЗА', 'resume': 'ПРОДОЛЖИТЬ', 'menu_btn': 'МЕНЮ',
        'lobby': 'ЛОББИ', 'host': 'Создать', 'join': 'Подключиться', 'back': 'Назад',
        'settings': 'Настройки', 'sound': 'Звук', 'exit': 'ВЫХОД',
    },
    'en': {
        'title': 'ALONE', 'start': 'PLAY', 'shop': 'SHOP', 'coins': 'Coins',
        'wave': 'Wave', 'lvl': 'LVL', 'game_over': 'GAME OVER', 'restart': 'SPACE - restart',
        'choose': 'CHOOSE UPGRADE', 'weapon_select': 'CHOOSE WEAPON',
        'pause': 'PAUSE', 'resume': 'RESUME', 'menu_btn': 'MENU',
        'lobby': 'LOBBY', 'host': 'Host', 'join': 'Join', 'back': 'Back',
        'settings': 'Settings', 'sound': 'Sound', 'exit': 'EXIT',
    }
}


def t(key):
    global lang
    return texts[lang][key]


# текстуры
def load_img(path, size=None):
    try:
        img = pygame.image.load(f'images/{path}')
        return pygame.transform.scale(img, size) if size else img
    except:
        return None


player_img = load_img('player.png', (30, 30))
enemy_imgs = {}
for name in ['normal', 'fast', 'tank', 'shooter']:
    enemy_imgs[name] = load_img(f'enemy_{name}.png', (24, 24))
arrow_img = load_img('arrow.png', (10, 4))
bolt_img = load_img('bolt.png', (8, 4))
musket_ball_img = load_img('musket_ball.png', (6, 6))
coin_img = load_img('coin.png', (14, 14))
heal_img = load_img('heal.png', (20, 20))
chest_img = load_img('chest.png', (30, 30))
boss_img = load_img('boss.png', (70, 70))
menu_bg_img = load_img('menu_bg.png', (WIDTH, HEIGHT))
lobby_bg_img = load_img('lobby_bg.png', (WIDTH, HEIGHT))

weapon_icons = {}
for w in ['sword', 'axe', 'bow', 'crossbow', 'musket']:
    weapon_icons[w] = load_img(f'{w}.png', (30, 30))

floor_imgs = []
for name in ['floor.png', 'floor2.png', 'floor3.png']:
    img = load_img(name)
    if img:
        floor_imgs.append(pygame.transform.scale(img, (64, 64)))
floor_img = random.choice(floor_imgs) if floor_imgs else None

# декорации
decorations = []
decoration_imgs = []
for name in ['stone.png', 'tree.png', 'bush.png']:
    img = load_img(name, (40, 40))
    if img:
        decoration_imgs.append(img)


def generate_decorations():
    global decorations
    decorations = []
    if not decoration_imgs:
        return
    for _ in range(80):
        dx = random.randint(0, MAP_WIDTH)
        dy = random.randint(0, MAP_HEIGHT)
        img_idx = random.randint(0, len(decoration_imgs) - 1)
        decorations.append([dx, dy, img_idx])


if decoration_imgs:
    generate_decorations()

# игрок
player_x = MAP_WIDTH // 2
player_y = MAP_HEIGHT // 2
player_speed = 4
player_radius = 15
player_hp = 100
player_max_hp = 100
player_shield = 0

# профиль
profile_level = 1
profile_xp = 0
profile_xp_to_next = 100

# оружие
bullets = []
enemy_bullets = []
attack_cooldown = 0

weapons = {
    'sword': {'name': 'Sword', 'speed': 25, 'damage': 40, 'bullet_speed': 0},
    'axe': {'name': 'Axe', 'speed': 35, 'damage': 60, 'bullet_speed': 0},
    'bow': {'name': 'Bow', 'speed': 30, 'damage': 25, 'bullet_speed': 8},
    'crossbow': {'name': 'Crossbow', 'speed': 45, 'damage': 45, 'bullet_speed': 10},
    'musket': {'name': 'Musket', 'speed': 70, 'damage': 80, 'bullet_speed': 14},
}
weapon_keys = ['sword', 'bow']
weapon_type = 'sword'
weapon_index = 0
in_weapon_select = False

# опыт
xp = 0
level = 1
xp_to_level = 50
level_up_choices = []
choosing = False

# монеты, зелья, сундуки
coins = []
heals = []
chests = []
game_coins = 0
total_coins = 0

# навыки
skill_q_timer = 0
skill_e_timer = 0
skill_e_unlocked = False
fireball_active = False
fireball_timer = 0
freeze_active = False
freeze_timer = 0
rage_active = False
rage_timer = 0
shield_skill_timer = 0

# враги и волны
enemies = []
wave = 1
enemies_in_wave = 5
enemies_spawned = 0
enemies_killed_wave = 0
total_kills = 0
spawn_timer = 0
wave_delay = 0
boss = None
boss_spawned = False
enemies_to_boss = 100

# меню
in_menu = True
game_over = False
in_shop = False
paused = False
in_lobby = False
in_settings = False
lobby_message = ''

# сеть
network_player2 = None
is_host = False
is_client = False
client_socket = None
server_socket = None


# сохранения
def save_game():
    data = {
        'total_coins': total_coins,
        'skill_e_unlocked': skill_e_unlocked,
        'lang': lang,
        'sound_volume': sound_volume,
        'skins': [s['unlocked'] for s in skins],
        'profile_level': profile_level,
        'profile_xp': profile_xp,
    }
    try:
        with open('save.json', 'w') as f:
            json.dump(data, f)
    except:
        pass


def load_game():
    global total_coins, skill_e_unlocked, lang, sound_volume, profile_level, profile_xp
    try:
        with open('save.json', 'r') as f:
            data = json.load(f)
            total_coins = data.get('total_coins', 0)
            skill_e_unlocked = data.get('skill_e_unlocked', False)
            lang = data.get('lang', 'ru')
            sound_volume = data.get('sound_volume', 0.5)
            profile_level = data.get('profile_level', 1)
            profile_xp = data.get('profile_xp', 0)
            if 'skins' in data:
                for i, unlocked in enumerate(data['skins']):
                    if i < len(skins):
                        skins[i]['unlocked'] = unlocked
    except:
        pass


load_game()

# скины
skins = [
    {'name': 'Knight', 'img': 'player.png', 'cost': 0, 'unlocked': True},
    {'name': 'Mage', 'img': 'player_mage.png', 'cost': 100, 'unlocked': False},
    {'name': 'Archer', 'img': 'player_archer.png', 'cost': 200, 'unlocked': False},
    {'name': 'Berserk', 'img': 'player_berserk.png', 'cost': 500, 'unlocked': False},
]
current_skin = 0
in_skins = False
skin_selected = 0


def save_skins():
    with open('skins.txt', 'w') as f:
        f.write(','.join(['1' if s['unlocked'] else '0' for s in skins]))


for s in skins:
    s['image'] = load_img(s['img'], (30, 30)) or player_img

# магазин
shop_items = [
    {'name': 'Heal 50 HP', 'cost': 30, 'effect': 'heal', 'bought': 0},
    {'name': '+5 Max HP', 'cost': 50, 'effect': 'max_hp', 'bought': 0},
    {'name': '+1 Speed', 'cost': 40, 'effect': 'speed', 'bought': 0},
    {'name': '+10 Damage', 'cost': 60, 'effect': 'damage', 'bought': 0},
    {'name': 'Faster Attack', 'cost': 45, 'effect': 'attack_speed', 'bought': 0},
    {'name': 'Ultimate Skill', 'cost': 300, 'effect': 'skill_e', 'bought': 0},
    {'name': 'Crossbow', 'cost': 150, 'effect': 'weapon_crossbow', 'bought': 0},
    {'name': 'Musket', 'cost': 250, 'effect': 'weapon_musket', 'bought': 0},
]
shop_selected = 0


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

    enemy_type = random.choices(['normal', 'fast', 'tank', 'shooter'], weights=[45, 25, 20, 10], k=1)[0]
    wave_bonus = min(wave, 20)
    hp_mult = 1 + wave_bonus * 0.3
    spd_mult = 1 + wave_bonus * 0.05

    if enemy_type == 'normal':
        hp = int(random.randint(20, 30) * hp_mult);
        speed = random.uniform(2, 3) * spd_mult
    elif enemy_type == 'fast':
        hp = int(15 * hp_mult);
        speed = random.uniform(4, 5) * spd_mult
    elif enemy_type == 'tank':
        hp = int(80 * hp_mult);
        speed = random.uniform(1, 1.5) * spd_mult
    else:
        hp = int(25 * hp_mult);
        speed = 1.5 * spd_mult

    enemies.append([ex, ey, hp, hp, speed, enemy_type, 0])


def spawn_boss():
    global boss, boss_spawned
    boss = [camera_x + WIDTH // 2, camera_y - 50, 500, 500, 1.5]
    boss_spawned = True


def get_level_up_choices():
    choices = [
        {'name': '+20 Max HP', 'effect': 'max_hp', 'value': 20},
        {'name': '+Speed', 'effect': 'speed', 'value': 1},
        {'name': '+Attack Speed', 'effect': 'attack_speed', 'value': -5},
        {'name': '+Damage', 'effect': 'damage', 'value': 10},
        {'name': '+Bullet Speed', 'effect': 'bullet_speed', 'value': 2},
        {'name': 'Heal 30 HP', 'effect': 'heal', 'value': 30},
    ]
    return random.sample(choices, 3)


def apply_choice(choice):
    global player_max_hp, player_hp, player_speed, skill_e_unlocked
    w = weapons[weapon_type]
    if choice['effect'] == 'max_hp':
        player_max_hp += choice['value']; player_hp = min(player_hp + choice['value'], player_max_hp)
    elif choice['effect'] == 'speed':
        player_speed += choice['value']
    elif choice['effect'] == 'attack_speed':
        w['speed'] = max(5, w['speed'] + choice['value'])
    elif choice['effect'] == 'damage':
        w['damage'] += choice['value']
    elif choice['effect'] == 'bullet_speed':
        w['bullet_speed'] += choice['value']
    elif choice['effect'] == 'heal':
        player_hp = min(player_hp + choice['value'], player_max_hp)
    elif choice['effect'] == 'skill_e':
        skill_e_unlocked = True
    elif choice['effect'] == 'weapon_crossbow' and 'crossbow' not in weapon_keys:
        weapon_keys.append('crossbow')
    elif choice['effect'] == 'weapon_musket' and 'musket' not in weapon_keys:
        weapon_keys.append('musket')


def use_skill_q():
    global skill_q_timer, fireball_active, fireball_timer, rage_active, rage_timer, player_shield, shield_skill_timer
    skin = skins[current_skin]['name']
    if skin == 'Knight':
        player_shield += 20; shield_skill_timer = 7200
    elif skin == 'Mage':
        fireball_active = True; fireball_timer = 60
    elif skin == 'Archer':
        for _ in range(15):
            if enemies:
                target = random.choice(enemies);
                target[2] -= 20
                if target[2] <= 0: enemies.remove(target)
    elif skin == 'Berserk':
        rage_active = True; rage_timer = 120
    skill_q_timer = 1200


def use_skill_e():
    global skill_e_timer, freeze_active, freeze_timer, player_shield
    skin = skins[current_skin]['name']
    if skin == 'Knight':
        player_shield += 999
    elif skin == 'Mage':
        freeze_active = True; freeze_timer = 180
    elif skin == 'Archer':
        for e in enemies[:]: e[2] -= 50
        enemies[:] = [e for e in enemies if e[2] > 0]
    elif skin == 'Berserk':
        for _ in range(5):
            if enemies:
                target = random.choice(enemies);
                target[2] -= 100
                if target[2] <= 0: enemies.remove(target)
    skill_e_timer = 3600


def reset_game():
    global player_x, player_y, player_hp, player_max_hp, player_speed
    global xp, level, xp_to_level, choosing
    global wave, enemies_in_wave, enemies_spawned, enemies_killed_wave, total_kills
    global spawn_timer, wave_delay, boss, boss_spawned, enemies_to_boss
    global player_shield, paused, weapon_type, weapon_index, weapon_keys
    global in_menu, game_over, in_shop, in_weapon_select
    global skill_q_timer, skill_e_timer, fireball_active, freeze_active, rage_active
    global game_coins, shield_skill_timer, floor_img

    player_x, player_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
    player_hp = 100;
    player_max_hp = 100;
    player_speed = 4;
    player_shield = 0
    paused = False;
    game_coins = 0
    weapon_keys = ['sword', 'bow'];
    weapon_type = 'sword';
    weapon_index = 0
    in_weapon_select = True
    xp = 0;
    level = 1;
    xp_to_level = 50
    wave = 1;
    enemies_in_wave = 5;
    enemies_spawned = 0;
    enemies_killed_wave = 0;
    total_kills = 0
    spawn_timer = 0;
    wave_delay = 0;
    boss = None;
    boss_spawned = False;
    enemies_to_boss = 100
    choosing = False;
    in_menu = False;
    game_over = False;
    in_shop = False
    skill_q_timer = 0;
    skill_e_timer = 0;
    shield_skill_timer = 0
    fireball_active = False;
    freeze_active = False;
    rage_active = False
    enemies.clear();
    bullets.clear();
    enemy_bullets.clear();
    coins.clear();
    heals.clear();
    chests.clear()
    if floor_imgs:
        floor_img = random.choice(floor_imgs)
    if decoration_imgs:
        generate_decorations()


# сеть
def start_server():
    global server_socket, is_host, lobby_message
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 5555));
        server_socket.listen(1);
        server_socket.settimeout(0.1)
        is_host = True;
        lobby_message = 'Waiting...'
        threading.Thread(target=accept_client, daemon=True).start()
    except:
        lobby_message = 'Server error'


def accept_client():
    global client_socket, network_player2
    try:
        client_socket, addr = server_socket.accept()
        network_player2 = {'x': MAP_WIDTH // 2, 'y': MAP_HEIGHT // 2, 'hp': 100}
        threading.Thread(target=network_listener, daemon=True).start()
    except:
        pass


def connect_to_server(ip):
    global client_socket, is_client, lobby_message, network_player2
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, 5555));
        is_client = True
        network_player2 = {'x': MAP_WIDTH // 2, 'y': MAP_HEIGHT // 2, 'hp': 100}
        lobby_message = 'Connected!'
        threading.Thread(target=network_listener, daemon=True).start()
    except:
        lobby_message = 'Connection failed'


def network_listener():
    while client_socket:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                global network_player2
                network_player2 = json.loads(data)
        except:
            break


def send_network_data():
    data = json.dumps({'x': player_x, 'y': player_y, 'hp': player_hp})
    try:
        if is_host and client_socket:
            client_socket.send(data.encode())
        elif is_client and client_socket:
            client_socket.send(data.encode())
    except:
        pass


# главный цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game();
            pygame.quit();
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            if paused:
                resume_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 30, 160, 40)
                menu_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 20, 160, 40)
                if resume_btn.collidepoint(mx, my): paused = False
                if menu_btn.collidepoint(mx, my): paused = False; in_menu = True; game_over = False
            elif in_menu:
                start_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 70, 160, 40)
                skins_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 20, 160, 40)
                lobby_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 30, 160, 40)
                settings_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 80, 160, 40)
                lang_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 130, 160, 40)
                exit_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 180, 160, 40)
                if start_btn.collidepoint(mx, my): reset_game()
                if skins_btn.collidepoint(mx, my): in_skins = True; in_menu = False; skin_selected = current_skin
                if lobby_btn.collidepoint(mx, my): in_lobby = True; in_menu = False
                if settings_btn.collidepoint(mx, my): in_settings = True; in_menu = False
                if lang_btn.collidepoint(mx, my): lang = 'ru' if lang == 'en' else 'en'; save_game()
                if exit_btn.collidepoint(mx, my): save_game(); pygame.quit(); sys.exit()
            elif in_lobby:
                host_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 30, 160, 35)
                join_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 15, 160, 35)
                back_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 60, 160, 35)
                if host_btn.collidepoint(mx, my): start_server()
                if join_btn.collidepoint(mx, my): connect_to_server('127.0.0.1')
                if back_btn.collidepoint(mx, my): in_lobby = False; in_menu = True
            elif in_settings:
                back_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 100, 160, 35)
                vol_up = pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 - 10, 30, 30)
                vol_down = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 10, 30, 30)
                if back_btn.collidepoint(mx, my): in_settings = False; in_menu = True
                if vol_up.collidepoint(mx, my): sound_volume = min(1.0, sound_volume + 0.1)
                if vol_down.collidepoint(mx, my): sound_volume = max(0.0, sound_volume - 0.1)
            elif in_weapon_select:
                sword_btn = pygame.Rect(WIDTH // 2 - 200, 350, 160, 60)
                bow_btn = pygame.Rect(WIDTH // 2 + 40, 350, 160, 60)
                if sword_btn.collidepoint(mx, my):
                    weapon_type = 'sword';
                    weapon_index = 0
                    in_weapon_select = False
                if bow_btn.collidepoint(mx, my):
                    weapon_type = 'bow';
                    weapon_index = 1
                    in_weapon_select = False
        if event.type == pygame.KEYDOWN:
            # ESC в меню = выход (ПРОВЕРЯЕТСЯ ПЕРВЫМ)
            if event.key == pygame.K_ESCAPE and in_menu:
                save_game();
                pygame.quit();
                sys.exit()

            if in_skins:
                if event.key == pygame.K_UP and skin_selected > 0: skin_selected -= 1
                if event.key == pygame.K_DOWN and skin_selected < len(skins) - 1: skin_selected += 1
                if event.key == pygame.K_RETURN:
                    s = skins[skin_selected]
                    if s['unlocked']:
                        current_skin = skin_selected
                    elif total_coins >= s['cost']:
                        s['unlocked'] = True;
                        total_coins -= s['cost']
                        current_skin = skin_selected;
                        save_skins();
                        save_game()
                if event.key == pygame.K_ESCAPE: in_skins = False; in_menu = True

            if in_shop:
                if event.key == pygame.K_UP: shop_selected = (shop_selected - 1) % len(shop_items)
                if event.key == pygame.K_DOWN: shop_selected = (shop_selected + 1) % len(shop_items)
                if event.key == pygame.K_RETURN:
                    item = shop_items[shop_selected]
                    cost = item['cost'] + item['bought'] * 20
                    if total_coins >= cost: total_coins -= cost; apply_choice(item); item['bought'] += 1; save_game()
                if event.key == pygame.K_SPACE: in_shop = False

            if event.key == pygame.K_SPACE and (in_menu or game_over):
                reset_game()

            # ESC в игре = пауза
            if event.key == pygame.K_ESCAPE and not in_menu and not game_over and not in_shop and not in_skins:
                paused = not paused

            if event.key == pygame.K_p and not in_menu and not game_over: paused = not paused
            if event.key == pygame.K_TAB and not in_menu and not game_over and not in_weapon_select:
                weapon_index = (weapon_index + 1) % len(weapon_keys);
                weapon_type = weapon_keys[weapon_index]
            if event.key == pygame.K_q and not in_menu and not game_over and skill_q_timer <= 0:
                if skins[current_skin]['name'] == 'Knight' and shield_skill_timer > 0:
                    pass
                else:
                    use_skill_q()
            if event.key == pygame.K_e and not in_menu and not game_over and skill_e_timer <= 0 and skill_e_unlocked: use_skill_e()
            if event.key == pygame.K_r and not in_menu and not game_over: auto_aim = not auto_aim
            if event.key == pygame.K_l and in_menu: lang = 'ru' if lang == 'en' else 'en'; save_game()
            if choosing:
                if event.key == pygame.K_1 and len(level_up_choices) >= 1: apply_choice(
                    level_up_choices[0]); choosing = False
                if event.key == pygame.K_2 and len(level_up_choices) >= 2: apply_choice(
                    level_up_choices[1]); choosing = False
                if event.key == pygame.K_3 and len(level_up_choices) >= 3: apply_choice(
                    level_up_choices[2]); choosing = False

    # выбор оружия
    if in_weapon_select:
        screen.fill(BLACK)
        screen.blit(big_font.render(t('weapon_select'), True, YELLOW),
                    big_font.render(t('weapon_select'), True, YELLOW).get_rect(center=(WIDTH // 2, 200)))
        sword_btn = pygame.Rect(WIDTH // 2 - 200, 350, 160, 60)
        bow_btn = pygame.Rect(WIDTH // 2 + 40, 350, 160, 60)
        pygame.draw.rect(screen, (60, 60, 80), sword_btn);
        pygame.draw.rect(screen, WHITE, sword_btn, 2)
        pygame.draw.rect(screen, (60, 60, 80), bow_btn);
        pygame.draw.rect(screen, WHITE, bow_btn, 2)
        if weapon_icons.get('sword'): screen.blit(weapon_icons['sword'], (WIDTH // 2 - 185, 365))
        if weapon_icons.get('bow'): screen.blit(weapon_icons['bow'], (WIDTH // 2 + 55, 365))
        screen.blit(font.render('Click to choose', True, GRAY),
                    font.render('Click to choose', True, GRAY).get_rect(center=(WIDTH // 2, 450)))
        pygame.display.flip();
        clock.tick(60);
        continue

    # скины
    if in_skins:
        screen.fill(BLACK)
        screen.blit(font.render('SKINS', True, YELLOW),
                    font.render('SKINS', True, YELLOW).get_rect(center=(WIDTH // 2, 60)))
        for i, s in enumerate(skins):
            color = WHITE if i == skin_selected else GRAY
            txt = f"{s['name']} - {s['cost']} coins" if not s['unlocked'] else f"{s['name']} - OWNED"
            screen.blit(font.render(txt, True, color), (WIDTH // 2 - 80, 120 + i * 40))
        screen.blit(small_font.render('ESC - back', True, GRAY), (WIDTH // 2 - 40, HEIGHT - 50))
        pygame.display.flip();
        clock.tick(60);
        continue

    # лобби
    if in_lobby:
        if lobby_bg_img:
            screen.blit(lobby_bg_img, (0, 0))
        else:
            screen.fill(BLACK)
        screen.blit(big_font.render(t('lobby'), True, YELLOW),
                    big_font.render(t('lobby'), True, YELLOW).get_rect(center=(WIDTH // 2, 80)))
        for i, (txt, y) in enumerate([(t('host'), 0), (t('join'), 50), (t('back'), 100)]):
            btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 30 + y, 160, 35)
            pygame.draw.rect(screen, (60, 60, 80), btn);
            pygame.draw.rect(screen, WHITE, btn, 2)
            screen.blit(font.render(txt, True, WHITE), font.render(txt, True, WHITE).get_rect(center=btn.center))
        if lobby_message:
            screen.blit(font.render(lobby_message, True, YELLOW), (WIDTH // 2 - 80, HEIGHT // 2 + 130))
        pygame.display.flip();
        clock.tick(60);
        continue

    # настройки
    if in_settings:
        screen.fill(BLACK)
        screen.blit(big_font.render(t('settings'), True, YELLOW),
                    big_font.render(t('settings'), True, YELLOW).get_rect(center=(WIDTH // 2, 80)))
        screen.blit(font.render(f"{t('sound')}: {int(sound_volume * 100)}%", True, WHITE),
                    (WIDTH // 2 - 80, HEIGHT // 2 - 40))
        vol_down = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 10, 30, 30)
        vol_up = pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 - 10, 30, 30)
        pygame.draw.rect(screen, (60, 60, 80), vol_down);
        pygame.draw.rect(screen, WHITE, vol_down, 2)
        screen.blit(font.render('-', True, WHITE), font.render('-', True, WHITE).get_rect(center=vol_down.center))
        pygame.draw.rect(screen, (60, 60, 80), vol_up);
        pygame.draw.rect(screen, WHITE, vol_up, 2)
        screen.blit(font.render('+', True, WHITE), font.render('+', True, WHITE).get_rect(center=vol_up.center))
        back_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 100, 160, 35)
        pygame.draw.rect(screen, (60, 60, 80), back_btn);
        pygame.draw.rect(screen, WHITE, back_btn, 2)
        screen.blit(font.render(t('back'), True, WHITE),
                    font.render(t('back'), True, WHITE).get_rect(center=back_btn.center))
        pygame.display.flip();
        clock.tick(60);
        continue

    # меню
    if in_menu:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(BLACK)
        screen.blit(big_font.render(t('title'), True, YELLOW),
                    big_font.render(t('title'), True, YELLOW).get_rect(center=(WIDTH // 2, 200)))
        buttons = [
            (t('start'), -70), ('SKINS', -20), (t('lobby'), 30), (t('settings'), 80), (lang.upper(), 130),
            (t('exit'), 180)
        ]
        for txt, y in buttons:
            btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + y, 160, 40)
            pygame.draw.rect(screen, (60, 60, 80), btn);
            pygame.draw.rect(screen, WHITE, btn, 2)
            screen.blit(font.render(txt, True, WHITE), font.render(txt, True, WHITE).get_rect(center=btn.center))
        prof_text = small_font.render(f"Profile LVL: {profile_level} | Coins: {total_coins}", True, GRAY)
        screen.blit(prof_text, (10, HEIGHT - 25))
        pygame.display.flip();
        clock.tick(60);
        continue

    # магазин
    if in_shop:
        screen.fill(BLACK)
        screen.blit(big_font.render(t('shop'), True, YELLOW),
                    big_font.render(t('shop'), True, YELLOW).get_rect(center=(WIDTH // 2, 60)))
        screen.blit(font.render(f"{t('coins')}: {total_coins}", True, WHITE), (WIDTH // 2 - 60, 100))
        for i, item in enumerate(shop_items):
            cost = item['cost'] + item['bought'] * 20
            color = WHITE if i == shop_selected else GRAY
            if total_coins < cost: color = RED
            screen.blit(font.render(f"{item['name']} - {cost} coins", True, color), (WIDTH // 2 - 100, 140 + i * 40))
        screen.blit(small_font.render('ARROWS/ENTER - buy | SPACE - leave', True, GRAY),
                    (WIDTH // 2 - 120, HEIGHT - 40))
        pygame.display.flip();
        clock.tick(60);
        continue

    # игра
    if not game_over and not choosing and not in_shop and not paused and not in_weapon_select:
        w = weapons[weapon_type]
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if dx != 0 and dy != 0: dx *= 0.707; dy *= 0.707

        player_x += dx * player_speed;
        player_y += dy * player_speed
        player_x = max(player_radius, min(MAP_WIDTH - player_radius, player_x))
        player_y = max(player_radius, min(MAP_HEIGHT - player_radius, player_y))
        camera_x = player_x - WIDTH // 2;
        camera_y = player_y - HEIGHT // 2
        camera_x = max(0, min(MAP_WIDTH - WIDTH, camera_x))
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, camera_y))

        attack_cooldown -= 1
        if weapon_type in ['sword', 'axe']:
            if attack_cooldown <= 0 and (enemies or boss):
                attack_cooldown = w['speed']
                for e in enemies[:]:
                    if abs(e[0] - player_x) < 60 and abs(e[1] - player_y) < 60:
                        e[2] -= w['damage']
                        if e[2] <= 0:
                            enemies.remove(e);
                            xp += 10;
                            enemies_killed_wave += 1;
                            total_kills += 1
                            game_coins += random.randint(1, 3);
                            profile_xp += 5
                            if random.random() < 0.5: coins.append([e[0], e[1]])
                            if random.random() < 0.12: heals.append([e[0], e[1]])
                            if total_kills >= enemies_to_boss and not boss_spawned: spawn_boss()
                if boss and abs(boss[0] - player_x) < 60 and abs(boss[1] - player_y) < 60:
                    boss[2] -= w['damage']
                    if boss[2] <= 0:
                        boss = None;
                        boss_spawned = False;
                        total_kills = 0;
                        xp += 200
                        game_coins += 50;
                        total_coins += 100;
                        profile_xp += 50
                        enemies_to_boss += 50;
                        in_shop = True;
                        save_game()
        else:
            if (enemies or boss) and attack_cooldown <= 0:
                if auto_aim and enemies:
                    target = min(enemies, key=lambda e: ((e[0] - player_x) ** 2 + (e[1] - player_y) ** 2) ** 0.5)
                    wx, wy = target[0], target[1]
                else:
                    mx, my = pygame.mouse.get_pos()
                    wx, wy = mx + camera_x, my + camera_y
                edx, edy = wx - player_x, wy - player_y
                dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
                bullets.append(
                    [player_x, player_y, edx / dist * w['bullet_speed'], edy / dist * w['bullet_speed'], weapon_type])
                attack_cooldown = w['speed']
                if shoot_sound: shoot_sound.play()

        for b in bullets[:]:
            b[0] += b[2];
            b[1] += b[3]
            if b[0] < 0 or b[0] > MAP_WIDTH or b[1] < 0 or b[1] > MAP_HEIGHT: bullets.remove(b)
        if len(bullets) > 80: bullets = bullets[-40:]

        for b in enemy_bullets[:]:
            b[0] += b[2];
            b[1] += b[3]
            if b[0] < 0 or b[0] > MAP_WIDTH or b[1] < 0 or b[1] > MAP_HEIGHT:
                enemy_bullets.remove(b)
            elif abs(b[0] - player_x) < 15 and abs(b[1] - player_y) < 15:
                enemy_bullets.remove(b)
                if player_shield > 0:
                    player_shield -= 1
                else:
                    player_hp -= 10
                if player_hp <= 0: game_over = True

        if not boss_spawned:
            if wave_delay > 0:
                wave_delay -= 1
            elif enemies_spawned < enemies_in_wave:
                spawn_timer += 1
                if spawn_timer > max(20, 60 - level * 2): spawn_timer = 0; spawn_enemy(); enemies_spawned += 1
            elif len(enemies) == 0 and not boss:
                wave += 1;
                enemies_in_wave = 5 + wave * 2;
                enemies_spawned = 0;
                enemies_killed_wave = 0;
                wave_delay = 60

        if random.randint(0, 3600) < 1 and not boss_spawned:
            chests.append([random.randint(100, MAP_WIDTH - 100), random.randint(100, MAP_HEIGHT - 100)])

        for e in enemies[:]:
            if not freeze_active:
                edx, edy = player_x - e[0], player_y - e[1]
                dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
                e[0] += edx / dist * e[4];
                e[1] += edy / dist * e[4]
            if abs(e[0] - player_x) < 20 and abs(e[1] - player_y) < 20:
                if len(e) > 5 and e[5] == 'shooter':
                    e[6] += 1
                    if e[6] > 60:
                        e[6] = 0
                        edx, edy = player_x - e[0], player_y - e[1]
                        dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
                        enemy_bullets.append([e[0], e[1], edx / dist * 4, edy / dist * 4])
                if player_shield > 0:
                    player_shield -= 1
                else:
                    player_hp -= 1
                if player_hp <= 0: game_over = True

        if boss:
            if not freeze_active:
                edx, edy = player_x - boss[0], player_y - boss[1]
                dist = max(1, (edx ** 2 + edy ** 2) ** 0.5)
                boss[0] += edx / dist * boss[4];
                boss[1] += edy / dist * boss[4]
            if abs(boss[0] - player_x) < 30 and abs(boss[1] - player_y) < 30:
                if player_shield > 0:
                    dmg = min(3, player_shield);
                    player_shield -= dmg
                    if 3 - dmg > 0: player_hp -= (3 - dmg)
                else:
                    player_hp -= 3
                if player_hp <= 0: game_over = True

        for b in bullets[:]:
            for e in enemies[:]:
                if abs(b[0] - e[0]) < 15 and abs(b[1] - e[1]) < 15:
                    if b in bullets: bullets.remove(b)
                    e[2] -= w['damage']
                    if e[2] <= 0:
                        if e in enemies:
                            enemies.remove(e);
                            xp += 10;
                            enemies_killed_wave += 1;
                            total_kills += 1
                            game_coins += random.randint(1, 3);
                            profile_xp += 5
                            if random.random() < 0.5: coins.append([e[0], e[1]])
                            if random.random() < 0.12: heals.append([e[0], e[1]])
                            if total_kills >= enemies_to_boss and not boss_spawned: spawn_boss()
                    break

        if boss:
            for b in bullets[:]:
                if abs(b[0] - boss[0]) < 40 and abs(b[1] - boss[1]) < 40:
                    if b in bullets: bullets.remove(b)
                    boss[2] -= w['damage']
                    if boss[2] <= 0:
                        boss = None;
                        boss_spawned = False;
                        total_kills = 0;
                        xp += 200
                        game_coins += 50;
                        total_coins += 100;
                        profile_xp += 50
                        # выпадение оружия с босса (только то, которого ещё нет)
                        possible_weapons = []
                        if 'bow' not in weapon_keys: possible_weapons.append('bow')
                        if 'crossbow' not in weapon_keys: possible_weapons.append('crossbow')
                        if 'musket' not in weapon_keys: possible_weapons.append('musket')
                        if possible_weapons and random.random() < 0.5:
                            new_weapon = random.choice(possible_weapons)
                            weapon_keys.append(new_weapon)
                        enemies_to_boss += 50;
                        in_shop = True;
                        save_game()
                    break

        for c in coins[:]:
            if abs(c[0] - player_x) < 25 and abs(c[1] - player_y) < 25: coins.remove(c); game_coins += 1
        for h in heals[:]:
            if abs(h[0] - player_x) < 25 and abs(h[1] - player_y) < 25: heals.remove(h); player_hp = min(player_hp + 15,
                                                                                                         player_max_hp)
        for ch in chests[:]:
            if abs(ch[0] - player_x) < 35 and abs(ch[1] - player_y) < 35:
                chests.remove(ch);
                player_shield += 10
                for _ in range(5): coins.append([ch[0] + random.randint(-20, 20), ch[1] + random.randint(-20, 20)])

        if skill_q_timer > 0: skill_q_timer -= 1
        if skill_e_timer > 0: skill_e_timer -= 1
        if shield_skill_timer > 0: shield_skill_timer -= 1
        if fireball_active:
            fireball_timer -= 1
            for e in enemies[:]:
                if abs(e[0] - player_x) < 100 and abs(e[1] - player_y) < 100:
                    e[2] -= 2
                    if e[2] <= 0: enemies.remove(e); profile_xp += 3
            if fireball_timer <= 0: fireball_active = False
        if freeze_active:
            freeze_timer -= 1
            if freeze_timer <= 0: freeze_active = False
        if rage_active:
            rage_timer -= 1
            if rage_timer <= 0: rage_active = False

        # профиль
        if profile_xp >= profile_xp_to_next:
            profile_level += 1
            profile_xp -= profile_xp_to_next
            profile_xp_to_next = int(profile_xp_to_next * 1.5)
            total_coins += 50
            save_game()

        if xp >= xp_to_level:
            level += 1;
            xp -= xp_to_level;
            xp_to_level = int(xp_to_level * 1.5)
            if level % 10 == 0: level_up_choices = get_level_up_choices(); choosing = True

        if is_host or is_client: send_network_data()

    # рисовка
    if floor_img:
        for fx in range(int(camera_x // 64) * 64 - 64, int(camera_x) + WIDTH + 64, 64):
            for fy in range(int(camera_y // 64) * 64 - 64, int(camera_y) + HEIGHT + 64, 64):
                if 0 <= fx < MAP_WIDTH and 0 <= fy < MAP_HEIGHT:
                    screen.blit(floor_img, (fx - camera_x, fy - camera_y))
    else:
        screen.fill(GRAY)

    # декорации
    for d in decorations:
        sx, sy = d[0] - camera_x, d[1] - camera_y
        if -60 < sx < WIDTH + 60 and -60 < sy < HEIGHT + 60:
            if decoration_imgs:
                screen.blit(decoration_imgs[d[2]], (sx - 20, sy - 20))

    # панель интерфейса
    panel = pygame.Rect(5, 5, 180, 120)
    pygame.draw.rect(screen, (0, 0, 0, 180), panel);
    pygame.draw.rect(screen, (80, 80, 100), panel, 2)
    screen.blit(font.render(f"{t('lvl')}: {level}", True, WHITE), (10, 8))
    screen.blit(font.render(f"Coins: {game_coins}", True, YELLOW), (10, 30))
    screen.blit(font.render(f"{t('wave')}: {wave}", True, ORANGE), (10, 52))
    if player_shield > 0: screen.blit(font.render(f'Shield: {player_shield}', True, (100, 150, 255)), (10, 74))
    screen.blit(small_font.render(f"[Q] {'OK' if skill_q_timer <= 0 else skill_q_timer // 60 + 1}s", True, YELLOW),
                (10, 94))
    if skill_e_unlocked:
        screen.blit(small_font.render(f"[E] {'OK' if skill_e_timer <= 0 else skill_e_timer // 60 + 1}s", True, ORANGE),
                    (10, 108))

    # оружие справа
    wp = pygame.Rect(WIDTH - 130, 5, 125, 50)
    pygame.draw.rect(screen, (0, 0, 0, 180), wp);
    pygame.draw.rect(screen, (80, 80, 100), wp, 2)
    screen.blit(small_font.render(f"{w['name']} [TAB]", True, WHITE), (WIDTH - 125, 8))
    aim_text = 'AUTO' if auto_aim else 'MOUSE'
    screen.blit(small_font.render(f'[R] {aim_text}', True, GRAY), (WIDTH - 125, 28))

    # объекты
    for c in coins:
        sx, sy = c[0] - camera_x, c[1] - camera_y
        if -30 < sx < WIDTH + 30 and -30 < sy < HEIGHT + 30:
            if coin_img:
                screen.blit(coin_img, (sx - 7, sy - 7))
            else:
                pygame.draw.circle(screen, YELLOW, (sx, sy), 5)
    for h in heals:
        sx, sy = h[0] - camera_x, h[1] - camera_y
        if -30 < sx < WIDTH + 30 and -30 < sy < HEIGHT + 30:
            if heal_img:
                screen.blit(heal_img, (sx - 10, sy - 10))
            else:
                pygame.draw.circle(screen, (255, 100, 100), (sx, sy), 7)
    for ch in chests:
        sx, sy = ch[0] - camera_x, ch[1] - camera_y
        if -30 < sx < WIDTH + 30 and -30 < sy < HEIGHT + 30:
            if chest_img:
                screen.blit(chest_img, (sx - 15, sy - 15))
            else:
                pygame.draw.rect(screen, (139, 90, 40), (sx - 15, sy - 15, 30, 30))

    for e in enemies:
        sx, sy = e[0] - camera_x, e[1] - camera_y
        if -40 < sx < WIDTH + 40 and -40 < sy < HEIGHT + 40:
            enemy_type = e[5] if len(e) > 5 else 'normal'
            if enemy_imgs.get(enemy_type):
                screen.blit(enemy_imgs[enemy_type], (sx - 12, sy - 12))
            else:
                ec = RED
                if enemy_type == 'fast':
                    ec = ORANGE
                elif enemy_type == 'tank':
                    ec = (150, 30, 30)
                elif enemy_type == 'shooter':
                    ec = PURPLE
                pygame.draw.circle(screen, ec, (sx, sy), 12)
            bar_w, bar_h = 30, 4;
            bx, by = sx - bar_w // 2, sy - 18
            pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
            pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (e[2] / e[3]), bar_h))
            pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    if boss:
        sx, sy = boss[0] - camera_x, boss[1] - camera_y
        if boss_img:
            screen.blit(boss_img, (sx - 35, sy - 35))
        else:
            pygame.draw.circle(screen, PURPLE, (sx, sy), 35)
        bar_w, bar_h = 70, 6;
        bx, by = sx - bar_w // 2, sy - 45
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (boss[2] / boss[3]), bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    for b in bullets:
        sx, sy = b[0] - camera_x, b[1] - camera_y
        bw = weapons.get(b[4], weapons['bow'])
        if b[4] == 'bow' and arrow_img:
            screen.blit(arrow_img, (sx - 5, sy - 2))
        elif b[4] == 'crossbow' and bolt_img:
            screen.blit(bolt_img, (sx - 4, sy - 2))
        elif b[4] == 'musket' and musket_ball_img:
            screen.blit(musket_ball_img, (sx - 3, sy - 3))
        else:
            pygame.draw.circle(screen, YELLOW, (sx, sy), 3)
    for b in enemy_bullets:
        sx, sy = b[0] - camera_x, b[1] - camera_y
        pygame.draw.circle(screen, PURPLE, (sx, sy), 5)

    # второй игрок
    if network_player2:
        sx, sy = network_player2['x'] - camera_x, network_player2['y'] - camera_y
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            pygame.draw.circle(screen, GREEN, (sx, sy), player_radius)

    if not game_over:
        sx, sy = player_x - camera_x, player_y - camera_y
        skin_img = skins[current_skin].get('image', player_img)
        if skin_img:
            screen.blit(skin_img, (sx - 15, sy - 15))
        else:
            pygame.draw.circle(screen, BLUE, (sx, sy), player_radius)
        if weapon_icons.get(weapon_type):
            screen.blit(weapon_icons[weapon_type], (sx + 5, sy - 20))
        bar_w, bar_h = 40, 5;
        bx, by = sx - bar_w // 2, sy - player_radius - 10
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (player_hp / player_max_hp), bar_h))

    if wave_delay > 0:
        wv = big_font.render(f"{t('wave')} {wave}", True, YELLOW)
        screen.blit(wv, wv.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    if paused:
        dark = pygame.Surface((WIDTH, HEIGHT));
        dark.set_alpha(150);
        dark.fill(BLACK);
        screen.blit(dark, (0, 0))
        screen.blit(big_font.render(t('pause'), True, YELLOW),
                    big_font.render(t('pause'), True, YELLOW).get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
        resume_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 30, 160, 40)
        menu_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 20, 160, 40)
        pygame.draw.rect(screen, (60, 60, 80), resume_btn);
        pygame.draw.rect(screen, WHITE, resume_btn, 2)
        screen.blit(font.render(t('resume'), True, WHITE),
                    font.render(t('resume'), True, WHITE).get_rect(center=resume_btn.center))
        pygame.draw.rect(screen, (60, 60, 80), menu_btn);
        pygame.draw.rect(screen, WHITE, menu_btn, 2)
        screen.blit(font.render(t('menu_btn'), True, WHITE),
                    font.render(t('menu_btn'), True, WHITE).get_rect(center=menu_btn.center))

    # профиль в игре
    prof_text = small_font.render(f"Prof: {profile_level} | {profile_xp}/{profile_xp_to_next}", True, GRAY)
    screen.blit(prof_text, (WIDTH - 200, HEIGHT - 20))

    if choosing:
        dark = pygame.Surface((WIDTH, HEIGHT));
        dark.set_alpha(180);
        dark.fill(BLACK);
        screen.blit(dark, (0, 0))
        screen.blit(big_font.render(t('choose'), True, YELLOW),
                    big_font.render(t('choose'), True, YELLOW).get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
        for i, c in enumerate(level_up_choices):
            screen.blit(font.render(f"[{i + 1}] {c['name']}", True, WHITE),
                        font.render(f"[{i + 1}] {c['name']}", True, WHITE).get_rect(
                            center=(WIDTH // 2, HEIGHT // 2 + i * 40)))

    if game_over:
        screen.blit(big_font.render(t('game_over'), True, RED),
                    big_font.render(t('game_over'), True, RED).get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        screen.blit(font.render(t('restart'), True, GRAY),
                    font.render(t('restart'), True, GRAY).get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        total_coins += game_coins;
        save_game()

    pygame.display.flip()
    clock.tick(60)
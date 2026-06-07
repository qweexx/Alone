import pygame
import sys
import random
import socket
import threading
import json

pygame.init()

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
zoom = 1.0
auto_aim = False

# текстуры для игры
try:
    player_img = pygame.image.load('images/player.png')
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
    arrow_img = pygame.transform.scale(pygame.image.load('images/arrow.png'), (10, 4))
except:
    arrow_img = None
try:
    bolt_img = pygame.transform.scale(pygame.image.load('images/bolt.png'), (8, 4))
except:
    bolt_img = None
try:
    musket_ball_img = pygame.transform.scale(pygame.image.load('images/musket_ball.png'), (6, 6))
except:
    musket_ball_img = None
try:
    coin_img = pygame.transform.scale(pygame.image.load('images/coin.png'), (14, 14))
except:
    coin_img = None
try:
    heal_img = pygame.transform.scale(pygame.image.load('images/heal.png'), (20, 20))
except:
    heal_img = None

# Локации
floor_imgs = []
try:
    floor_imgs.append(pygame.transform.scale(pygame.image.load('images/floor.png'), (64, 64)))
    floor_imgs.append(pygame.transform.scale(pygame.image.load('images/floor2.png'), (64, 64)))
    floor_imgs.append(pygame.transform.scale(pygame.image.load('images/floor3.png'), (64, 64)))
except:
    pass
floor_img = random.choice(floor_imgs) if floor_imgs else None

try:
    menu_bg_img = pygame.image.load('images/menu_bg.png')
    menu_bg_img = pygame.transform.scale(menu_bg_img, (WIDTH, HEIGHT))
except:
    menu_bg_img = None
try:
    lobby_bg_img = pygame.image.load('images/lobby_bg.png')
    lobby_bg_img = pygame.transform.scale(lobby_bg_img, (WIDTH, HEIGHT))
except:
    lobby_bg_img = None
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

# Питомец
pet_img = None
try:
    pet_img = pygame.image.load('images/pet.png')
    pet_img = pygame.transform.scale(pet_img, (20, 20))
except:
    pass
pet_unlocked = False
pet_active = False
pet_x, pet_y = 0, 0

# Статуя воскрешения
revive_statue = None
revive_statue_img = None
try:
    revive_statue_img = pygame.image.load('images/statue.png')
    revive_statue_img = pygame.transform.scale(revive_statue_img, (40, 40))
except:
    pass
ally_revived = False

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

# Профиль
profile_level = 1
profile_xp = 0
profile_xp_to_next = 100

# Оружие
bullets = []
enemy_bullets = []
attack_cooldown = 0

weapon_type = 'bow'
weapons = {
    'bow': {'name': 'Bow', 'speed': 30, 'damage': 25, 'bullet_speed': 8, 'img': arrow_img, 'color': YELLOW, 'size': 4},
    'crossbow': {'name': 'Crossbow', 'speed': 45, 'damage': 45, 'bullet_speed': 10, 'img': bolt_img, 'color': ORANGE, 'size': 3},
    'musket': {'name': 'Musket', 'speed': 70, 'damage': 80, 'bullet_speed': 14, 'img': musket_ball_img, 'color': (150, 100, 50), 'size': 5},
    'sword': {'name': 'Sword', 'speed': 45, 'damage': 40, 'bullet_speed': 0, 'img': None, 'color': WHITE, 'size': 0},
    'axe': {'name': 'Axe', 'speed': 60, 'damage': 60, 'bullet_speed': 0, 'img': None, 'color': (150, 100, 50), 'size': 0},
}
weapon_keys = ['bow', 'crossbow', 'musket', 'sword', 'axe']
weapon_index = 0

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

# Навыки
skill_q_timer = 0
skill_e_timer = 0
skill_e_unlocked = False
fireball_active = False
fireball_timer = 0
freeze_active = False
freeze_timer = 0
rage_active = False
rage_timer = 0

# Магазин
shop_items = [
    {'name': 'Heal 50 HP', 'cost': 30, 'effect': 'heal', 'value': 50},
    {'name': '+5 Max HP', 'cost': 50, 'effect': 'max_hp', 'value': 5},
    {'name': '+1 Speed', 'cost': 40, 'effect': 'speed', 'value': 1},
    {'name': '+10 Damage', 'cost': 60, 'effect': 'damage', 'value': 10},
    {'name': 'Faster Attack', 'cost': 45, 'effect': 'attack_speed', 'value': -5},
    {'name': 'Ultimate Skill', 'cost': 300, 'effect': 'skill_e', 'value': 1},
    {'name': 'Pet', 'cost': 500, 'effect': 'pet', 'value': 1},
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
boss_type = 0

# Меню
in_menu = True
game_over = False
in_shop = False
paused = False
in_lobby = False
lobby_message = ''

# Сеть
network_player2 = None
network_data = {'x': MAP_WIDTH//2, 'y': MAP_HEIGHT//2, 'hp': 100}
is_host = False
is_client = False
client_socket = None
server_socket = None

# Сохранения
def save_game():
    data = {
        'total_coins': total_coins,
        'best_score': max(total_kills, get_best_score()),
        'skill_e_unlocked': skill_e_unlocked,
        'skins': [s['unlocked'] for s in skins],
        'lang': lang,
        'profile_level': profile_level,
        'profile_xp': profile_xp,
        'pet_unlocked': pet_unlocked,
    }
    try:
        with open('save.json', 'w') as f:
            json.dump(data, f)
    except:
        pass

def load_game():
    global total_coins, skill_e_unlocked, lang, profile_level, profile_xp, pet_unlocked
    try:
        with open('save.json', 'r') as f:
            data = json.load(f)
            total_coins = data.get('total_coins', 0)
            skill_e_unlocked = data.get('skill_e_unlocked', False)
            lang = data.get('lang', 'ru')
            profile_level = data.get('profile_level', 1)
            profile_xp = data.get('profile_xp', 0)
            pet_unlocked = data.get('pet_unlocked', False)
            if 'skins' in data:
                for i, unlocked in enumerate(data['skins']):
                    if i < len(skins):
                        skins[i]['unlocked'] = unlocked
    except:
        pass

def get_best_score():
    try:
        with open('save.json', 'r') as f:
            return json.load(f).get('best_score', 0)
    except:
        return 0

load_game()

# Шрифт
try:
    font = pygame.font.Font('font.ttf', 22)
    big_font = pygame.font.Font('font.ttf', 44)
    small_font = pygame.font.Font('font.ttf', 14)
except:
    font = pygame.font.Font(None, 34)
    big_font = pygame.font.Font(None, 68)
    small_font = pygame.font.Font(None, 22)

# Язык
texts = {
    'ru': {
        'title': 'ОДИН', 'start': 'ПРОБЕЛ чтобы начать', 'shop': 'МАГАЗИН',
        'coins': 'Монеты', 'choose': 'ВЫБЕРИ УЛУЧШЕНИЕ', 'wave': 'Волна',
        'boss_in': 'До босса', 'lvl': 'УР', 'game_over': 'ИГРА ОКОНЧЕНА',
        'restart': 'ПРОБЕЛ чтобы начать заново', 'up_down_buy': 'СТРЕЛКИ - выбор | ENTER - купить | ПРОБЕЛ - выход',
        'lang_hint': 'L - язык', 'resume': 'ПРОДОЛЖИТЬ (P)', 'menu_btn': 'МЕНЮ (ESC)',
        'skill_q': 'Q: Атака', 'skill_e': 'E: Ульт', 'lobby': 'ЛОББИ',
        'host': 'Создать игру', 'join': 'Подключиться', 'back': 'Назад',
        'waiting': 'Ожидание игрока...', 'connecting': 'Подключение...', 'enter_ip': 'Введите IP: ',
        'profile': 'Профиль', 'pet': 'Питомец',
    },
    'en': {
        'title': 'ALONE', 'start': 'Press SPACE to start', 'shop': 'SHOP',
        'coins': 'Coins', 'choose': 'CHOOSE UPGRADE', 'wave': 'Wave',
        'boss_in': 'Boss in', 'lvl': 'LVL', 'game_over': 'GAME OVER',
        'restart': 'Press SPACE to restart', 'up_down_buy': 'UP/DOWN - choose | ENTER - buy | SPACE - leave',
        'lang_hint': 'L - language', 'resume': 'RESUME (P)', 'menu_btn': 'MENU (ESC)',
        'skill_q': 'Q: Attack', 'skill_e': 'E: Ultimate', 'lobby': 'LOBBY',
        'host': 'Host Game', 'join': 'Join Game', 'back': 'Back',
        'waiting': 'Waiting for player...', 'connecting': 'Connecting...', 'enter_ip': 'Enter IP: ',
        'profile': 'Profile', 'pet': 'Pet',
    }
}
lang = 'ru'
def t(key):
    global lang
    return texts[lang][key]

# Скины
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
    try:
        s['image'] = pygame.image.load(f"images/{s['img']}")
        s['image'] = pygame.transform.scale(s['image'], (30, 30))
    except:
        s['image'] = player_img


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

    enemy_type = random.choices(['normal', 'fast', 'tank', 'shooter'], weights=[50, 25, 15, 10], k=1)[0]
    wave_bonus = min(wave, 20)
    hp_mult = 1 + wave_bonus * 0.3
    spd_mult = 1 + wave_bonus * 0.05

    if enemy_type == 'normal':
        hp = int(random.randint(20, 30) * hp_mult)
        speed = random.uniform(2, 3) * spd_mult
    elif enemy_type == 'fast':
        hp = int(15 * hp_mult)
        speed = random.uniform(4, 5) * spd_mult
    elif enemy_type == 'tank':
        hp = int(80 * hp_mult)
        speed = random.uniform(1, 1.5) * spd_mult
    else:
        hp = int(25 * hp_mult)
        speed = 1.5 * spd_mult

    enemies.append([ex, ey, hp, hp, speed, enemy_type, 0])


def spawn_boss():
    global boss, boss_spawned, boss_type
    boss_type = random.randint(0, 2)
    if boss_type == 0: boss = [camera_x + WIDTH//2, camera_y - 50, 500, 500, 1.5, 'normal']
    elif boss_type == 1: boss = [camera_x + WIDTH//2, camera_y - 50, 300, 300, 3, 'fast']
    else: boss = [camera_x + WIDTH//2, camera_y - 50, 800, 800, 1, 'tank']
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
    global player_max_hp, player_hp, player_speed, skill_e_unlocked, pet_unlocked
    w = weapons[weapon_type]
    if choice['effect'] == 'max_hp':
        player_max_hp += choice['value']
        player_hp = min(player_hp + choice['value'], player_max_hp)
    elif choice['effect'] == 'speed': player_speed += choice['value']
    elif choice['effect'] == 'attack_speed': w['speed'] = max(5, w['speed'] + choice['value'])
    elif choice['effect'] == 'damage': w['damage'] += choice['value']
    elif choice['effect'] == 'bullet_speed': w['bullet_speed'] += choice['value']
    elif choice['effect'] == 'heal': player_hp = min(player_hp + choice['value'], player_max_hp)
    elif choice['effect'] == 'skill_e': skill_e_unlocked = True
    elif choice['effect'] == 'pet': pet_unlocked = True


def use_skill_q():
    global skill_q_timer, fireball_active, fireball_timer, rage_active, rage_timer, player_shield
    skin = skins[current_skin]['name']
    if skin == 'Knight': player_shield += 20
    elif skin == 'Mage': fireball_active = True; fireball_timer = 60
    elif skin == 'Archer':
        for _ in range(15):
            if enemies:
                target = random.choice(enemies)
                target[2] -= 20
                if target[2] <= 0: enemies.remove(target)
    elif skin == 'Berserk': rage_active = True; rage_timer = 120
    skill_q_timer = 600


def use_skill_e():
    global skill_e_timer, freeze_active, freeze_timer, player_shield
    skin = skins[current_skin]['name']
    if skin == 'Knight': player_shield += 999
    elif skin == 'Mage': freeze_active = True; freeze_timer = 180
    elif skin == 'Archer':
        for e in enemies[:]:
            e[2] -= 50
            if e[2] <= 0: enemies.remove(e)
    elif skin == 'Berserk':
        for _ in range(5):
            if enemies:
                target = random.choice(enemies)
                target[2] -= 100
                if target[2] <= 0: enemies.remove(target)
    skill_e_timer = 1800


def reset_game():
    global player_x, player_y, player_hp, player_max_hp, player_speed
    global xp, level, xp_to_level, choosing
    global wave, enemies_in_wave, enemies_spawned, enemies_killed_wave, total_kills
    global spawn_timer, wave_delay, boss, boss_spawned, enemies_to_boss
    global player_shield, paused, weapon_type, weapon_index
    global in_menu, game_over, in_shop
    global skill_q_timer, skill_e_timer, fireball_active, freeze_active, rage_active
    global pet_active, revive_statue, ally_revived, zoom, auto_aim

    player_x, player_y = MAP_WIDTH//2, MAP_HEIGHT//2
    player_hp = 100; player_max_hp = 100; player_speed = 4; player_shield = 0
    paused = False; weapon_type = 'bow'; weapon_index = 0; zoom = 1.0; auto_aim = False
    xp = 0; level = 1; xp_to_level = 50
    wave = 1; enemies_in_wave = 10; enemies_spawned = 0; enemies_killed_wave = 0; total_kills = 0
    spawn_timer = 0; wave_delay = 0; boss = None; boss_spawned = False; enemies_to_boss = 100
    choosing = False; in_menu = False; game_over = False; in_shop = False
    skill_q_timer = 0; skill_e_timer = 0
    fireball_active = False; freeze_active = False; rage_active = False
    pet_active = pet_unlocked; revive_statue = None; ally_revived = False
    enemies.clear(); bullets.clear(); enemy_bullets.clear(); coins.clear(); heals.clear(); chests.clear()
    if floor_imgs: global floor_img; floor_img = random.choice(floor_imgs)


# Сетевые функции
def start_server():
    global server_socket, is_host, lobby_message
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 5555))
        server_socket.listen(1)
        server_socket.settimeout(0.1)
        is_host = True
        lobby_message = t('waiting')
        threading.Thread(target=accept_client, daemon=True).start()
    except:
        lobby_message = 'Server error'

def accept_client():
    global client_socket, network_player2
    try:
        client_socket, addr = server_socket.accept()
        network_player2 = [MAP_WIDTH//2, MAP_HEIGHT//2, 100]
        threading.Thread(target=network_listener, daemon=True).start()
    except:
        pass

def connect_to_server(ip):
    global client_socket, is_client, lobby_message, network_player2
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, 5555))
        is_client = True
        network_player2 = [MAP_WIDTH//2, MAP_HEIGHT//2, 100]
        lobby_message = 'Connected!'
        threading.Thread(target=network_listener, daemon=True).start()
    except:
        lobby_message = 'Connection failed'

def network_listener():
    global network_data
    while client_socket:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                network_data = json.loads(data)
        except:
            break

def send_network_data():
    global network_data
    data = json.dumps({'x': player_x, 'y': player_y, 'hp': player_hp})
    try:
        if is_host and client_socket: client_socket.send(data.encode())
        elif is_client and client_socket: client_socket.send(data.encode())
    except:
        pass


# Главный цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0: zoom = min(2.0, zoom + 0.1)
            else: zoom = max(0.5, zoom - 0.1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            if paused:
                menu_btn_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT//2, 180, 45)
                resume_btn_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 55, 180, 45)
                if menu_btn_rect.collidepoint(mx, my): paused = False; in_menu = True; game_over = False
                if resume_btn_rect.collidepoint(mx, my): paused = False
            if in_menu:
                start_btn_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 - 40, 180, 40)
                lobby_btn_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 10, 180, 30)
                lang_btn_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 45, 180, 30)
                skins_btn_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 80, 180, 30)
                if start_btn_rect.collidepoint(mx, my): reset_game()
                if lobby_btn_rect.collidepoint(mx, my): in_lobby = True; in_menu = False
                if lang_btn_rect.collidepoint(mx, my): lang = 'ru' if lang == 'en' else 'en'; save_game()
                if skins_btn_rect.collidepoint(mx, my): in_skins = True; in_menu = False; skin_selected = current_skin
            if in_lobby:
                host_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 - 30, 180, 40)
                join_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 20, 180, 40)
                back_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 70, 180, 40)
                if host_btn.collidepoint(mx, my): start_server()
                if join_btn.collidepoint(mx, my): connect_to_server('127.0.0.1')
                if back_btn.collidepoint(mx, my): in_lobby = False; in_menu = True
        if event.type == pygame.KEYDOWN:
            if in_skins:
                if event.key == pygame.K_UP and skin_selected > 0: skin_selected -= 1
                if event.key == pygame.K_DOWN and skin_selected < len(skins)-1: skin_selected += 1
                if event.key == pygame.K_RETURN:
                    s = skins[skin_selected]
                    if s['unlocked']: current_skin = skin_selected
                    elif total_coins >= s['cost']: s['unlocked'] = True; total_coins -= s['cost']; current_skin = skin_selected; save_skins(); save_game()
                if event.key == pygame.K_ESCAPE: in_skins = False; in_menu = True
            if in_shop:
                if event.key == pygame.K_UP: shop_selected = (shop_selected - 1) % len(shop_items)
                if event.key == pygame.K_DOWN: shop_selected = (shop_selected + 1) % len(shop_items)
                if event.key == pygame.K_RETURN:
                    item = shop_items[shop_selected]
                    if total_coins >= item['cost']: total_coins -= item['cost']; apply_choice(item); save_game()
                if event.key == pygame.K_SPACE: in_shop = False
            if event.key == pygame.K_SPACE and (in_menu or game_over) and not in_skins and not in_shop: reset_game()
            if event.key == pygame.K_ESCAPE:
                if in_skins: in_skins = False; in_menu = True
                elif in_shop: in_shop = False
                elif in_lobby: in_lobby = False; in_menu = True
                elif in_menu: save_game(); pygame.quit(); sys.exit()
                elif not game_over and not in_menu: paused = not paused
                else: in_menu = True; game_over = False
            if event.key == pygame.K_p and not in_menu and not game_over and not in_shop and not in_skins: paused = not paused
            if event.key == pygame.K_TAB and not in_menu and not game_over and not in_shop:
                weapon_index = (weapon_index + 1) % len(weapon_keys); weapon_type = weapon_keys[weapon_index]
            if event.key == pygame.K_q and not in_menu and not game_over and not in_shop and skill_q_timer <= 0: use_skill_q()
            if event.key == pygame.K_e and not in_menu and not game_over and not in_shop and skill_e_timer <= 0 and skill_e_unlocked: use_skill_e()
            if event.key == pygame.K_r and not in_menu and not game_over and not in_shop: auto_aim = not auto_aim
            if event.key == pygame.K_l and in_menu: lang = 'ru' if lang == 'en' else 'en'; save_game()
            if event.key == pygame.K_4 and in_menu: in_skins = True; in_menu = False; skin_selected = current_skin
            if choosing:
                if event.key == pygame.K_1 and len(level_up_choices) >= 1: apply_choice(level_up_choices[0]); choosing = False
                if event.key == pygame.K_2 and len(level_up_choices) >= 2: apply_choice(level_up_choices[1]); choosing = False
                if event.key == pygame.K_3 and len(level_up_choices) >= 3: apply_choice(level_up_choices[2]); choosing = False

    # Отрисовка экранов
    if in_skins:
        screen.fill(BLACK)
        skin_title = font.render('SKINS', True, YELLOW)
        screen.blit(skin_title, skin_title.get_rect(center=(WIDTH//2, 60)))
        for i, s in enumerate(skins):
            color = WHITE if i == skin_selected else GRAY
            txt = f"{s['name']} - {s['cost']} coins" if not s['unlocked'] else f"{s['name']} - OWNED"
            screen.blit(font.render(txt, True, color), font.render(txt, True, color).get_rect(center=(WIDTH//2, 120 + i*50)))
        screen.blit(font.render('ESC - back', True, GRAY), font.render('ESC - back', True, GRAY).get_rect(center=(WIDTH//2, HEIGHT-50)))
        pygame.display.flip(); clock.tick(60); continue

    if in_lobby:
        if lobby_bg_img: screen.blit(lobby_bg_img, (0, 0))
        else: screen.fill(BLACK)
        screen.blit(big_font.render(t('lobby'), True, YELLOW), big_font.render(t('lobby'), True, YELLOW).get_rect(center=(WIDTH//2, 100)))
        host_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 - 30, 180, 40)
        join_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 20, 180, 40)
        back_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 70, 180, 40)
        for btn, txt in [(host_btn, t('host')), (join_btn, t('join')), (back_btn, t('back'))]:
            pygame.draw.rect(screen, (60, 60, 80), btn); pygame.draw.rect(screen, WHITE, btn, 2)
            screen.blit(font.render(txt, True, WHITE), font.render(txt, True, WHITE).get_rect(center=btn.center))
        if lobby_message:
            screen.blit(font.render(lobby_message, True, YELLOW), font.render(lobby_message, True, YELLOW).get_rect(center=(WIDTH//2, HEIGHT//2 + 120)))
        pygame.display.flip(); clock.tick(60); continue

    if in_menu:
        if menu_bg_img: screen.blit(menu_bg_img, (0, 0))
        else: screen.fill(BLACK)
        menu_bg_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 160, 440, 320)
        pygame.draw.rect(screen, (20, 20, 30, 200), menu_bg_rect); pygame.draw.rect(screen, (80, 80, 100), menu_bg_rect, 3)
        screen.blit(big_font.render(t('title'), True, YELLOW), big_font.render(t('title'), True, YELLOW).get_rect(center=(WIDTH//2, HEIGHT//2 - 90)))
        for y, key in [(-40, 'start'), (10, 'lobby'), (45, 'lang_hint'), (80, 'start')]:
            if key == 'lobby':
                btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + y, 180, 30)
                pygame.draw.rect(screen, (60, 60, 80), btn); pygame.draw.rect(screen, WHITE, btn, 2)
                screen.blit(font.render(t('lobby'), True, WHITE), font.render(t('lobby'), True, WHITE).get_rect(center=btn.center))
            elif key == 'start' and y == -40:
                btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + y, 180, 40)
                pygame.draw.rect(screen, (60, 60, 80), btn); pygame.draw.rect(screen, WHITE, btn, 2)
                screen.blit(font.render(t(key), True, WHITE), font.render(t(key), True, WHITE).get_rect(center=btn.center))
            elif key == 'start' and y == 80:
                screen.blit(small_font.render('[4] SKINS', True, GRAY), small_font.render('[4] SKINS', True, GRAY).get_rect(center=(WIDTH//2, HEIGHT//2 + y)))
            else:
                screen.blit(small_font.render(t(key), True, GRAY), small_font.render(t(key), True, GRAY).get_rect(center=(WIDTH//2, HEIGHT//2 + y)))
        # Профиль
        profile_text = small_font.render(f"Profile LVL: {profile_level} ({profile_xp}/{profile_xp_to_next})", True, GRAY)
        screen.blit(profile_text, profile_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 120)))
        pygame.display.flip(); clock.tick(60); continue

    if in_shop:
        screen.fill(BLACK)
        screen.blit(big_font.render(t('shop'), True, YELLOW), big_font.render(t('shop'), True, YELLOW).get_rect(center=(WIDTH//2, 80)))
        screen.blit(font.render(f"{t('coins')}: {total_coins}", True, WHITE), font.render(f"{t('coins')}: {total_coins}", True, WHITE).get_rect(center=(WIDTH//2, 130)))
        for i, item in enumerate(shop_items):
            color = WHITE if i == shop_selected else GRAY
            if total_coins < item['cost']: color = RED
            screen.blit(font.render(f"{item['name']} - {item['cost']} {t('coins').lower()}", True, color),
                       font.render(f"{item['name']} - {item['cost']} {t('coins').lower()}", True, color).get_rect(center=(WIDTH//2, 190 + i*45)))
        screen.blit(font.render(t('up_down_buy'), True, GRAY), font.render(t('up_down_buy'), True, GRAY).get_rect(center=(WIDTH//2, HEIGHT-40)))
        pygame.display.flip(); clock.tick(60); continue

    # Игра
    if not game_over and not choosing and not in_shop and not paused:
        w = weapons[weapon_type]
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if dx != 0 and dy != 0: dx *= 0.707; dy *= 0.707

        player_x += dx * player_speed; player_y += dy * player_speed
        player_x = max(player_radius, min(MAP_WIDTH - player_radius, player_x))
        player_y = max(player_radius, min(MAP_HEIGHT - player_radius, player_y))
        camera_x = player_x - WIDTH//2 / zoom; camera_y = player_y - HEIGHT//2 / zoom
        camera_x = max(0, min(MAP_WIDTH - WIDTH/zoom, camera_x))
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT/zoom, camera_y))

        # Питомец следует за игроком
        if pet_active:
            pet_x += (player_x - pet_x) * 0.05
            pet_y += (player_y - pet_y) * 0.05

        attack_cooldown -= 1
        if weapon_type not in ['sword', 'axe']:
            if (enemies or boss) and attack_cooldown <= 0:
                if auto_aim and enemies:
                    target = min(enemies, key=lambda e: ((e[0]-player_x)**2 + (e[1]-player_y)**2)**0.5)
                    wx, wy = target[0], target[1]
                else:
                    mx, my = pygame.mouse.get_pos()
                    wx, wy = mx/zoom + camera_x, my/zoom + camera_y
                edx, edy = wx - player_x, wy - player_y
                dist = max(1, (edx**2 + edy**2)**0.5)
                bullets.append([player_x, player_y, edx/dist*w['bullet_speed'], edy/dist*w['bullet_speed'], weapon_type])
                attack_cooldown = w['speed']
        else:
            if attack_cooldown <= 0 and (enemies or boss):
                attack_cooldown = w['speed']
                for e in enemies[:]:
                    if abs(e[0]-player_x) < 60 and abs(e[1]-player_y) < 60:
                        e[2] -= w['damage']
                        if e[2] <= 0:
                            enemies.remove(e); xp += 10; enemies_killed_wave += 1; total_kills += 1
                            profile_xp += 5
                            if total_kills >= enemies_to_boss and not boss_spawned: spawn_boss()
                if boss and abs(boss[0]-player_x) < 60 and abs(boss[1]-player_y) < 60:
                    boss[2] -= w['damage']
                    if boss[2] <= 0:
                        boss = None; boss_spawned = False; total_kills = 0; xp += 200; profile_xp += 50
                        for _ in range(10): coins.append([random.randint(100, MAP_WIDTH-100), random.randint(100, MAP_HEIGHT-100)])
                        total_coins += 100; enemies_to_boss += 50; in_shop = True; save_game()

        for b in bullets[:]:
            b[0] += b[2]; b[1] += b[3]
            if b[0] < 0 or b[0] > MAP_WIDTH or b[1] < 0 or b[1] > MAP_HEIGHT: bullets.remove(b)
        for b in enemy_bullets[:]:
            b[0] += b[2]; b[1] += b[3]
            if b[0] < 0 or b[0] > MAP_WIDTH or b[1] < 0 or b[1] > MAP_HEIGHT: enemy_bullets.remove(b)
            elif abs(b[0]-player_x) < 15 and abs(b[1]-player_y) < 15:
                enemy_bullets.remove(b)
                if player_shield > 0: player_shield -= 1
                else: player_hp -= 10
                if player_hp <= 0: game_over = True

        if not boss_spawned:
            if wave_delay > 0: wave_delay -= 1
            elif enemies_spawned < enemies_in_wave:
                spawn_timer += 1
                if spawn_timer > max(15, 60 - level*2): spawn_timer = 0; spawn_enemy(); enemies_spawned += 1
            elif len(enemies) == 0 and not boss:
                wave += 1; enemies_in_wave = 10 + wave*3; enemies_spawned = 0; enemies_killed_wave = 0; wave_delay = 60
                # Статуя воскрешения
                if revive_statue is None and network_player2 and not ally_revived:
                    revive_statue = [random.randint(100, MAP_WIDTH-100), random.randint(100, MAP_HEIGHT-100)]

        if random.randint(0, 2700) < 1 and not boss_spawned:
            chests.append([random.randint(100, MAP_WIDTH-100), random.randint(100, MAP_HEIGHT-100)])

        # Проверка статуи воскрешения
        if revive_statue:
            if abs(revive_statue[0]-player_x) < 40 and abs(revive_statue[1]-player_y) < 40:
                ally_revived = True
                revive_statue = None

        for e in enemies[:]:
            if not freeze_active:
                edx, edy = player_x - e[0], player_y - e[1]
                dist = max(1, (edx**2 + edy**2)**0.5)
                e[0] += edx/dist*e[4]; e[1] += edy/dist*e[4]
            if abs(e[0]-player_x) < 20 and abs(e[1]-player_y) < 20:
                if len(e) > 5 and e[5] == 'shooter':
                    e[6] += 1
                    if e[6] > 120:
                        e[6] = 0; edx, edy = player_x - e[0], player_y - e[1]
                        dist = max(1, (edx**2 + edy**2)**0.5)
                        enemy_bullets.append([e[0], e[1], edx/dist*4, edy/dist*4])
                if player_shield > 0: player_shield -= 1
                else: player_hp -= 1
                if player_hp <= 0: game_over = True

        if boss:
            if not freeze_active:
                edx, edy = player_x - boss[0], player_y - boss[1]
                dist = max(1, (edx**2 + edy**2)**0.5)
                boss[0] += edx/dist*boss[4]; boss[1] += edy/dist*boss[4]
            if abs(boss[0]-player_x) < 30 and abs(boss[1]-player_y) < 30:
                if player_shield > 0:
                    dmg = min(3, player_shield); player_shield -= dmg
                    if 3 - dmg > 0: player_hp -= (3 - dmg)
                else: player_hp -= 3
                if player_hp <= 0: game_over = True

        for b in bullets[:]:
            for e in enemies[:]:
                if abs(b[0]-e[0]) < 15 and abs(b[1]-e[1]) < 15:
                    if b in bullets: bullets.remove(b)
                    e[2] -= w['damage']
                    if e[2] <= 0:
                        if e in enemies:
                            enemies.remove(e); xp += 10; enemies_killed_wave += 1; total_kills += 1; profile_xp += 5
                            if random.random() < 0.4: coins.append([e[0], e[1]])
                            if random.random() < 0.08: heals.append([e[0], e[1]])
                            if total_kills >= enemies_to_boss and not boss_spawned: spawn_boss()
                    break

        if boss:
            for b in bullets[:]:
                if abs(b[0]-boss[0]) < 40 and abs(b[1]-boss[1]) < 40:
                    if b in bullets: bullets.remove(b)
                    boss[2] -= w['damage']
                    if boss[2] <= 0:
                        boss = None; boss_spawned = False; total_kills = 0; xp += 200; profile_xp += 50
                        for _ in range(10): coins.append([random.randint(100, MAP_WIDTH-100), random.randint(100, MAP_HEIGHT-100)])
                        total_coins += 100; enemies_to_boss += 50; in_shop = True; save_game()
                    break

        for c in coins[:]:
            if abs(c[0]-player_x) < 25 and abs(c[1]-player_y) < 25: coins.remove(c); total_coins += 1
        for h in heals[:]:
            if abs(h[0]-player_x) < 25 and abs(h[1]-player_y) < 25: heals.remove(h); player_hp = min(player_hp+15, player_max_hp)
        for ch in chests[:]:
            if abs(ch[0]-player_x) < 35 and abs(ch[1]-player_y) < 35:
                chests.remove(ch); player_shield += 10
                for _ in range(5): coins.append([ch[0] + random.randint(-20,20), ch[1] + random.randint(-20,20)])

        if skill_q_timer > 0: skill_q_timer -= 1
        if skill_e_timer > 0: skill_e_timer -= 1
        if fireball_active:
            fireball_timer -= 1
            for e in enemies[:]:
                if abs(e[0]-player_x) < 100 and abs(e[1]-player_y) < 100:
                    e[2] -= 2
                    if e[2] <= 0: enemies.remove(e); profile_xp += 3
            if fireball_timer <= 0: fireball_active = False
        if freeze_active:
            freeze_timer -= 1
            if freeze_timer <= 0: freeze_active = False
        if rage_active:
            rage_timer -= 1
            if rage_timer <= 0: rage_active = False

        # Профиль
        if profile_xp >= profile_xp_to_next:
            profile_level += 1; profile_xp -= profile_xp_to_next; profile_xp_to_next = int(profile_xp_to_next * 1.5)
            total_coins += 50  # награда за уровень
            save_game()

        if xp >= xp_to_level:
            level += 1; xp -= xp_to_level; xp_to_level = int(xp_to_level*1.5)
            if level % 10 == 0: level_up_choices = get_level_up_choices(); choosing = True

        # Сеть
        if is_host or is_client:
            send_network_data()
            if network_player2:
                pass

    # Рисовка
    if floor_img:
        start_x = int(camera_x//64)*64; start_y = int(camera_y//64)*64
        for fx in range(start_x-64, int(camera_x)+int(WIDTH/zoom)+128, 64):
            for fy in range(start_y-64, int(camera_y)+int(HEIGHT/zoom)+128, 64):
                if 0 <= fx < MAP_WIDTH and 0 <= fy < MAP_HEIGHT:
                    screen.blit(floor_img, (int((fx-camera_x)*zoom), int((fy-camera_y)*zoom)))
    else:
        screen.fill(GRAY)

    panel = pygame.Rect(5, 5, 220, 130)
    pygame.draw.rect(screen, (0,0,0,180), panel); pygame.draw.rect(screen, (80,80,100), panel, 2)
    screen.blit(font.render(f"{t('lvl')}: {level}", True, WHITE), (12, 12))
    screen.blit(font.render(f"{t('coins')}: {total_coins}", True, YELLOW), (12, 38))
    screen.blit(font.render(f"{t('wave')}: {wave}", True, ORANGE), (12, 64))
    if player_shield > 0: screen.blit(font.render(f'Shield: {player_shield}', True, (100,150,255)), (12, 90))

    wp = pygame.Rect(WIDTH-170, 5, 160, 35)
    pygame.draw.rect(screen, (0,0,0,180), wp); pygame.draw.rect(screen, (80,80,100), wp, 2)
    screen.blit(font.render(f"{w['name']} [TAB]", True, WHITE), (WIDTH-162, 12))
    aim_text = 'AUTO' if auto_aim else 'MOUSE'
    screen.blit(small_font.render(f'[R] {aim_text}', True, GRAY), (WIDTH-162, 40))
    screen.blit(font.render(f"[Q] {'READY' if skill_q_timer<=0 else skill_q_timer//60+1}s", True, YELLOW), (WIDTH-200, 55))
    if skill_e_unlocked:
        screen.blit(font.render(f"[E] {'READY' if skill_e_timer<=0 else skill_e_timer//60+1}s", True, ORANGE), (WIDTH-200, 80))

    # Объекты с учётом зума
    def draw_obj(img, x, y, w, h, color=None, size=None):
        sx, sy = int((x-camera_x)*zoom), int((y-camera_y)*zoom)
        if -50 < sx < WIDTH+50 and -50 < sy < HEIGHT+50:
            if img: screen.blit(img, (sx-w//2, sy-h//2))
            elif color: pygame.draw.circle(screen, color, (sx, sy), size)

    for c in coins: draw_obj(coin_img, c[0], c[1], 14, 14, YELLOW, 6)
    for h in heals: draw_obj(heal_img, h[0], h[1], 20, 20, (255,100,100), 8)
    for ch in chests:
        sx, sy = int((ch[0]-camera_x)*zoom), int((ch[1]-camera_y)*zoom)
        if -50 < sx < WIDTH+50 and -50 < sy < HEIGHT+50:
            if chest_img: screen.blit(chest_img, (sx-15, sy-15))
            else: pygame.draw.rect(screen, (139,90,40), (sx-15, sy-15, 30, 30)); pygame.draw.rect(screen, YELLOW, (sx-15, sy-15, 30, 30), 2)

    for e in enemies:
        sx, sy = int((e[0]-camera_x)*zoom), int((e[1]-camera_y)*zoom)
        if -50 < sx < WIDTH+50 and -50 < sy < HEIGHT+50:
            enemy_type = e[5] if len(e) > 5 else 'normal'
            if enemy_type in enemy_imgs: screen.blit(enemy_imgs[enemy_type], (sx-12, sy-12))
            else:
                ec = RED
                if enemy_type == 'fast': ec = ORANGE
                elif enemy_type == 'tank': ec = (150,30,30)
                elif enemy_type == 'shooter': ec = PURPLE
                pygame.draw.circle(screen, ec, (sx, sy), 12)
            bar_w, bar_h = 30, 4; bx, by = sx-bar_w//2, sy-18
            pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
            pygame.draw.rect(screen, GREEN, (bx, by, bar_w*(e[2]/e[3]), bar_h))
            pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    if boss:
        sx, sy = int((boss[0]-camera_x)*zoom), int((boss[1]-camera_y)*zoom)
        bc = RED if boss[5]=='fast' else (PURPLE if boss[5]=='tank' else (200,100,50))
        pygame.draw.circle(screen, bc, (sx, sy), 35); pygame.draw.circle(screen, WHITE, (sx, sy), 35, 3)
        bar_w, bar_h = 70, 6; bx, by = sx-bar_w//2, sy-45
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w*(boss[2]/boss[3]), bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    for b in bullets:
        sx, sy = int((b[0]-camera_x)*zoom), int((b[1]-camera_y)*zoom)
        bw = weapons.get(b[4], weapons['bow'])
        if bw['img']: screen.blit(bw['img'], (sx-3, sy-2))
        else: pygame.draw.circle(screen, bw['color'], (sx, sy), bw['size'])
    for b in enemy_bullets:
        sx, sy = int((b[0]-camera_x)*zoom), int((b[1]-camera_y)*zoom)
        pygame.draw.circle(screen, PURPLE, (sx, sy), 5)

    # Статуя
    if revive_statue:
        sx, sy = int((revive_statue[0]-camera_x)*zoom), int((revive_statue[1]-camera_y)*zoom)
        if revive_statue_img: screen.blit(revive_statue_img, (sx-20, sy-20))
        else: pygame.draw.rect(screen, YELLOW, (sx-15, sy-15, 30, 30))

    # Питомец
    if pet_active and pet_img:
        sx, sy = int((pet_x-camera_x)*zoom), int((pet_y-camera_y)*zoom)
        screen.blit(pet_img, (sx-10, sy-10))

    # Второй игрок
    if network_player2:
        sx, sy = int((network_player2['x']-camera_x)*zoom), int((network_player2['y']-camera_y)*zoom)
        if -50 < sx < WIDTH+50 and -50 < sy < HEIGHT+50:
            pygame.draw.circle(screen, GREEN, (sx, sy), player_radius)
            pygame.draw.circle(screen, WHITE, (sx, sy), player_radius, 2)

    if not game_over:
        sx, sy = int((player_x-camera_x)*zoom), int((player_y-camera_y)*zoom)
        skin_img = skins[current_skin].get('image', player_img)
        if skin_img: screen.blit(skin_img, (sx-15, sy-15))
        else: pygame.draw.circle(screen, BLUE, (sx, sy), player_radius); pygame.draw.circle(screen, WHITE, (sx, sy), player_radius, 2)
        bar_w, bar_h = 40, 5; bx, by = sx-bar_w//2, sy-player_radius-10
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w*(player_hp/player_max_hp), bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    if wave_delay > 0:
        screen.blit(big_font.render(f"{t('wave')} {wave}", True, YELLOW),
                   big_font.render(f"{t('wave')} {wave}", True, YELLOW).get_rect(center=(WIDTH//2, HEIGHT//2)))

    if paused:
        dark = pygame.Surface((WIDTH, HEIGHT)); dark.set_alpha(150); dark.fill(BLACK); screen.blit(dark, (0,0))
        screen.blit(big_font.render('PAUSE', True, YELLOW), big_font.render('PAUSE', True, YELLOW).get_rect(center=(WIDTH//2, HEIGHT//2-60)))
        menu_btn_rect = pygame.Rect(WIDTH//2-90, HEIGHT//2, 180, 45)
        resume_btn_rect = pygame.Rect(WIDTH//2-90, HEIGHT//2+55, 180, 45)
        pygame.draw.rect(screen, (80,80,100), menu_btn_rect); pygame.draw.rect(screen, WHITE, menu_btn_rect, 2)
        screen.blit(font.render(t('menu_btn'), True, WHITE), font.render(t('menu_btn'), True, WHITE).get_rect(center=menu_btn_rect.center))
        pygame.draw.rect(screen, (80,80,100), resume_btn_rect); pygame.draw.rect(screen, WHITE, resume_btn_rect, 2)
        screen.blit(font.render(t('resume'), True, WHITE), font.render(t('resume'), True, WHITE).get_rect(center=resume_btn_rect.center))

    if choosing:
        dark = pygame.Surface((WIDTH, HEIGHT)); dark.set_alpha(180); dark.fill(BLACK); screen.blit(dark, (0,0))
        screen.blit(big_font.render(t('choose'), True, YELLOW), big_font.render(t('choose'), True, YELLOW).get_rect(center=(WIDTH//2, HEIGHT//2-80)))
        for i, c in enumerate(level_up_choices):
            screen.blit(font.render(f"[{i+1}] {c['name']}", True, WHITE), font.render(f"[{i+1}] {c['name']}", True, WHITE).get_rect(center=(WIDTH//2, HEIGHT//2 + i*40)))

    if game_over:
        screen.blit(big_font.render(t('game_over'), True, RED), big_font.render(t('game_over'), True, RED).get_rect(center=(WIDTH//2, HEIGHT//2-20)))
        screen.blit(font.render(t('restart'), True, GRAY), font.render(t('restart'), True, GRAY).get_rect(center=(WIDTH//2, HEIGHT//2+20)))
        save_game()

    pygame.display.flip()
    clock.tick(60)
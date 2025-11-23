# Special Day Dodger

import pygame
import random
import time
import string
import json
import os

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SIZE = 100
LASER_SIZE = (5, 5)
SPEED_INCREMENT = 0.005
FPS = 60
WHITE, BLACK, RED, LIGHT_GREEN = (255, 255, 255), (0, 0, 0), (255, 0, 0), (144, 238, 144)
LEADERBOARD_FILE = "leaderboard.json"
FONT_PATH = "fonts/"
IMAGE_PATH = "images/"
AUDIO_PATH = "audio/"

OBJECT_SIZES = {
    'flowers': 100,
    'spreadsheet': 50,
    'invitation': 60,
    'rings': 40,
    'tux': 100,
    'list': 50,
    'maddievillain': 200
}
  

# --- Initialization ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Special Day Dodger")
clock = pygame.time.Clock()

# --- Asset Loading ---
def load_image(name, size):
    return pygame.transform.scale(pygame.image.load(os.path.join(IMAGE_PATH, name)), size)

def load_assets():
    assets = {name: load_image(f"{name}.png", (size, size)) for name, size in OBJECT_SIZES.items()}
    assets['player'] = load_image("andreas.png", (PLAYER_SIZE, PLAYER_SIZE))
    assets['background_img'] = pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGE_PATH, "dodgebg.png")),
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    return assets

assets = load_assets()

# --- Fonts ---
def get_font(size, title=False):
    path = os.path.join(FONT_PATH, "neon_pixel-7.ttf" if title else "smallest_pixel-7.ttf")
    try:
        return pygame.font.Font(path, size)
    except:
        return pygame.font.SysFont(None, size)

font = get_font(24)
initial_font = get_font(50)
title_font = get_font(72, title=True)
small_font = get_font(16)

# --- Leaderboard ---
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f)

leaderboard = load_leaderboard()

# --- Utility Functions ---
def draw_text(text, x, y, font_obj=font, color=BLACK):
    for i, line in enumerate(text.splitlines()):
        screen.blit(font_obj.render(line, True, color), (x, y + i * 30))

def draw_wrapped(text, top_y, font_obj, color=WHITE):
    margin = 50
    words, lines, current = text.split(), [], ''
    for word in words:
        test = f"{current} {word}".strip()
        if font_obj.size(test)[0] <= SCREEN_WIDTH - 2 * margin:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    for i, line in enumerate(lines):
        surf = font_obj.render(line, True, color)
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, top_y + i * 35))
        screen.blit(surf, rect)

def play_laser_sound():
    if mute:
        return
    try:
        sound = pygame.mixer.Sound(os.path.join(AUDIO_PATH, "pew.mp3"))
        sound.set_volume(0.5)  # Adjust volume if needed
        sound.play()
    except Exception as e:
        print(f"Laser sound error: {e}")
    except Exception as e:
        print(f"Laser sound error: {e}")

def play_special_sound():
    if mute:
        return
    try:
        special = pygame.mixer.Sound(os.path.join(AUDIO_PATH, "special_day.mp3"))
        special.set_volume(1.0)
        special.play()
    except Exception as e:
        print(f"Special sound error: {e}")

def play_lose_sound():
    if mute:
        return
    try:
        sound = pygame.mixer.Sound(os.path.join(AUDIO_PATH, "lose_sound.mp3"))
        sound.set_volume(0.7)
        sound.play()
    except Exception as e:
        print(f"Lose sound error: {e}")

def init_music():
    try:
        pygame.mixer.music.load(os.path.join(AUDIO_PATH, "happy_whistle_tune.mp3"))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Music init error: {e}")

init_music()

# --- Game State ---
def reset_game():
    global player_x, player_y, laser, laser_trail, obstacles
    global obstacle_speed, spawn_rate, tasks_avoided
    global boost_end_time, special_event_timer

    player_x = 10
    player_y = SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2
    laser = None
    laser_trail = []
    obstacles = []
    obstacle_speed = 2
    spawn_rate = 0.02
    tasks_avoided = 0
    boost_end_time = -10
    special_event_timer = time.time()

reset_game()
special_event_interval = random.randint(20, 30)
mute, running, show_start_screen = False, True, True
maddie_display_time = -10

# --- Game Functions ---
def handle_input():
    global player_x, player_y, laser, laser_trail
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= 5
        if player_x < 0:
            player_x = 0
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += 5
        if player_x > SCREEN_WIDTH - PLAYER_SIZE:
            player_x = SCREEN_WIDTH - PLAYER_SIZE
    if keys[pygame.K_UP] or keys[pygame.K_w]: player_y -= 5
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: player_y += 5

    # Wrap vertically if more than 35% off-screen
    if player_y + PLAYER_SIZE * 0.35 > SCREEN_HEIGHT:
        player_y = -PLAYER_SIZE * 0.35
    elif player_y < -PLAYER_SIZE * 0.35:
        player_y = SCREEN_HEIGHT - PLAYER_SIZE * 0.35
    if keys[pygame.K_SPACE] and not laser:
        laser = [player_x + PLAYER_SIZE // 2 - LASER_SIZE[0] // 2,
                 player_y + PLAYER_SIZE // 2 - LASER_SIZE[1] // 2]
        laser_trail = []
        play_laser_sound()

def update_laser():
    global laser, laser_trail
    if laser:
        laser_trail.append((laser[0], laser[1]))
        laser[0] += 7
        if laser[0] > SCREEN_WIDTH:
            laser = None
            laser_trail.clear()

def spawn_obstacle():
    name = random.choice([k for k in OBJECT_SIZES if k != 'maddievillain'])
    size = OBJECT_SIZES[name]
    y = random.randint(0, SCREEN_HEIGHT - size)
    img = assets[name]
    obstacles.append([SCREEN_WIDTH, y, img, size])

def update_obstacles():
    global obstacle_speed, tasks_avoided, spawn_rate
    for obstacle in obstacles[:]:
        obstacle[0] -= obstacle_speed
        if obstacle[0] + obstacle[3] < 0:
            obstacles.remove(obstacle)
            tasks_avoided += 1
    obstacle_speed += SPEED_INCREMENT / FPS
    if random.random() < spawn_rate:
        spawn_obstacle()

def check_collisions():
    global laser, laser_trail, tasks_avoided
    buffer = 0.2
    px, py = player_x + PLAYER_SIZE * buffer, player_y + PLAYER_SIZE * buffer
    psize = PLAYER_SIZE * (1 - 2 * buffer)
    for obstacle in obstacles[:]:
        ox, oy = obstacle[0] + obstacle[3] * buffer, obstacle[1] + obstacle[3] * buffer
        osize = obstacle[3] * (1 - 2 * buffer)
        if (px < ox + osize and px + psize > ox and py < oy + osize and py + psize > oy):
            return True
        if laser and (laser[0] + LASER_SIZE[0] > obstacle[0] and laser[0] < obstacle[0] + obstacle[3] and
                      laser[1] < obstacle[1] + obstacle[3] and laser[1] + LASER_SIZE[1] > obstacle[1]):
            obstacles.remove(obstacle)
            laser = None
            laser_trail.clear()
            tasks_avoided += 1
            break
    return False

def draw_game():
    screen.blit(assets['background_img'], (0,0))
    screen.blit(assets['player'], (player_x, player_y))
    for ox, oy, img, _ in obstacles:
        screen.blit(img, (ox, oy))
    if laser:
        pygame.draw.rect(screen, RED, (*laser, *LASER_SIZE))
        for i, (tx, ty) in enumerate(laser_trail[-10:]):
            if i % 2 == 0:
                pygame.draw.circle(screen, RED, (tx + LASER_SIZE[0] // 2, ty + LASER_SIZE[1]), 2)
    if time.time() - maddie_display_time < 5:
        draw_text("IT'S MY", SCREEN_WIDTH - 270, 200, font, BLACK)
        draw_text("SPECIAL", SCREEN_WIDTH - 270, 230, font, BLACK)
        draw_text("DAY!!!", SCREEN_WIDTH - 260, 260, font, BLACK)
        screen.blit(assets['maddievillain'], (SCREEN_WIDTH - 220, SCREEN_HEIGHT // 2 - 100))
    draw_text(f"Tasks avoided: {tasks_avoided}", 20, 20, font, BLACK)
    pygame.display.update()

# --- Game Loop ---
while running:
    if show_start_screen:
        screen.fill(BLACK)
        draw_wrapped("Special Day Dodger", 200, title_font, WHITE)
        draw_wrapped("Help Andreas avoid his wedding responsibilities.", 300, font, WHITE)
        draw_wrapped("Arrows to move. Space to shoot. M to mute.", 350, font, WHITE)
        draw_wrapped("Press Enter to Start", 450, font, WHITE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    show_start_screen = False
                elif event.key == pygame.K_m:
                    mute = not mute
                    pygame.mixer.music.pause() if mute else pygame.mixer.music.unpause()
        continue

    handle_input()
    update_laser()
    update_obstacles()

    now = time.time()
    if 15 < now - special_event_timer < 45:
        spawn_rate = min(spawn_rate + 0.001, 0.12)
        obstacle_speed = min(obstacle_speed + 0.01, 4)

    if now - special_event_timer > special_event_interval:
        maddie_display_time = now
        boost_end_time = now + 10
        spawn_rate = min(0.1, 0.06)
        play_special_sound()
        special_event_timer = now
        special_event_interval = random.randint(20, 30)

    if now > boost_end_time:
        spawn_rate = 0.02

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            mute = not mute
            pygame.mixer.music.pause() if mute else pygame.mixer.music.unpause()

    if check_collisions():
        pygame.mixer.music.stop()
        play_lose_sound()
        screen.fill(BLACK)
        oops_text = "Oops. Responsibility caught up with Andreas."
        text_surface = font.render(oops_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(text_surface, text_rect)
        
        pygame.display.update()
        pygame.time.delay(3000)

        def get_player_initials():
            name = ""
            while len(name) < 3:
                screen.fill(BLACK)
                draw_text("Enter Your Initials:", 120, SCREEN_HEIGHT // 2 - 40, font, WHITE)
                draw_text(name, 120, SCREEN_HEIGHT // 2, initial_font, WHITE)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.unicode.upper() in string.ascii_uppercase:
                            name += event.unicode.upper()
                        elif event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
            return name

        if len(leaderboard) < 5 or tasks_avoided > leaderboard[-1][1]:
            name = get_player_initials()
            leaderboard.append((name, tasks_avoided))
            leaderboard.sort(key=lambda x: x[1], reverse=True)
            leaderboard[:] = leaderboard[:5]
            save_leaderboard(leaderboard)

        screen.fill(BLACK)
        draw_text("LEADERBOARD - MOST AVOIDANT LEGENDS", 100, 100, font, WHITE)
        for i, (name, score) in enumerate(leaderboard):
            draw_text(f"{i + 1}. {name} - {score}", 120, 150 + i * 50, initial_font, WHITE)
        draw_text("Press Enter to Restart. ESC for Menu.", 120, 450, font, WHITE)
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False

        reset_game()
        pygame.mixer.music.load(os.path.join(AUDIO_PATH, "happy_whistle_tune.mp3"))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        if mute:
            pygame.mixer.music.pause()
        pygame.time.delay(1000)


    draw_game()
    clock.tick(FPS)

pygame.quit()

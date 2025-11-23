import pygame
import random
import time
import string
import json
import os
import sys

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE, BLACK, LILAC = (255, 255, 255), (0, 0, 0), (171, 147, 186)
TILE_SIZE, ZOOM, PLAYER_SPEED = 10, 3, 10
MADDIE_SIZE = int(TILE_SIZE * 2.6 * ZOOM)
COUNTDOWN_TIME, HUG_DURATION = 180, 3000
LEADERBOARD_FILE = "leaderboard_2.json"

# --- Paths ---
BASE_PATH = os.path.dirname(__file__)
FONT_PATH = os.path.join(BASE_PATH, "fonts")
IMAGE_PATH = os.path.join(BASE_PATH, "images")
AUDIO_PATH = os.path.join(BASE_PATH, "audio")

# --- Init ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maddie Paddy")
clock = pygame.time.Clock()

# --- Fonts ---
def get_font(size, title=False):
    path = os.path.join(FONT_PATH, "neon_pixel-7.ttf" if title else "smallest_pixel-7.ttf")
    try:
        return pygame.font.Font(path, size)
    except:
        return pygame.font.SysFont(None, size)

font = get_font(24)
big_font = get_font(36)
initial_font = get_font(50)
title_font = get_font(72, title=True)

# --- Drawing Utilities ---
def draw_text(text, x, y, font_obj=font, color=BLACK):
    for i, line in enumerate(text.splitlines()):
        screen.blit(font_obj.render(line, True, color), (x, y + i * 30))

def draw_wrapped(text, top_y, font_obj, color=WHITE):
    margin = 50
    words, lines, current = text.split(), [], ""
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

def draw_torch(surface, player_pos, radius=150, offset=(30, 0)):
    dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dark_overlay.fill((0, 0, 0, 200))
    torch_center = (player_pos[0] + offset[0], player_pos[1] + offset[1])
    pygame.draw.circle(dark_overlay, (0, 0, 0, 0), torch_center, radius)
    surface.blit(dark_overlay, (0, 0))

def darken_surface(surface, factor=0.5):
    dark = pygame.Surface(surface.get_size()).convert_alpha()
    dark.fill((0, 0, 0, int((1 - factor) * 255)))
    copy = surface.copy()
    copy.blit(dark, (0, 0))
    return copy

# --- Audio ---
mute = False

def play_lose_sound():
    if mute:
        return
    try:
        sound = pygame.mixer.Sound(os.path.join(AUDIO_PATH, "lose_sound.mp3"))
        sound.set_volume(0.7)
        sound.play()
    except Exception as e:
        print(f"Lose sound error: {e}")

try:
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(AUDIO_PATH, "sadmaze.mp3"))
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except:
    mute = True

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

# --- Load Assets ---
def load_scaled_image(name, height):
    raw = pygame.image.load(os.path.join(IMAGE_PATH, name)).convert_alpha()
    factor = height / raw.get_height()
    return pygame.transform.scale(raw, (int(raw.get_width() * factor), height))

maze_img_raw = pygame.image.load(os.path.join(IMAGE_PATH, "mazebgclippedpurpscare2.png")).convert()
maze_img = pygame.transform.scale(maze_img_raw, (maze_img_raw.get_width() * ZOOM, maze_img_raw.get_height() * ZOOM))
maze_rect = maze_img.get_rect()

maddie_img = load_scaled_image("maddiesadre.png", 80)
andreas_img = load_scaled_image("andreasrev.png", 80)
hug_img = pygame.transform.scale(pygame.image.load(os.path.join(IMAGE_PATH, "andymaddie_hug.png")).convert_alpha(), (300, 300))
MADDIE_WIDTH, MADDIE_HEIGHT = maddie_img.get_size()
andreas_width, andreas_height = andreas_img.get_size()

# --- Position Functions ---
def is_walkable(x, y, w, h):
    for i in range(w):
        for j in range(h):
            if not (0 <= x + i < maze_rect.width and 0 <= y + j < maze_rect.height):
                return False
            if maze_img.get_at((x + i, y + j)) != pygame.Color(BLACK):
                return False
    return True

def find_position(size, reverse=False):
    x_range = range(maze_rect.width - size, 0, -1) if reverse else range(0, maze_rect.width - size)
    y_range = range(maze_rect.height - size, 0, -1) if reverse else range(0, maze_rect.height - size)
    for y in y_range:
        for x in x_range:
            if is_walkable(x, y, size, size):
                return x, y
    return TILE_SIZE, TILE_SIZE

# --- Game State ---
running, show_start, win, hugging = True, True, False, False
timer, hugging_start = COUNTDOWN_TIME, 0
pygame.time.set_timer(pygame.USEREVENT, 1000)

player_x, player_y = find_position(MADDIE_SIZE)
andreas_x, andreas_y = find_position(MADDIE_SIZE, reverse=True)

# --- Main Loop ---
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                mute = not mute
                pygame.mixer.music.pause() if mute else pygame.mixer.music.unpause()
            elif event.key == pygame.K_RETURN and show_start:
                show_start = False
        elif event.type == pygame.USEREVENT and not win and not hugging:
            timer -= 1

    if show_start:
        screen.fill(BLACK)
        draw_wrapped("Maddie Paddy", 200, title_font)
        draw_wrapped("Help Maddie find Andreas for hugs and avoid an anxiety attack.", 280, font)
        draw_wrapped("Arrow keys to move. M to mute.", 340, font)
        draw_wrapped("Press Enter to start", 420, font)
        pygame.display.update()
        continue

    if hugging:
        elapsed = pygame.time.get_ticks() - hugging_start
        if elapsed >= HUG_DURATION:
            hugging, win = False, True
            remaining_time = timer
            continue
        screen.fill(BLACK)
        if elapsed < 1000:
            screen.blit(maddie_img, (SCREEN_WIDTH // 2 - MADDIE_WIDTH + 10, SCREEN_HEIGHT // 2 - MADDIE_HEIGHT // 2))
            screen.blit(andreas_img, (SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT // 2 - andreas_height // 2))
        else:
            screen.blit(hug_img, (SCREEN_WIDTH // 2 - hug_img.get_width() // 2, SCREEN_HEIGHT // 2 - hug_img.get_height() // 2))
        screen.blit(big_font.render(f"Time: {timer // 60}:{timer % 60:02d}", True, WHITE), (10, 10))
        pygame.display.flip()
        continue

    # Movement
    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
    dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
    if dx and is_walkable(player_x + dx * PLAYER_SPEED, player_y, MADDIE_WIDTH, MADDIE_HEIGHT):
        player_x += dx * PLAYER_SPEED
    if dy and is_walkable(player_x, player_y + dy * PLAYER_SPEED, MADDIE_WIDTH, MADDIE_HEIGHT):
        player_y += dy * PLAYER_SPEED

    # Camera
    cam_x = max(0, min(player_x - SCREEN_WIDTH // 2, maze_rect.width - SCREEN_WIDTH))
    cam_y = max(0, min(player_y - SCREEN_HEIGHT // 2, maze_rect.height - SCREEN_HEIGHT))

    screen.blit(maze_img, (-cam_x, -cam_y))
    screen.blit(darken_surface(andreas_img), (andreas_x - cam_x, andreas_y - cam_y))
    screen.blit(darken_surface(maddie_img), (player_x - cam_x, player_y - cam_y))
    draw_torch(screen, (player_x - cam_x + MADDIE_WIDTH // 2, player_y - cam_y + MADDIE_HEIGHT // 2))
    screen.blit(big_font.render(f"Time: {timer // 60}:{timer % 60:02d}", True, WHITE), (10, 10))
    pygame.display.flip()

    if not win and not hugging and andreas_x <= player_x + MADDIE_WIDTH // 2 <= andreas_x + andreas_width and andreas_y <= player_y + MADDIE_HEIGHT // 2 <= andreas_y + andreas_height:
        hugging = True
        hugging_start = pygame.time.get_ticks()
        pygame.mixer.music.stop()

    if win:
        pygame.mixer.music.stop()
        screen.fill(BLACK)
        draw_wrapped("You found Andreas! Hugs ahoy!", SCREEN_HEIGHT // 2 - 80, big_font)
        draw_wrapped(f"Time left: {remaining_time // 60}:{remaining_time % 60:02d}", SCREEN_HEIGHT // 2 - 40, font)
        pygame.display.update()
        pygame.time.delay(2000)

        def get_initials():
            name = ""
            while len(name) < 3:
                screen.fill(BLACK)
                draw_wrapped("Enter Your Initials:", SCREEN_HEIGHT // 2 - 60, font)
                draw_wrapped(name, SCREEN_HEIGHT // 2, initial_font)
                pygame.display.update()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif e.type == pygame.KEYDOWN:
                        if e.unicode.upper() in string.ascii_uppercase:
                            name += e.unicode.upper()
                        elif e.key == pygame.K_BACKSPACE:
                            name = name[:-1]
            return name

        initials = get_initials()
        leaderboard.append((initials, remaining_time))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        leaderboard = leaderboard[:5]
        save_leaderboard(leaderboard)

        screen.fill(BLACK)
        draw_text("LEADERBOARD - LEAST PANICKY PERCY", 100, 100, font, WHITE)
        for i, (name, score) in enumerate(leaderboard):
            draw_text(f"{i + 1}. {name} - {score // 60}:{score % 60:02d}", 120, 150 + i * 50, initial_font, WHITE)
        draw_text("Press Enter to Restart. ESC for Menu.", 120, 450, font, WHITE)
        pygame.display.update()

        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        win = False
                        timer = COUNTDOWN_TIME
                        player_x, player_y = find_position(MADDIE_SIZE)
                        andreas_x, andreas_y = find_position(MADDIE_SIZE, reverse=True)
                        pygame.mixer.music.play(-1)
                        waiting = False
                    elif e.key == pygame.K_ESCAPE:
                        show_start = True
                        win = False
                        waiting = False

    elif timer <= 0 and not win:
        pygame.mixer.music.stop()
        play_lose_sound()
        screen.fill(BLACK)
        draw_wrapped("Oops. Full blown anxiety attack. Too late!", SCREEN_HEIGHT // 2 - 40, font)
        pygame.display.update()
        pygame.time.delay(3000)

        screen.fill(BLACK)
        draw_text("LEADERBOARD - TIME LEFT", 100, 100, font, WHITE)
        for i, (name, score) in enumerate(leaderboard):
            draw_text(f"{i + 1}. {name} - {score}", 120, 150 + i * 50, initial_font, WHITE)
        draw_text("Press Enter to Restart. ESC for Menu.", 120, 450, font, WHITE)
        pygame.display.update()

        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        timer = COUNTDOWN_TIME
                        player_x, player_y = find_position(MADDIE_SIZE)
                        andreas_x, andreas_y = find_position(MADDIE_SIZE, reverse=True)
                        pygame.mixer.music.play(-1)
                        waiting = False
                    elif e.key == pygame.K_ESCAPE:
                        show_start = True
                        waiting = False

pygame.quit()
sys.exit()

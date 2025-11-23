import pygame
import random
import time
import string
import json
import os

# Initialize Pygame and audio
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SIZE = 100
FLOWER_SIZE = 100
SPREADSHEET_SIZE = 60
INVITATION_SIZE = 60
LASER_SIZE = (20, 40)
SPEED_INCREMENT = 0.005
FPS = 60
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
LEADERBOARD_FILE = "leaderboard.json"

# Load and scale images
def load_image(path, size):
    return pygame.transform.scale(pygame.image.load(path), size)

andreas_img = load_image("images/andreas.png", (PLAYER_SIZE, PLAYER_SIZE))
spreadsheet_img = load_image("images/spreadsheet.png", (SPREADSHEET_SIZE, SPREADSHEET_SIZE))
flowers_img = load_image("images/flowers.png", (FLOWER_SIZE, FLOWER_SIZE))
invitation_img = load_image("images/invitation.png", (INVITATION_SIZE, INVITATION_SIZE))
maddie_img = load_image("images/maddie.png", (200, 200))

# Font setup
def get_font(size):
    try:
        return pygame.font.Font("fonts/rundeck.ttf", size)
    except:
        return pygame.font.SysFont(None, size)

font = get_font(24)
small_font = get_font(20)

# Initialize game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Special Day Dodger")
clock = pygame.time.Clock()

# Audio
pygame.mixer.music.load("audio/whistle_tune.mp3")
pygame.mixer.music.play(-1)

# Game state variables
player_x, player_y = 10, SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2
player_speed = 5
laser = None
laser_speed = 7
obstacles = []
obstacle_speed = 2
spawn_rate = 0.02
normal_spawn_rate = spawn_rate
speed_multiplier = 1.25
tasks_avoided = 0
special_event_timer = time.time()
special_event_interval = random.randint(20, 30)
maddie_display_time = -10
boost_end_time = -10
mute = False
running = True
show_start_screen = True

# Load leaderboard from file
leaderboard = []
if os.path.exists(LEADERBOARD_FILE):
    with open(LEADERBOARD_FILE, "r") as f:
        leaderboard = json.load(f)

def save_leaderboard():
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

def draw_text(text, x, y, font_obj=font, color=BLACK):
    for i, line in enumerate(text.splitlines()):
        text_obj = font_obj.render(line, True, color)
        screen.blit(text_obj, (x, y + i * 30))

def handle_input():
    global player_x, player_y, laser
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: player_x -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_x += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]: player_y -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: player_y += player_speed
    if keys[pygame.K_SPACE] and not laser:
        laser = [player_x + PLAYER_SIZE // 2 - LASER_SIZE[0] // 2, player_y]

def update_laser():
    global laser
    if laser:
        laser[0] += laser_speed
        if laser[0] > SCREEN_WIDTH:
            laser = None

def update_obstacles():
    global obstacles, obstacle_speed, tasks_avoided
    for obstacle in obstacles[:]:
        obstacle[0] -= obstacle_speed
        if obstacle[0] < -FLOWER_SIZE:
            obstacles.remove(obstacle)
            tasks_avoided += 1
    obstacle_speed += SPEED_INCREMENT / FPS

def spawn_obstacle():
    if random.random() < spawn_rate:
        y = random.randint(0, SCREEN_HEIGHT - FLOWER_SIZE)
        image = random.choice([
            [spreadsheet_img, SPREADSHEET_SIZE],
            [flowers_img, FLOWER_SIZE],
            [invitation_img, INVITATION_SIZE]
        ])
        obstacles.append([SCREEN_WIDTH, y, image[0], image[1]])

def check_collisions():
    global laser
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
            break
    return False

def show_leaderboard():
    screen.fill(BLACK)
    draw_text("LEADERBOARD - TASKS AVOIDED", 100, 100, font, WHITE)
    for i, entry in enumerate(leaderboard):
        name, score = entry
        draw_text(f"{i+1}. {name} - {score}", 120, 150 + i * 40, font, WHITE)
    draw_text("Press Enter to Restart", 120, 400, font, WHITE)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

def get_player_initials():
    name = ""
    while len(name) < 3:
        screen.fill(WHITE)
        draw_text("Enter Your Initials:", 120, SCREEN_HEIGHT // 2 - 40)
        draw_text(name, 120, SCREEN_HEIGHT // 2)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.unicode.upper() in string.ascii_uppercase and len(name) < 3:
                    name += event.unicode.upper()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
    return name

def reset_game():
    global player_x, player_y, laser, obstacles, obstacle_speed, spawn_rate
    global boost_end_time, tasks_avoided, special_event_timer

    pygame.mixer.music.stop()
    screen.fill(WHITE)
    draw_text("Oops. Responsibility caught up with Andreas.", 100, SCREEN_HEIGHT // 2 - 40)
    pygame.display.update()
    pygame.time.delay(3000)

    qualifies = len(leaderboard) < 5 or tasks_avoided > leaderboard[-1][1]
    if qualifies:
        name = get_player_initials()
        leaderboard.append((name, tasks_avoided))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        leaderboard[:] = leaderboard[:5]
        save_leaderboard()

    show_leaderboard()

    player_x = 10
    player_y = SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2
    laser = None
    obstacles.clear()
    obstacle_speed = 2
    spawn_rate = normal_spawn_rate
    boost_end_time = -10
    tasks_avoided = 0
    special_event_timer = time.time()

    if not mute:
        pygame.mixer.music.play(-1)

    pygame.time.delay(1000)

def handle_special_event():
    global maddie_display_time, boost_end_time, spawn_rate
    if time.time() - special_event_timer > special_event_interval:
        maddie_display_time = time.time()
        boost_end_time = maddie_display_time + 10
        spawn_rate = min(normal_spawn_rate * 3, 0.1)
        if not mute:
            try:
                special_sound = pygame.mixer.Sound("audio/special_day.mp3")
                special_sound.play()
            except Exception as e:
                print("Could not play special_day.mp3:", e)
        return True
    return False

def speed_up():
    global spawn_rate, obstacle_speed
    max_spawn_rate, max_speed = 0.12, 4
    spawn_rate = min(spawn_rate + (max_spawn_rate - normal_spawn_rate) / (30 * FPS), max_spawn_rate)
    obstacle_speed = min(obstacle_speed + (max_speed - 2) / (30 * FPS), max_speed)

def wrap_player():
    global player_x, player_y
    if player_y < -PLAYER_SIZE * 0.35:
        player_y = SCREEN_HEIGHT - PLAYER_SIZE * 0.65
    elif player_y + PLAYER_SIZE * 0.65 > SCREEN_HEIGHT:
        player_y = -PLAYER_SIZE * 0.35

    if player_x < 0:
        player_x = 0
    elif player_x > SCREEN_WIDTH - PLAYER_SIZE:
        player_x = SCREEN_WIDTH - PLAYER_SIZE

def show_start():
    screen.fill(WHITE)
    margin = 50
    title_font = get_font(42)
    subtitle_font = get_font(28)
    body_font = get_font(22)
    prompt_font = get_font(26)

    def wrap_text(text, font_obj, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font_obj.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def draw_wrapped_block(text, top_y, font_obj):
        wrapped_lines = []
        for line in text.splitlines():
            wrapped_lines.extend(wrap_text(line, font_obj, SCREEN_WIDTH - 2 * margin))

        for i, line in enumerate(wrapped_lines):
            surface = font_obj.render(line, True, BLACK)
            rect = surface.get_rect(center=(SCREEN_WIDTH // 2, top_y + i * 35))
            screen.blit(surface, rect)

    draw_wrapped_block("Special Day Dodger", margin, title_font)
    draw_wrapped_block("Help Andreas dodge the wedding responsibilities by avoiding or lasering them.", margin + 80, subtitle_font)
    draw_wrapped_block("Arrows to move.\nSpace bar to shoot.\nM to mute music.", margin + 200, body_font)
    draw_wrapped_block("Press Enter to Start.", margin + 340, prompt_font)

    pygame.display.update()

# Main loop
while running:
    if show_start_screen:
        show_start()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    show_start_screen = False
                elif event.key == pygame.K_m:
                    mute = not mute
                    if mute:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(-1)
        continue

    screen.fill(WHITE)
    handle_input()
    wrap_player()
    spawn_obstacle()
    update_obstacles()
    update_laser()

    if 15 < time.time() - special_event_timer < 45:
        speed_up()
    if handle_special_event():
        special_event_timer = time.time()
        special_event_interval = random.randint(20, 30)

    if time.time() > boost_end_time:
        spawn_rate = normal_spawn_rate

    if check_collisions():
        reset_game()
        continue

    screen.blit(andreas_img, (player_x, player_y))
    for obstacle in obstacles:
        screen.blit(obstacle[2], (obstacle[0], obstacle[1]))
    if laser:
        pygame.draw.rect(screen, BLACK, (*laser, *LASER_SIZE))
    if time.time() - maddie_display_time < 5:
        text_x = SCREEN_WIDTH - 270
        draw_text("IT'S MY SPECIAL", text_x, 120, small_font)
        draw_text("DAY!!!", text_x + 10, 150, small_font)
        screen.blit(maddie_img, (SCREEN_WIDTH - 220, SCREEN_HEIGHT // 2 - 100))

    draw_text(f"Tasks avoided: {tasks_avoided}", 20, 20)

    pygame.display.update()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            mute = not mute
            if mute:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)

pygame.quit()

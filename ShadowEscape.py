
import pygame
import random
from PIL import Image

pygame.init()
pygame.mixer.init()

# Game Settings
TILE_SIZE = 32
WINDOW_WIDTH = 1152
WINDOW_HEIGHT = 720
MOVE_DELAY = 150
ENEMY_MOVE_DELAY = 500
ANIMATION_SPEED = 150
TIME_LIMIT = 300
INITIAL_LIVES = 3
JUMP_SCARE_DURATION = 1000
ENEMY_POSITIONS = [(7, 3), (15, 9), (9, 15)]

# Colors
COLOR_WALL = (60, 60, 60)
COLOR_DOOR_LOCKED = (139, 69, 19)
COLOR_DOOR_OPEN = (34, 139, 34)
COLOR_KEY = (255, 215, 0)

MAP = [
    "#################D#################",
    "#P.....#...........................#",
    "#.#.##...###.#.###.#.###...#######.#",
    "#.#....#...#...#.#.#.#.#...#.....#.#",
    "#...#######.#.#.#..#.#.#...#.###.#.#",
    "#.#.......#.#.#.#.#.#.#.#.#.#.#.#.#",
    "#.#.#####.#.#.#.#.#.#.#.#.#.#.#.#.#",
    "#.#.#...#.#...#.#.#.#.#.#.#.#.#.#.#",
    "#.#.#.#.#.###.#.#.#.#.#.....#.#.#.#",
    "#...#.#.#.....#...#.#.#...#.#.#...#",
    "##.#.#.#.#####.#K###.#.#.#...#.###.#",
    "#..#.........#...#.#.#.#.#.......#",
    "#.#.###..#.#.#.#.#.#.#...#.#.#####.#",
    "#.#.....#.#...#.#.#.#.#.#.#........#",
    "#.#.###.#.#.#.#.#.#.#.#.#.#.#.#.#.#",
    "#.#.#...#.#.#......#.....#.#.#....#",
    "#.#.#.###.#.#####.#...#.#.#.#.#.#.#",
    "#.#........K.#........#.#.#.#.#.#.#",
    "#.#.#########.#####.#.#.#.#.#.#.#.#",
    "#...#.........#....#.#....#.#.#..K#",
    "###################################.#",
]

FONT_SMALL = pygame.font.SysFont(None, 24)
FONT = pygame.font.SysFont(None, 28)
FONT_LARGE = pygame.font.SysFont(None, 36, bold=True)

# Load Images
HEART_IMG = None
try:
    PLAYER_IMG = pygame.transform.scale(pygame.image.load("Character.png"), (TILE_SIZE, TILE_SIZE))
    GHOST_IMG = pygame.transform.scale(pygame.image.load("Ghost.png"), (TILE_SIZE, TILE_SIZE))
except:
    PLAYER_IMG = GHOST_IMG = None

try:
    HEART_IMG = pygame.transform.scale(pygame.image.load("heart.webp"), (36, 36))
except:
    HEART_IMG = None

# Load Background
BACKGROUND_IMAGE = None
BACKGROUND_START = None
try:
    bg = Image.open("background.avif").resize((WINDOW_WIDTH, WINDOW_HEIGHT - 60))
    BACKGROUND_IMAGE = pygame.image.fromstring(bg.tobytes(), bg.size, bg.mode)
    
    bg_full = Image.open("background.avif").resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    BACKGROUND_START = pygame.image.fromstring(bg_full.tobytes(), bg_full.size, bg_full.mode)
except:
    pass

# Load Audio Files
START_MUSIC = None
AMBIENT_MUSIC = None
JUMP_SCARE_SOUND = None

try:
    START_MUSIC = pygame.mixer.Sound("simplesound-horror-trailer-443327.mp3")
except:
    pass

try:
    AMBIENT_MUSIC = pygame.mixer.Sound("universfield-horror-background-atmosphere-025-499631.mp3")
except:
    pass

try:
    JUMP_SCARE_SOUND = pygame.mixer.Sound("mixkit-horror-swish-1495.wav")
except:
    pass

# Animation Frames
# Player frames for running animation
PLAYER_FRAMES = {
    'down': [PLAYER_IMG, PLAYER_IMG] if PLAYER_IMG else [None, None],
    'up': [PLAYER_IMG, PLAYER_IMG] if PLAYER_IMG else [None, None],
    'left': [PLAYER_IMG, PLAYER_IMG] if PLAYER_IMG else [None, None],
    'right': [PLAYER_IMG, PLAYER_IMG] if PLAYER_IMG else [None, None]
}

# Ghost frames with animation
GHOST_FRAMES = [GHOST_IMG, GHOST_IMG] if GHOST_IMG else [None, None]
GHOST_JUMPSCARE = GHOST_IMG if GHOST_IMG else None

# Utility Functions
def load_map():
    # Load the game map and return walls, keys, door, and player position.
    walls = []
    keys = []
    door = None
    player = None
    
    for y, row in enumerate(MAP):
        for x, tile in enumerate(row):
            if tile == "#":
                walls.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == "K":
                keys.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == "D":
                door = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            elif tile == "P":
                player = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    
    return walls, keys, door, player


def move_rect(rect, dx, dy, walls):
    # Move a rectangle with collision detection against walls.
    if dx == 0 and dy == 0:
        return rect
    
    candidate = rect.copy()
    candidate.x += dx
    candidate.y += dy
    
    for wall in walls:
        if candidate.colliderect(wall):
            return rect
    
    return candidate


def random_enemy_path(start, walls):
    #Calculate a random valid direction for enemy movement.
    directions = [(TILE_SIZE, 0), (-TILE_SIZE, 0), (0, TILE_SIZE), (0, -TILE_SIZE)]
    x, y = start
    random.shuffle(directions)
    
    for dx, dy in directions:
        candidate = pygame.Rect(x + dx, y + dy, TILE_SIZE, TILE_SIZE)
        if all(not candidate.colliderect(wall) for wall in walls):
            return dx, dy
    
    return 0, 0

def draw_text(screen, text, x, y, color=(255, 255, 255), font=FONT):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def draw_darkness(screen, player):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - 60), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 240))
    light_radius = TILE_SIZE * 3.5
    pygame.draw.circle(overlay, (0, 0, 0, 0), player.center, light_radius)
    pygame.draw.circle(overlay, (0, 0, 0, 120), player.center, light_radius, width=60)
    screen.blit(overlay, (0, 0))

def draw_player(screen, rect, frame, direction):
    if PLAYER_FRAMES[direction][frame % 2]:
        # Running animation with bobbing effect
        bob_offset = int(2 * ((frame // 2) % 2))
        bob_rect = rect.copy()
        bob_rect.y -= bob_offset
        screen.blit(PLAYER_FRAMES[direction][frame % 2], bob_rect)

def draw_enemy(screen, rect, frame):
    if GHOST_FRAMES[frame % 2]:
        # Ghost floating animation with scale and bob effect
        float_offset = int(3 * ((frame // 2) % 2))
        float_rect = rect.copy()
        float_rect.y -= float_offset
        
        # Add scale variation for pulsing effect
        scale_factor = 0.95 + (0.1 * ((frame // 2) % 2))
        scaled_size = int(TILE_SIZE * scale_factor)
        scaled_ghost = pygame.transform.scale(GHOST_FRAMES[frame % 2], (scaled_size, scaled_size))
        
        # Center the scaled ghost in the rect
        offset_x = (TILE_SIZE - scaled_size) // 2
        offset_y = (TILE_SIZE - scaled_size) // 2
        screen.blit(scaled_ghost, (float_rect.x + offset_x, float_rect.y + offset_y))

def draw_key(screen, rect):
    # Draw a fancy key design
    key_x, key_y = rect.centerx, rect.centery
    
    # Key head (circle)
    pygame.draw.circle(screen, COLOR_KEY, (key_x - 6, key_y), 6)
    pygame.draw.circle(screen, (200, 170, 0), (key_x - 6, key_y), 6, 2)
    
    # Key shaft (rectangle)
    pygame.draw.rect(screen, COLOR_KEY, (key_x - 2, key_y - 2, 10, 4))
    
    # Key teeth (two small rectangles)
    pygame.draw.rect(screen, COLOR_KEY, (key_x + 7, key_y - 1, 2, 2))
    pygame.draw.rect(screen, COLOR_KEY, (key_x + 7, key_y + 1, 2, 2))
    
    # Inner design on key head
    pygame.draw.circle(screen, (200, 170, 0), (key_x - 6, key_y), 3)

def draw_walls_with_bricks(screen, walls):
    for wall in walls:
        pygame.draw.rect(screen, COLOR_WALL, wall)
        brick_w, brick_h = 16, 10
        for y in range(int(wall.y), int(wall.y + wall.height), brick_h):
            for x in range(int(wall.x), int(wall.x + wall.width), brick_w):
                offset = brick_w // 2 if ((y - int(wall.y)) // brick_h) % 2 else 0
                pygame.draw.rect(screen, (40, 40, 40), (x + offset, y, brick_w, brick_h), 1)

def draw_door_design(screen, rect, is_locked):
    color = COLOR_DOOR_LOCKED if is_locked else COLOR_DOOR_OPEN
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 3)
    
    # Draw door panel lines
    center_x = rect.centerx
    center_y = rect.centery
    pygame.draw.line(screen, (80, 60, 40), (center_x, rect.top + 4), (center_x, rect.bottom - 4), 2)
    pygame.draw.line(screen, (80, 60, 40), (rect.left + 4, center_y), (rect.right - 4, center_y), 2)
    
    # Draw door handle
    handle_color = (200, 150, 50) if is_locked else (100, 200, 100)
    pygame.draw.circle(screen, handle_color, (rect.right - 8, center_y), 4)
    pygame.draw.circle(screen, (0, 0, 0), (rect.right - 8, center_y), 4, 1)

def draw_hearts(screen, lives):
    for i in range(INITIAL_LIVES):
        x = WINDOW_WIDTH - (INITIAL_LIVES * 45) - 15 + i * 45
        y = WINDOW_HEIGHT - 45
        
        if HEART_IMG:
            if i < lives:
                screen.blit(HEART_IMG, (x, y))
            else:
                gray_heart = HEART_IMG.copy()
                gray_heart.fill((100, 100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(gray_heart, (x, y))
        else:
            color = (255, 0, 0) if i < lives else (100, 100, 100)
            pygame.draw.circle(screen, color, (x - 3, y - 5), 4)
            pygame.draw.circle(screen, color, (x + 7, y - 5), 4)
            pygame.draw.polygon(screen, color, [
                (x - 6, y - 2),
                (x + 10, y - 2),
                (x + 2, y + 8)
            ])

def draw_start_screen(screen):
    if BACKGROUND_START:
        screen.blit(BACKGROUND_START, (0, 0))
    else:
        screen.fill((20, 20, 30))
    
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))
    
    title_font = pygame.font.SysFont(None, 72, bold=True)
    title = title_font.render("SHADOW ESCAPE", True, (150, 150, 150))
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 5))
    
    # Instructions
    instructions = [
        "INSTRUCTIONS:",
        "Use ARROW KEYS to move through the maze",
        "Collect all KEYS to unlock the door",
        "Avoid the GHOSTS or you'll lose a life",
        "You have 3 lives - escape before time runs out!"
    ]
    
    instr_font = pygame.font.SysFont(None, 20)
    y_offset = WINDOW_HEIGHT // 2 - 50
    for line in instructions:
        instr_text = instr_font.render(line, True, (200, 200, 200))
        screen.blit(instr_text, (WINDOW_WIDTH // 2 - instr_text.get_width() // 2, y_offset))
        y_offset += 30
    
    button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 120, 200, 60)
    pygame.draw.rect(screen, (50, 150, 50), button_rect)
    pygame.draw.rect(screen, (100, 255, 100), button_rect, 3)
    
    button_text = pygame.font.SysFont(None, 40, bold=True).render("START", True, (255, 255, 255))
    screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))
    
    pygame.display.flip()
    return button_rect

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Shadow Escape")
        self.clock = pygame.time.Clock()
        
        self.walls, self.keys, self.door, self.player = load_map()
        self.player_start_pos = self.player.copy()
        self.enemies = [pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE) for x, y in ENEMY_POSITIONS]
        self.enemy_dirs = [random_enemy_path((e.x, e.y), self.walls) for e in self.enemies]
        
        self.keys_needed = len(self.keys)
        self.collected_keys = 0
        self.timer = TIME_LIMIT * 1000
        self.lives = INITIAL_LIVES
        self.game_over = self.win = self.started = False
        self.move_timer = self.enemy_move_timer = 0
        self.player_animation_frame = self.player_animation_time = 0
        self.player_direction = 'down'
        self.enemy_animation_frame = self.enemy_animation_time = 0
        self.jump_scare_active = self.jump_scare_time = 0
        self.start_button_rect = None
        self.retry_button_rect = None
        self.ambient_music_playing = False

    def handle_start_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, False
            if event.type == pygame.MOUSEBUTTONDOWN and self.start_button_rect and self.start_button_rect.collidepoint(event.pos):
                return True, True
        return True, False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                if self.retry_button_rect and self.retry_button_rect.collidepoint(event.pos):
                    return self.reset_game()
            
            if event.type == pygame.KEYDOWN and not self.game_over:
                dx = dy = 0
                
                if event.key == pygame.K_LEFT:
                    dx, self.player_direction = -TILE_SIZE, 'left'
                elif event.key == pygame.K_RIGHT:
                    dx, self.player_direction = TILE_SIZE, 'right'
                elif event.key == pygame.K_UP:
                    dy, self.player_direction = -TILE_SIZE, 'up'
                elif event.key == pygame.K_DOWN:
                    dy, self.player_direction = TILE_SIZE, 'down'
                
                if (dx or dy) and self.move_timer >= MOVE_DELAY:
                    blocking = self.walls + ([self.door] if self.collected_keys < self.keys_needed else [])
                    new_player = move_rect(self.player, dx, dy, blocking)
                    if new_player != self.player:
                        self.player = new_player
                        self.move_timer = 0
        
        return True
    
    def reset_game(self):
        # Reset game state for retry
        self.walls, self.keys, self.door, self.player = load_map()
        self.player_start_pos = self.player.copy()
        self.enemies = [pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE) for x, y in ENEMY_POSITIONS]
        self.enemy_dirs = [random_enemy_path((e.x, e.y), self.walls) for e in self.enemies]
        
        self.collected_keys = 0
        self.timer = TIME_LIMIT * 1000
        self.lives = INITIAL_LIVES
        self.game_over = self.win = False
        self.move_timer = self.enemy_move_timer = 0
        self.player_animation_frame = self.player_animation_time = 0
        self.player_direction = 'down'
        self.enemy_animation_frame = self.enemy_animation_time = 0
        self.jump_scare_active = self.jump_scare_time = 0
        
        # Play ambient music again
        if AMBIENT_MUSIC:
            AMBIENT_MUSIC.play(-1)
        
        return True

    def update(self, dt):
        if self.jump_scare_active:
            self.jump_scare_time += dt
            if self.jump_scare_time >= JUMP_SCARE_DURATION:
                self.jump_scare_active = 0
                self.jump_scare_time = 0
        
        if self.game_over:
            return
        
        # Start ambient music if not playing
        if not self.ambient_music_playing and AMBIENT_MUSIC:
            AMBIENT_MUSIC.play(-1)
            self.ambient_music_playing = True
        
        self.timer -= dt
        self.move_timer += dt
        self.enemy_move_timer += dt
        self.player_animation_time += dt
        self.enemy_animation_time += dt
        
        if self.player_animation_time >= ANIMATION_SPEED:
            self.player_animation_frame += 1
            self.player_animation_time = 0
        if self.enemy_animation_time >= ANIMATION_SPEED:
            self.enemy_animation_frame += 1
            self.enemy_animation_time = 0
        
        if self.timer <= 0:
            self.game_over = True
        
        for key in self.keys[:]:
            if self.player.colliderect(key):
                self.keys.remove(key)
                self.collected_keys += 1
        
        if self.player.colliderect(self.door) and len(self.keys) == 0:
            self.game_over = True
            self.win = True
        
        # Check collision with ghosts every frame
        for enemy in self.enemies:
            if enemy.colliderect(self.player):
                self.jump_scare_active = 1
                self.jump_scare_time = 0
                
                # Play jump scare sound
                if JUMP_SCARE_SOUND:
                    JUMP_SCARE_SOUND.play()
                
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.player = self.player_start_pos.copy()
                break
        
        if self.enemy_move_timer >= ENEMY_MOVE_DELAY:
            for i, enemy in enumerate(self.enemies):
                if random.random() < 0.15:
                    self.enemy_dirs[i] = random_enemy_path((enemy.x, enemy.y), self.walls)
                dx, dy = self.enemy_dirs[i]
                next_enemy = move_rect(enemy, dx, dy, self.walls)
                if next_enemy == enemy:
                    self.enemy_dirs[i] = random_enemy_path((enemy.x, enemy.y), self.walls)
                else:
                    self.enemies[i] = next_enemy
            self.enemy_move_timer = 0

    def draw(self):
        if BACKGROUND_IMAGE:
            self.screen.blit(BACKGROUND_IMAGE, (0, 0))
        else:
            self.screen.fill((50, 50, 50))
        
        # Make background slightly transparent
        bg_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - 60), pygame.SRCALPHA)
        bg_overlay.fill((0, 0, 0, 20))
        self.screen.blit(bg_overlay, (0, 0))
        
        draw_walls_with_bricks(self.screen, self.walls)
        
        for key in self.keys:
            draw_key(self.screen, key)
        
        draw_door_design(self.screen, self.door, self.collected_keys < self.keys_needed)
        
        draw_player(self.screen, self.player, self.player_animation_frame, self.player_direction)
        for enemy in self.enemies:
            draw_enemy(self.screen, enemy, self.enemy_animation_frame)
        
        draw_darkness(self.screen, self.player)
        
        pygame.draw.rect(self.screen, (20, 20, 20), (0, WINDOW_HEIGHT - 60, WINDOW_WIDTH, 60))
        pygame.draw.line(self.screen, (80, 80, 80), (0, WINDOW_HEIGHT - 60), (WINDOW_WIDTH, WINDOW_HEIGHT - 60), 2)
        
        draw_text(self.screen, f"Keys: {self.collected_keys}/{self.keys_needed}", 10, WINDOW_HEIGHT - 25, COLOR_KEY, FONT_SMALL)
        
        mins, secs = max(0, self.timer // 60000), max(0, (self.timer % 60000) // 1000)
        draw_text(self.screen, f"Time: {mins:02d}:{secs:02d}", WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT - 25, (255, 200, 150), FONT_SMALL)
        
        draw_hearts(self.screen, self.lives)
        
        if self.jump_scare_active:
            progress = self.jump_scare_time / JUMP_SCARE_DURATION
            # Make ghost much bigger when popping up
            scale = 1 + (progress * 5) if progress < 0.5 else 1 + ((1 - progress) * 5)
            size = int(TILE_SIZE * 7 * scale)
            if GHOST_JUMPSCARE:
                ghost = pygame.transform.scale(GHOST_JUMPSCARE, (size, size))
                x = WINDOW_WIDTH // 2 - size // 2 + random.randint(-10, 10) if progress < 0.3 else WINDOW_WIDTH // 2 - size // 2
                y = WINDOW_HEIGHT // 2 - size // 2 - 30
                self.screen.blit(ghost, (x, y))
        
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            msg = "YOU ESCAPED!" if self.win else "GAME OVER"
            color = (0, 255, 0) if self.win else (255, 100, 100)
            text = FONT_LARGE.render(msg, True, color)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - 80))
            
            # Draw retry button
            retry_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 40, 200, 60)
            pygame.draw.rect(self.screen, (150, 100, 50), retry_rect)
            pygame.draw.rect(self.screen, (255, 200, 100), retry_rect, 3)
            
            retry_text = pygame.font.SysFont(None, 40, bold=True).render("RETRY", True, (255, 255, 255))
            self.screen.blit(retry_text, (retry_rect.centerx - retry_text.get_width() // 2, retry_rect.centery - retry_text.get_height() // 2))
            
            self.retry_button_rect = retry_rect
        
        pygame.display.flip()

    def run(self):
        running = True
        while running and not self.started:
            # Play start music on start screen
            if START_MUSIC and not self.ambient_music_playing:
                START_MUSIC.play()
                self.ambient_music_playing = True
            
            running, self.started = self.handle_start_input()
            self.start_button_rect = draw_start_screen(self.screen)
            self.clock.tick(60)
        
        # Stop start music and play ambient music
        if START_MUSIC:
            START_MUSIC.stop()
        
        while running:
            running = self.handle_input()
            self.update(self.clock.tick(60))
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    Game().run()


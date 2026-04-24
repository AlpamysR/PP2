import pygame
import random
import sys

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()

CELL            = 20
COLS            = 30
ROWS            = 25
WIDTH           = CELL * COLS
HEIGHT          = CELL * ROWS
FPS_BASE        = 8
FPS_STEP        = 2
FOODS_PER_LEVEL = 3   # foods needed to advance one level

# Maximum food items on screen at once
MAX_FOODS = 3

# Colours
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = ( 60, 200,  60)
DKGREEN = ( 30, 120,  30)
RED     = (220,  50,  50)
YELLOW  = (255, 220,   0)
GRAY    = (100, 100, 100)
BLUE    = ( 50, 150, 255)
ORANGE  = (255, 140,   0)
PURPLE  = (180,  50, 220)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

font_big   = pygame.font.SysFont("consolas", 36, bold=True)
font_med   = pygame.font.SysFont("consolas", 24)
font_small = pygame.font.SysFont("consolas", 18)
font_tiny  = pygame.font.SysFont("consolas", 13, bold=True)


# ── Food tier definitions ─────────────────────────────────────────────────────
# Each entry: (point_multiplier, colour, lifespan_seconds, label)
#   Normal  – common, moderate lifetime
#   Bonus   – uncommon, shorter lifetime, more points
#   Super   – rare, very short lifetime, many points
FOOD_TIERS = [
    (1,  YELLOW, 8.0,  "1×"),   # Normal – 60 % chance
    (3,  ORANGE, 5.0,  "3×"),   # Bonus  – 28 % chance
    (5,  PURPLE, 3.0,  "5×"),   # Super  – 12 % chance
]
FOOD_SPAWN_WEIGHTS = [0.60, 0.28, 0.12]


# ── Food class ────────────────────────────────────────────────────────────────

class Food:
    """
    A food item placed on the grid with a weight and a disappear timer.

    Attributes
    ----------
    pos        : (col, row) grid position
    multiplier : score multiplier (1, 3, or 5)
    color      : display colour that signals the tier
    lifespan   : total seconds before the food disappears on its own
    age        : seconds elapsed since spawning
    eaten      : True once the snake eats it
    """

    def __init__(self, pos, fps):
        self.pos   = pos
        tier = random.choices(FOOD_TIERS, weights=FOOD_SPAWN_WEIGHTS)[0]
        self.multiplier, self.color, self.lifespan, self.label = tier
        self.age   = 0.0        # seconds alive
        self.eaten = False
        self._fps  = fps        # stored so tick() knows frame duration

    def tick(self, fps):
        """Advance age by one frame. Call once per game tick."""
        self.age += 1.0 / fps

    @property
    def expired(self):
        """True when the food's lifespan has run out."""
        return self.age >= self.lifespan

    @property
    def time_left(self):
        return max(0.0, self.lifespan - self.age)

    def draw(self, surface):
        """Draw food circle with a shrinking timer arc around it."""
        col, row = self.pos
        cx = col * CELL + CELL // 2
        cy = row * CELL + CELL // 2
        r  = CELL // 2 - 2

        # Background circle
        pygame.draw.circle(surface, self.color, (cx, cy), r)

        # Timer arc: full circle = full lifespan; shrinks as time passes
        fraction = self.time_left / self.lifespan
        if fraction < 1.0:
            import math
            arc_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            # Draw a dark overlay arc to show how much time is left
            end_angle = -math.pi / 2 + 2 * math.pi * fraction
            pygame.draw.arc(surface, BLACK, arc_rect,
                            end_angle, 3 * math.pi / 2, 3)

        # Multiplier label (tiny text)
        lbl = font_tiny.render(self.label, True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2,
                           cy - lbl.get_height() // 2))


# ── Helper functions ──────────────────────────────────────────────────────────

def draw_cell(surface, color, col, row):
    """Draw a filled grid cell with a 1-px dark border."""
    rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BLACK, rect, 1)


def random_empty_pos(snake_body, food_positions):
    """Return a (col, row) not on the snake, not on a wall, not on food."""
    occupied = set(snake_body) | set(food_positions)
    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)
        if (col, row) not in occupied:
            return col, row


def draw_walls():
    """Draw 1-cell-thick border walls."""
    for c in range(COLS):
        draw_cell(screen, GRAY, c, 0)
        draw_cell(screen, GRAY, c, ROWS - 1)
    for r in range(1, ROWS - 1):
        draw_cell(screen, GRAY, 0, r)
        draw_cell(screen, GRAY, COLS - 1, r)


def draw_hud(score, level, foods_in_level):
    """HUD bar: score on the left, level centre, progress on the right."""
    hud = pygame.Surface((WIDTH, 28), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 160))
    screen.blit(hud, (0, 0))

    screen.blit(font_small.render(f"Score: {score}", True, WHITE), (6, 5))
    lv = font_small.render(f"Level: {level}", True, YELLOW)
    screen.blit(lv, (WIDTH // 2 - lv.get_width() // 2, 5))
    prog = f"{'■' * foods_in_level}{'□' * (FOODS_PER_LEVEL - foods_in_level)}"
    pr = font_small.render(prog, True, BLUE)
    screen.blit(pr, (WIDTH - pr.get_width() - 6, 5))


def show_message(title, subtitle=""):
    """Centred game-over overlay."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    t = font_big.render(title, True, RED)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 40))
    if subtitle:
        s = font_med.render(subtitle, True, WHITE)
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()


# ── Main game loop ─────────────────────────────────────────────────────────────

def game():
    # Snake starts in the middle, moving right
    sc, sr = COLS // 2, ROWS // 2
    snake      = [(sc - i, sr) for i in range(3)]
    direction  = (1, 0)
    next_dir   = direction

    score          = 0
    level          = 1
    foods_in_level = 0

    foods      = []   # list of Food objects currently on the grid
    food_timer = 0    # frames since last food spawn attempt
    game_over  = False

    # Spawn initial food
    pos = random_empty_pos(snake, [])
    foods.append(Food(pos, FPS_BASE))

    while True:
        fps = FPS_BASE + (level - 1) * FPS_STEP
        clock.tick(fps)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r: game(); return
                    if event.key == pygame.K_q: pygame.quit(); sys.exit()
                else:
                    if event.key == pygame.K_UP    and direction != (0,  1):
                        next_dir = (0, -1)
                    elif event.key == pygame.K_DOWN  and direction != (0, -1):
                        next_dir = (0,  1)
                    elif event.key == pygame.K_LEFT  and direction != (1,  0):
                        next_dir = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        next_dir = (1,  0)

        if game_over:
            show_message("GAME OVER",
                         f"Score: {score}  Level: {level}   R=restart  Q=quit")
            continue

        # ── Tick existing foods (advance their age) ──────────────────────────
        for f in foods:
            f.tick(fps)
        # Remove foods that have expired (disappeared due to timer)
        foods = [f for f in foods if not f.expired and not f.eaten]

        # Spawn a new food if fewer than MAX_FOODS are present
        food_timer += 1
        if len(foods) < MAX_FOODS and food_timer > fps // 2:
            food_timer = 0
            taken = [f.pos for f in foods]
            pos   = random_empty_pos(snake, taken)
            foods.append(Food(pos, fps))

        # ── Move snake ───────────────────────────────────────────────────────
        direction = next_dir
        hc, hr    = snake[0]
        new_head  = (hc + direction[0], hr + direction[1])

        # Wall collision
        nc, nr = new_head
        if nc <= 0 or nc >= COLS - 1 or nr <= 0 or nr >= ROWS - 1:
            game_over = True; continue

        # Self collision
        if new_head in snake:
            game_over = True; continue

        snake.insert(0, new_head)

        # Check if head landed on any food
        ate = None
        for f in foods:
            if new_head == f.pos:
                ate = f; break

        if ate:
            ate.eaten       = True
            score          += 10 * level * ate.multiplier   # weighted score
            foods_in_level += 1
            if foods_in_level >= FOODS_PER_LEVEL:
                level          += 1
                foods_in_level  = 0
            # Don't pop tail → snake grows
        else:
            snake.pop()   # no food → keep length constant

        # ── Draw ─────────────────────────────────────────────────────────────
        screen.fill(BLACK)
        draw_walls()

        # Snake body
        for i, (c, r) in enumerate(snake):
            draw_cell(screen, GREEN if i > 0 else DKGREEN, c, r)

        # All food items (each shows its colour + timer arc + label)
        for f in foods:
            f.draw(screen)

        draw_hud(score, level, foods_in_level)
        pygame.display.flip()


if __name__ == "__main__":
    game()
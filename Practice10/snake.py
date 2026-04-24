import pygame
import random
import sys

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()

# Window / grid constants
CELL      = 20          # size of one grid cell in pixels
COLS      = 30          # number of columns
ROWS      = 25          # number of rows
WIDTH     = CELL * COLS
HEIGHT    = CELL * ROWS
FPS_BASE  = 4        # starting frames-per-second (snake speed)
FPS_STEP  = 1           # extra FPS gained per level
FOODS_PER_LEVEL = 3     # foods needed to advance one level

# Colours
BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = ( 60, 200,  60)
DKGREEN= ( 30, 120,  30)
RED    = (220,  50,  50)
YELLOW = (255, 220,   0)
GRAY   = (100, 100, 100)
BLUE   = ( 50, 150, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

# Fonts
font_big  = pygame.font.SysFont("consolas", 36, bold=True)
font_med  = pygame.font.SysFont("consolas", 24)
font_small= pygame.font.SysFont("consolas", 18)


# ── Helpers ───────────────────────────────────────────────────────────────────

def draw_cell(surface, color, col, row):
    """Draw a filled grid cell with a 1-px dark border."""
    rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BLACK, rect, 1)


def random_food(snake_body):
    """Return (col, row) that is NOT on the snake and NOT on the border wall."""
    while True:
        col = random.randint(1, COLS - 2)   # keep 1 cell away from each wall
        row = random.randint(1, ROWS - 2)
        if (col, row) not in snake_body:
            return col, row


def draw_hud(score, level, foods_in_level):
    """Render score, level, and a small progress bar at the top of the screen."""
    # Semi-transparent HUD bar
    hud = pygame.Surface((WIDTH, 28), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 160))
    screen.blit(hud, (0, 0))

    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    level_surf = font_small.render(f"Level: {level}", True, YELLOW)
    # Progress dots toward next level
    prog = f"Next lv: {'■' * foods_in_level}{'□' * (FOODS_PER_LEVEL - foods_in_level)}"
    prog_surf = font_small.render(prog, True, BLUE)

    screen.blit(score_surf, (6, 5))
    screen.blit(level_surf, (WIDTH // 2 - level_surf.get_width() // 2, 5))
    screen.blit(prog_surf,  (WIDTH - prog_surf.get_width() - 6, 5))


def draw_walls():
    """Draw a border wall one cell thick around the playing area."""
    for c in range(COLS):
        draw_cell(screen, GRAY, c, 0)
        draw_cell(screen, GRAY, c, ROWS - 1)
    for r in range(1, ROWS - 1):
        draw_cell(screen, GRAY, 0, r)
        draw_cell(screen, GRAY, COLS - 1, r)


def show_message(title, subtitle=""):
    """Overlay a centred message box (used for Game-Over / pause)."""
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
    # ── State ──
    # Snake starts in the middle, moving right; stored as list of (col, row)
    start_col, start_row = COLS // 2, ROWS // 2
    snake  = [(start_col - i, start_row) for i in range(3)]  # head first
    direction  = (1, 0)   # (dc, dr)  →  moving right
    next_dir   = direction

    score          = 0
    level          = 1
    foods_in_level = 0        # foods eaten since last level-up

    food = random_food(set(snake))

    running    = True
    game_over  = False

    while running:
        fps = FPS_BASE + (level - 1) * FPS_STEP   # speed increases with level
        clock.tick(fps)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        game()   # restart by recursion
                        return
                    if event.key == pygame.K_q:
                        pygame.quit(); sys.exit()
                else:
                    # Prevent reversing directly into yourself
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

        # ── Update ──────────────────────────────────────────────────────────
        direction = next_dir
        head_col, head_row = snake[0]
        new_head = (head_col + direction[0], head_row + direction[1])

        # 1. Border (wall) collision → game over
        nc, nr = new_head
        if nc <= 0 or nc >= COLS - 1 or nr <= 0 or nr >= ROWS - 1:
            game_over = True
            continue

        # 2. Self collision → game over
        if new_head in snake:
            game_over = True
            continue

        # Move: prepend new head
        snake.insert(0, new_head)

        # 3. Food eaten
        if new_head == food:
            score         += 10 * level   # more points at higher levels
            foods_in_level += 1

            # Level-up check
            if foods_in_level >= FOODS_PER_LEVEL:
                level         += 1
                foods_in_level = 0

            # Place new food NOT on wall AND NOT on snake
            food = random_food(set(snake))
        else:
            snake.pop()   # no food eaten → remove tail to keep length constant

        # ── Draw ────────────────────────────────────────────────────────────
        screen.fill(BLACK)
        draw_walls()

        # Draw snake (head slightly lighter)
        for i, (c, r) in enumerate(snake):
            color = GREEN if i > 0 else DKGREEN
            draw_cell(screen, color, c, r)

        # Draw food as a yellow circle
        fx = food[0] * CELL + CELL // 2
        fy = food[1] * CELL + CELL // 2
        pygame.draw.circle(screen, YELLOW, (fx, fy), CELL // 2 - 2)

        draw_hud(score, level, foods_in_level)
        pygame.display.flip()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game()
import pygame
import random
import sys

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()

WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()
FPS   = 60

# Colours
BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (100, 100, 100)
DKGRAY = ( 50,  50,  50)
RED    = (220,  50,  50)
BLUE   = ( 50, 130, 230)
YELLOW = (255, 220,   0)
GREEN  = ( 60, 200,  60)
ORANGE = (255, 140,   0)
SILVER = (200, 200, 210)
GOLD   = (255, 200,   0)
BRONZE = (180, 100,  30)

font_big   = pygame.font.SysFont("consolas", 42, bold=True)
font_med   = pygame.font.SysFont("consolas", 26)
font_small = pygame.font.SysFont("consolas", 20)
font_tiny  = pygame.font.SysFont("consolas", 14, bold=True)

# Road geometry
ROAD_LEFT  = 80
ROAD_RIGHT = WIDTH - 80
ROAD_W     = ROAD_RIGHT - ROAD_LEFT

# Lane centres (3 lanes)
LANES = [ROAD_LEFT + ROAD_W // 6,
         ROAD_LEFT + ROAD_W // 2,
         ROAD_LEFT + ROAD_W * 5 // 6]

# ── Every N coins collected, enemy speed increases by ENEMY_BOOST ─────────────
COINS_PER_BOOST = 5      # collect this many coins → next speed boost triggers
ENEMY_BOOST     = 0.8    # added to road_speed per boost level


# ── Coin tier definitions ─────────────────────────────────────────────────────
# Tuple: (point_value, face_colour, ring_colour, label_text)
COIN_TYPES = [
    (1,  BRONZE, (120, 70,  20), "1"),   # Bronze – common,   worth 1 pt
    (3,  SILVER, (150, 150, 160), "3"),  # Silver – uncommon, worth 3 pts
    (5,  GOLD,   (200, 160,   0), "5"),  # Gold   – rare,     worth 5 pts
]
# Weighted spawn probabilities (must sum to 1.0)
COIN_SPAWN_WEIGHTS = [0.60, 0.28, 0.12]


# ── Car class ─────────────────────────────────────────────────────────────────

class Car:
    """Rectangle car with a body colour and a windscreen highlight."""
    W, H = 40, 70

    def __init__(self, lane, color, y=None):
        self.lane  = lane
        self.color = color
        self.x     = LANES[lane] - self.W // 2
        self.y     = y if y is not None else HEIGHT + self.H
        self.speed = 0   # assigned externally for enemy cars

    def draw(self, surface):
        rect = pygame.Rect(self.x, int(self.y), self.W, self.H)
        pygame.draw.rect(surface, self.color, rect, border_radius=6)
        ws = pygame.Rect(self.x + 5, int(self.y) + 8, self.W - 10, 16)
        pygame.draw.rect(surface, (180, 220, 255), ws, border_radius=3)

    def get_rect(self):
        return pygame.Rect(self.x, int(self.y), self.W, self.H)


# ── Coin class ────────────────────────────────────────────────────────────────

class Coin:
    """
    A road coin with a randomised weight (point value).

    Tiers and spawn probabilities:
      Bronze (1 pt)  – 60 %
      Silver (3 pts) – 28 %
      Gold   (5 pts) – 12 %

    Higher-value coins have a distinct colour so the player can react quickly.
    """
    RADIUS = 13

    def __init__(self, road_speed):
        self.lane  = random.randint(0, 2)
        self.x     = LANES[self.lane]
        self.y     = float(-self.RADIUS * 2)   # start just above the screen
        self.speed = road_speed
        self.collected = False

        # Pick a tier using weighted random choice
        tier = random.choices(COIN_TYPES, weights=COIN_SPAWN_WEIGHTS)[0]
        self.value, self.face_color, self.ring_color, self.label = tier

    def update(self):
        """Scroll the coin downward."""
        self.y += self.speed

    def draw(self, surface):
        if self.collected:
            return
        cx, cy = self.x, int(self.y)
        pygame.draw.circle(surface, self.ring_color, (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, self.face_color, (cx, cy), self.RADIUS - 3)
        lbl = font_tiny.render(self.label, True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width()  // 2,
                           cy - lbl.get_height() // 2))

    def get_rect(self):
        r = self.RADIUS
        return pygame.Rect(self.x - r, int(self.y) - r, r * 2, r * 2)

    def is_off_screen(self):
        return self.y > HEIGHT + self.RADIUS * 2


# ── Road drawing ──────────────────────────────────────────────────────────────

def draw_road(surface, stripe_offset):
    """Draw the scrolling road with dashed lane dividers."""
    surface.fill(GREEN)
    pygame.draw.rect(surface, DKGRAY, (ROAD_LEFT, 0, ROAD_W, HEIGHT))
    pygame.draw.rect(surface, GRAY,   (ROAD_LEFT,      0, 8, HEIGHT))
    pygame.draw.rect(surface, GRAY,   (ROAD_RIGHT - 8, 0, 8, HEIGHT))
    stripe_h, gap = 40, 30
    period = stripe_h + gap
    for lx in [LANES[0] + Car.W // 2 + 10, LANES[1] + Car.W // 2 + 10]:
        for top in range(-period + int(stripe_offset) % period,
                         HEIGHT + period, period):
            pygame.draw.rect(surface, WHITE, (lx, top, 4, stripe_h))


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud(surface, score, coin_score, boost_level, coins_to_next):
    """
    Top-left   – distance score
    Top-right  – coin score (weighted points) + current boost level
    Small bar  – progress toward the next enemy speed-up
    """
    surface.blit(font_small.render(f"Score: {score}", True, WHITE),
                 (ROAD_LEFT + 6, 8))
    surface.blit(font_small.render(f"Coins: {coin_score} pts", True, GOLD),
                 (WIDTH - font_small.size(f"Coins: {coin_score} pts")[0] - 10, 8))
    boost_txt = f"Boost lv: {boost_level}"
    surface.blit(font_small.render(boost_txt, True, ORANGE),
                 (WIDTH - font_small.size(boost_txt)[0] - 10, 30))

    # Progress bar: coins collected since last boost / COINS_PER_BOOST
    filled = COINS_PER_BOOST - coins_to_next
    bar_w = 80
    bar_x = WIDTH - bar_w - 10
    bar_y = 54
    pygame.draw.rect(surface, GRAY,   (bar_x, bar_y, bar_w, 6))
    pygame.draw.rect(surface, ORANGE, (bar_x, bar_y,
                                       int(bar_w * filled / COINS_PER_BOOST), 6))


# ── Main game loop ─────────────────────────────────────────────────────────────

def game():
    player       = Car(lane=1, color=BLUE, y=HEIGHT - Car.H - 20)
    enemies      = []
    coins        = []
    enemy_timer  = 0
    coin_timer   = 0
    road_speed   = 5.0
    stripe_offset= 0.0
    score        = 0      # distance-based (increments every frame)
    coin_score   = 0      # weighted points from collected coins
    coin_count   = 0      # raw number of coins collected
    boost_level  = 0      # how many speed boosts have triggered so far
    coins_to_next_boost = COINS_PER_BOOST  # coins still needed for next boost
    game_over    = False

    def reset():
        nonlocal player, enemies, coins, enemy_timer, coin_timer, road_speed
        nonlocal stripe_offset, score, coin_score, coin_count
        nonlocal boost_level, coins_to_next_boost, game_over
        player              = Car(lane=1, color=BLUE, y=HEIGHT - Car.H - 20)
        enemies = []; coins = []
        enemy_timer = 0;  coin_timer = 0
        road_speed   = 5.0; stripe_offset = 0.0
        score = 0;  coin_score = 0;  coin_count = 0
        boost_level = 0;  coins_to_next_boost = COINS_PER_BOOST
        game_over = False

    while True:
        clock.tick(FPS)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:  reset();  continue
                    if event.key == pygame.K_q:  pygame.quit(); sys.exit()
                else:
                    if event.key in (pygame.K_LEFT, pygame.K_a) and player.lane > 0:
                        player.lane -= 1
                        player.x = LANES[player.lane] - Car.W // 2
                    if event.key in (pygame.K_RIGHT, pygame.K_d) and player.lane < 2:
                        player.lane += 1
                        player.x = LANES[player.lane] - Car.W // 2

        # ── Game-over screen ─────────────────────────────────────────────────
        if game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            screen.blit(ov, (0, 0))
            screen.blit(font_big.render("GAME OVER", True, RED),
                        (WIDTH//2 - font_big.size("GAME OVER")[0]//2, HEIGHT//2 - 80))
            screen.blit(font_med.render(f"Distance: {score // 10} m", True, WHITE),
                        (WIDTH//2 - font_med.size(f"Distance: {score//10} m")[0]//2,
                         HEIGHT//2 - 10))
            screen.blit(font_med.render(f"Coins: {coin_score} pts", True, GOLD),
                        (WIDTH//2 - font_med.size(f"Coins: {coin_score} pts")[0]//2,
                         HEIGHT//2 + 35))
            screen.blit(font_small.render("R = restart    Q = quit", True, GRAY),
                        (WIDTH//2 - font_small.size("R = restart    Q = quit")[0]//2,
                         HEIGHT//2 + 85))
            pygame.display.flip()
            continue

        # ── Update ──────────────────────────────────────────────────────────
        score += 1
        # Road speed: base growth with distance + boost from collected coins
        road_speed = 5.0 + score / 400.0 + boost_level * ENEMY_BOOST
        stripe_offset += road_speed

        # Spawn enemy cars (interval shrinks as score grows)
        enemy_timer += 1
        if enemy_timer >= max(35, 90 - score // 120):
            enemy_timer = 0
            e = Car(lane=random.randint(0, 2),
                    color=random.choice([RED, ORANGE, WHITE]),
                    y=-Car.H)
            e.speed = road_speed + random.uniform(0.5, 2.5)
            enemies.append(e)

        # Spawn coins at random intervals
        coin_timer += 1
        if coin_timer >= random.randint(80, 190):
            coin_timer = 0
            coins.append(Coin(road_speed=road_speed))

        # Move & cull enemies
        for e in enemies: e.y += e.speed
        enemies = [e for e in enemies if e.y < HEIGHT + Car.H]

        # Move & cull coins
        for c in coins: c.update()
        coins = [c for c in coins if not c.is_off_screen() and not c.collected]

        # Collision: player ↔ enemy → game over
        for e in enemies:
            if player.get_rect().colliderect(e.get_rect()):
                game_over = True

        # Collision: player ↔ coin → collect
        pr = player.get_rect()
        for c in coins:
            if pr.colliderect(c.get_rect()):
                c.collected  = True
                coin_score  += c.value   # weighted points
                coin_count  += 1         # raw count for boost tracking

                # Every COINS_PER_BOOST coins → increase enemy speed
                if coin_count >= coins_to_next_boost:
                    boost_level         += 1
                    coins_to_next_boost += COINS_PER_BOOST

        # ── Draw ─────────────────────────────────────────────────────────────
        draw_road(screen, stripe_offset)
        for e in enemies: e.draw(screen)
        for c in coins:   c.draw(screen)
        player.draw(screen)
        draw_hud(screen, score // 10, coin_score, boost_level,
                 coins_to_next_boost - coin_count)
        pygame.display.flip()


if __name__ == "__main__":
    game()
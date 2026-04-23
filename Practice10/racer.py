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

font_big   = pygame.font.SysFont("consolas", 42, bold=True)
font_med   = pygame.font.SysFont("consolas", 26)
font_small = pygame.font.SysFont("consolas", 20)

# Road geometry
ROAD_LEFT  = 80
ROAD_RIGHT = WIDTH - 80
ROAD_W     = ROAD_RIGHT - ROAD_LEFT

# Lane centres (3 lanes)
LANES = [ROAD_LEFT + ROAD_W // 6,
         ROAD_LEFT + ROAD_W // 2,
         ROAD_LEFT + ROAD_W * 5 // 6]


# ── Car class ─────────────────────────────────────────────────────────────────

class Car:
    """Simple rectangle car with a colour."""
    W, H = 40, 70

    def __init__(self, lane, color, y=None):
        self.lane  = lane
        self.color = color
        self.x     = LANES[lane] - self.W // 2
        self.y     = y if y is not None else HEIGHT + self.H
        self.speed = 0   # set externally for enemies

    def draw(self, surface):
        rect = pygame.Rect(self.x, int(self.y), self.W, self.H)
        pygame.draw.rect(surface, self.color, rect, border_radius=6)
        # Windscreen
        ws = pygame.Rect(self.x + 5, int(self.y) + 8, self.W - 10, 16)
        pygame.draw.rect(surface, (180, 220, 255), ws, border_radius=3)

    def get_rect(self):
        return pygame.Rect(self.x, int(self.y), self.W, self.H)


# ── Coin class ────────────────────────────────────────────────────────────────

class Coin:
    """A yellow circle coin that appears on the road randomly."""
    RADIUS = 12

    def __init__(self, speed):
        self.lane  = random.randint(0, 2)
        self.x     = LANES[self.lane]
        self.y     = -self.RADIUS * 2       # start just above screen
        self.speed = speed
        self.collected = False

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        if not self.collected:
            pygame.draw.circle(surface, YELLOW,
                               (self.x, int(self.y)), self.RADIUS)
            pygame.draw.circle(surface, ORANGE,
                               (self.x, int(self.y)), self.RADIUS, 3)
            # Dollar sign
            label = font_small.render("$", True, BLACK)
            surface.blit(label, (self.x - label.get_width()  // 2,
                                 int(self.y) - label.get_height() // 2))

    def get_rect(self):
        r = self.RADIUS
        return pygame.Rect(self.x - r, int(self.y) - r, r * 2, r * 2)

    def is_off_screen(self):
        return self.y > HEIGHT + self.RADIUS * 2


# ── Road stripe helper ─────────────────────────────────────────────────────────

def draw_road(surface, stripe_offset):
    """Draw road surface and scrolling lane-divider stripes."""
    # Grass on both sides
    surface.fill(GREEN)
    # Road rectangle
    pygame.draw.rect(surface, DKGRAY,
                     (ROAD_LEFT, 0, ROAD_W, HEIGHT))
    # Kerb strips
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT,      0, 8, HEIGHT))
    pygame.draw.rect(surface, GRAY, (ROAD_RIGHT - 8, 0, 8, HEIGHT))
    # Lane dividers (dashed)
    stripe_h, gap = 40, 30
    period = stripe_h + gap
    for lane_x in [LANES[0] + Car.W // 2 + 10, LANES[1] + Car.W // 2 + 10]:
        for top in range(-period + int(stripe_offset) % period,
                         HEIGHT + period, period):
            pygame.draw.rect(surface, WHITE,
                             (lane_x, top, 4, stripe_h))


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud(surface, score, coins):
    """Display score (distance) on left and coin count in top-right corner."""
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    # Coin icon + count in the top-right corner
    coin_surf  = font_small.render(f"Coins: {coins}", True, YELLOW)
    surface.blit(score_surf, (ROAD_LEFT + 6, 8))
    surface.blit(coin_surf,  (WIDTH - coin_surf.get_width() - 10, 8))


# ── Main game loop ─────────────────────────────────────────────────────────────

def game():
    # Player car (middle lane, near bottom)
    player = Car(lane=1, color=BLUE,
                 y=HEIGHT - Car.H - 20)

    enemies      = []     # list of Car objects
    coins        = []     # list of Coin objects

    enemy_timer  = 0      # frames since last enemy spawn
    coin_timer   = 0      # frames since last coin spawn

    road_speed   = 5      # how fast the road scrolls (increases over time)
    stripe_offset= 0.0

    score        = 0      # distance-based score
    coin_count   = 0      # number of collected coins
    game_over    = False

    def restart():
        nonlocal player, enemies, coins, enemy_timer, coin_timer
        nonlocal road_speed, stripe_offset, score, coin_count, game_over
        player        = Car(lane=1, color=BLUE, y=HEIGHT - Car.H - 20)
        enemies       = []; coins = []
        enemy_timer   = 0;  coin_timer = 0
        road_speed    = 5;  stripe_offset = 0.0
        score = 0;          coin_count = 0
        game_over     = False

    while True:
        clock.tick(FPS)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r: restart(); continue
                    if event.key == pygame.K_q:
                        pygame.quit(); sys.exit()
                else:
                    # Move player between lanes
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        if player.lane > 0:
                            player.lane -= 1
                            player.x = LANES[player.lane] - Car.W // 2
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        if player.lane < 2:
                            player.lane += 1
                            player.x = LANES[player.lane] - Car.W // 2

        if game_over:
            # Show overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            t = font_big.render("GAME OVER", True, RED)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
            s = font_med.render(f"Score: {score}   Coins: {coin_count}", True, WHITE)
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2))
            h = font_small.render("R = restart    Q = quit", True, GRAY)
            screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()
            continue

        # ── Update ──────────────────────────────────────────────────────────
        score        += 1
        road_speed    = 5 + score // 300   # gradually speed up
        stripe_offset += road_speed

        # Spawn enemy cars
        enemy_timer += 1
        if enemy_timer > max(40, 90 - score // 100):   # spawn faster over time
            enemy_timer = 0
            lane  = random.randint(0, 2)
            enemy = Car(lane=lane,
                        color=random.choice([RED, ORANGE, WHITE]),
                        y=-Car.H)
            enemy.speed = road_speed + random.uniform(0, 3)
            enemies.append(enemy)

        # Spawn coins randomly (~every 2-4 seconds)
        coin_timer += 1
        if coin_timer > random.randint(90, 200):
            coin_timer = 0
            coins.append(Coin(speed=road_speed))

        # Move enemies
        for e in enemies:
            e.y += e.speed
        enemies = [e for e in enemies if e.y < HEIGHT + Car.H]

        # Move coins
        for c in coins:
            c.update()
        coins = [c for c in coins
                 if not c.is_off_screen() and not c.collected]

        # Collision: player vs enemies
        for e in enemies:
            if player.get_rect().colliderect(e.get_rect()):
                game_over = True

        # Collision: player vs coins
        player_rect = player.get_rect()
        for c in coins:
            if player_rect.colliderect(c.get_rect()):
                c.collected = True
                coin_count  += 1

        # ── Draw ────────────────────────────────────────────────────────────
        draw_road(screen, stripe_offset)

        for e in enemies: e.draw(screen)
        for c in coins:   c.draw(screen)
        player.draw(screen)

        draw_hud(screen, score // 10, coin_count)   # score in "meters"
        pygame.display.flip()


if __name__ == "__main__":
    game()
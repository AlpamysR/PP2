"""
racer.py — Game logic: player, traffic, obstacles, power-ups, coins, road events.
Covers Tasks 3.1 (Race Track), 3.2 (Traffic & Obstacles),
3.3 (Power-Ups), 3.4 (Score & Distance).
"""

import pygame
import random

# ── Window / Road Layout ──────────────────────────────────────────────────────
WINDOW_W   = 860
WINDOW_H   = 680
ROAD_LEFT  = 130
ROAD_RIGHT = 730
ROAD_W     = ROAD_RIGHT - ROAD_LEFT          # 600 px
NUM_LANES  = 5
LANE_W     = ROAD_W // NUM_LANES             # 120 px
LANE_CENTERS = [ROAD_LEFT + LANE_W * i + LANE_W // 2
                for i in range(NUM_LANES)]   # [190, 310, 430, 550, 670]

FINISH_DISTANCE = 2000   # metres to "finish line"

# ── Colours ───────────────────────────────────────────────────────────────────
C_GRASS     = (34,  110,  34)
C_ROAD      = (55,   55,  55)
C_ROAD_EDGE = (255, 255, 255)
C_DASH      = (240, 200,  50)
C_BLACK     = (0,     0,   0)
C_WHITE     = (255, 255, 255)
C_GRAY      = (120, 120, 120)
C_DARK      = (30,   30,  30)
C_YELLOW    = (240, 200,  50)
C_GREEN     = (60,  200,  80)

CAR_COLORS = {
    "red":    (220,  50,  50),
    "blue":   ( 50, 110, 230),
    "green":  ( 40, 190,  70),
    "yellow": (240, 200,  50),
    "purple": (160,  80, 220),
}

TRAFFIC_PALETTE = [
    (220, 50,  50),
    (50,  80, 220),
    (40, 180,  70),
    (220,140,  40),
    (180, 60, 200),
    (60, 200, 200),
]

# ── Sizes ─────────────────────────────────────────────────────────────────────
PLAYER_W,  PLAYER_H  = 40, 68
TRAFFIC_W, TRAFFIC_H = 40, 68
POWERUP_S = 36
COIN_R    = 10

# ── Speed constants ───────────────────────────────────────────────────────────
BASE_SPEED       = 4.5
MAX_SPEED        = 13.0
NITRO_MULT       = 1.85
NITRO_DURATION   = 4.0    # seconds
OIL_SLOW_TIME    = 2.2    # seconds
POWERUP_TIMEOUT  = 9.0    # seconds on road before disappearing

# ── Difficulty presets ────────────────────────────────────────────────────────
DIFFICULTY = {
    "easy":   dict(traffic_rate=90,  obstacle_rate=130, coin_rate=38),
    "medium": dict(traffic_rate=55,  obstacle_rate=85,  coin_rate=50),
    "hard":   dict(traffic_rate=32,  obstacle_rate=52,  coin_rate=65),
}


# ─────────────────────────────────────────────────────────────────────────────
#  Helper – draw a top-down car
# ─────────────────────────────────────────────────────────────────────────────
def _draw_car(surf, cx, cy, w, h, body_color, *, facing_down=True):
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, body_color, r, border_radius=7)
    # windshield
    if facing_down:
        ws = pygame.Rect(r.left + 5, r.top + 6, w - 10, h // 3)
    else:
        ws = pygame.Rect(r.left + 5, r.bottom - h // 3 - 6, w - 10, h // 3)
    pygame.draw.rect(surf, (170, 215, 255), ws, border_radius=3)
    # wheels
    ww, wh = 8, 14
    for dx, dy in [(-w // 2 - 4, -h // 4), (w // 2 - 4, -h // 4),
                    (-w // 2 - 4,  h // 4), (w // 2 - 4,  h // 4)]:
        pygame.draw.rect(surf, C_DARK,
                         (cx + dx, cy + dy - wh // 2, ww, wh), border_radius=2)


# ─────────────────────────────────────────────────────────────────────────────
#  Player
# ─────────────────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, color):
        self.lane          = 2                        # start in centre lane
        self.x             = float(LANE_CENTERS[2])
        self.y             = float(WINDOW_H - 130)
        self.color         = color
        self.shield        = False
        self.nitro         = False
        self.nitro_timer   = 0.0
        self._lane_cd      = 0.0                     # lane-switch cooldown

    # ── Smooth lane target ───────────────────────────────────────────────────
    @property
    def target_x(self):
        return float(LANE_CENTERS[self.lane])

    def update(self, dt: float, keys):
        # Lane switching
        if self._lane_cd > 0:
            self._lane_cd -= dt
        if self._lane_cd <= 0:
            if keys[pygame.K_LEFT] and self.lane > 0:
                self.lane     -= 1
                self._lane_cd  = 0.18
            elif keys[pygame.K_RIGHT] and self.lane < NUM_LANES - 1:
                self.lane     += 1
                self._lane_cd  = 0.18

        # Glide toward target x
        self.x += (self.target_x - self.x) * min(1.0, dt * 14)

        # Nitro timer
        if self.nitro:
            self.nitro_timer -= dt
            if self.nitro_timer <= 0:
                self.nitro = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - PLAYER_W // 2,
                           int(self.y) - PLAYER_H // 2,
                           PLAYER_W, PLAYER_H)

    def apply_nitro(self):
        self.nitro       = True
        self.nitro_timer = NITRO_DURATION

    def apply_shield(self):
        self.shield = True

    def take_hit(self) -> bool:
        """Returns True if player dies (False if shield absorbs the hit)."""
        if self.shield:
            self.shield = False
            return False
        return True

    def draw(self, surf):
        _draw_car(surf, int(self.x), int(self.y),
                  PLAYER_W, PLAYER_H, self.color, facing_down=False)
        if self.shield:
            pygame.draw.circle(surf, (100, 160, 255),
                               (int(self.x), int(self.y)),
                               max(PLAYER_W, PLAYER_H) // 2 + 9, 3)
        if self.nitro:
            flame_y = int(self.y) + PLAYER_H // 2 + 4
            for i in range(3):
                pygame.draw.ellipse(
                    surf, (255, random.randint(100, 200), 0),
                    (int(self.x) - 7 + i * 6, flame_y, 8, random.randint(8, 18)))


# ─────────────────────────────────────────────────────────────────────────────
#  Traffic car  (Task 3.2)
# ─────────────────────────────────────────────────────────────────────────────
class TrafficCar:
    def __init__(self, lane: int, scroll_speed: float):
        self.lane   = lane
        self.x      = float(LANE_CENTERS[lane])
        self.y      = float(-TRAFFIC_H // 2 - 10)
        self.color  = random.choice(TRAFFIC_PALETTE)
        # Traffic comes toward player: moves faster than the road scroll
        self.own_speed = random.uniform(1.0, 3.5)
        self._scroll = scroll_speed

    def update(self, scroll_speed: float):
        self.y += scroll_speed + self.own_speed

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - TRAFFIC_W // 2,
                           int(self.y) - TRAFFIC_H // 2,
                           TRAFFIC_W, TRAFFIC_H)

    def off_screen(self) -> bool:
        return self.y > WINDOW_H + TRAFFIC_H

    def draw(self, surf):
        _draw_car(surf, int(self.x), int(self.y),
                  TRAFFIC_W, TRAFFIC_H, self.color, facing_down=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Road Obstacle  (Task 3.1 + 3.2)
# ─────────────────────────────────────────────────────────────────────────────
OBSTACLE_TYPES = ["barrier", "oil", "pothole"]

class Obstacle:
    def __init__(self, lane: int):
        self.type = random.choice(OBSTACLE_TYPES)
        self.lane = lane
        self.x    = float(LANE_CENTERS[lane])
        self.y    = float(-60)
        if self.type == "barrier":
            self.w, self.h = LANE_W - 10, 22
        elif self.type == "oil":
            self.w, self.h = 70, 38
        else:                                  # pothole
            self.w, self.h = 54, 30

    def update(self, scroll_speed: float):
        self.y += scroll_speed          # fixed on road — scrolls with it

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - self.w // 2,
                           int(self.y) - self.h // 2,
                           self.w, self.h)

    def off_screen(self) -> bool:
        return self.y > WINDOW_H + 80

    def draw(self, surf, font):
        if self.type == "barrier":
            pygame.draw.rect(surf, (210, 70, 70),
                             self.get_rect(), border_radius=5)
            t = font.render("BARRIER", True, C_WHITE)
            surf.blit(t, t.get_rect(center=(int(self.x), int(self.y))))

        elif self.type == "oil":
            pygame.draw.ellipse(surf, (15, 15, 55), self.get_rect())
            inner = pygame.Rect(int(self.x) - 20, int(self.y) - 9, 40, 18)
            pygame.draw.ellipse(surf, (40, 40, 110), inner)
            t = font.render("OIL", True, (180, 180, 255))
            surf.blit(t, t.get_rect(center=(int(self.x), int(self.y))))

        else:                                  # pothole
            pygame.draw.ellipse(surf, (22, 18, 18), self.get_rect())
            pygame.draw.ellipse(surf, (38, 30, 28),
                                self.get_rect().inflate(-12, -8))
            t = font.render("!", True, C_YELLOW)
            surf.blit(t, t.get_rect(center=(int(self.x), int(self.y))))


# ─────────────────────────────────────────────────────────────────────────────
#  Power-Up  (Task 3.3)
# ─────────────────────────────────────────────────────────────────────────────
POWERUP_COLORS = {"nitro": (240, 200, 50), "shield": (60, 120, 230), "repair": (60, 200, 80)}
POWERUP_ICONS  = {"nitro": "N",            "shield": "S",            "repair": "R"}

class PowerUp:
    COLORS = POWERUP_COLORS
    ICONS  = POWERUP_ICONS

    def __init__(self, lane: int):
        self.type  = random.choice(["nitro", "shield", "repair"])
        self.lane  = lane
        self.x     = float(LANE_CENTERS[lane])
        self.y     = float(-POWERUP_S // 2 - 10)
        self.timer = POWERUP_TIMEOUT   # disappears after timeout (Task 3.3 rule 2)

    def update(self, scroll_speed: float, dt: float):
        self.y    += scroll_speed
        self.timer -= dt

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - POWERUP_S // 2,
                           int(self.y) - POWERUP_S // 2,
                           POWERUP_S, POWERUP_S)

    def expired(self) -> bool:
        return self.timer <= 0 or self.y > WINDOW_H + POWERUP_S

    def draw(self, surf, font):
        color = POWERUP_COLORS[self.type]
        r = self.get_rect()
        pygame.draw.rect(surf, color, r, border_radius=9)
        pygame.draw.rect(surf, C_WHITE, r, width=2, border_radius=9)
        t = font.render(POWERUP_ICONS[self.type], True, C_WHITE)
        surf.blit(t, t.get_rect(center=r.center))
        # Timeout bar below
        bw = int(POWERUP_S * max(0, self.timer / POWERUP_TIMEOUT))
        pygame.draw.rect(surf, (80, 80, 80), (r.left, r.bottom + 3, POWERUP_S, 4))
        pygame.draw.rect(surf, color,        (r.left, r.bottom + 3, bw, 4))


# ─────────────────────────────────────────────────────────────────────────────
#  Coin
# ─────────────────────────────────────────────────────────────────────────────
class Coin:
    def __init__(self, lane: int):
        self.lane = lane
        self.x    = float(LANE_CENTERS[lane])
        self.y    = float(-COIN_R - 5)

    def update(self, scroll_speed: float):
        self.y += scroll_speed

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - COIN_R,
                           int(self.y) - COIN_R,
                           COIN_R * 2, COIN_R * 2)

    def off_screen(self) -> bool:
        return self.y > WINDOW_H + COIN_R * 2

    def draw(self, surf):
        pygame.draw.circle(surf, (255, 215, 0), (int(self.x), int(self.y)), COIN_R)
        pygame.draw.circle(surf, (200, 160,  0), (int(self.x), int(self.y)), COIN_R, 2)
        pygame.draw.circle(surf, (255, 240, 120), (int(self.x) - 3, int(self.y) - 3), 3)


# ─────────────────────────────────────────────────────────────────────────────
#  Road Event  (Task 3.1 – nitro strip / speed bump)
# ─────────────────────────────────────────────────────────────────────────────
class RoadEvent:
    def __init__(self):
        self.type = random.choice(["nitro_strip", "speed_bump", "nitro_strip"])
        self.y    = float(-20)

    def update(self, scroll_speed: float):
        self.y += scroll_speed

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(ROAD_LEFT, int(self.y) - 10, ROAD_W, 20)

    def off_screen(self) -> bool:
        return self.y > WINDOW_H + 30

    def draw(self, surf, font):
        if self.type == "nitro_strip":
            s = pygame.Surface((ROAD_W, 20), pygame.SRCALPHA)
            s.fill((255, 220, 0, 160))
            surf.blit(s, (ROAD_LEFT, int(self.y) - 10))
            t = font.render("NITRO STRIP", True, C_BLACK)
            surf.blit(t, t.get_rect(center=(ROAD_LEFT + ROAD_W // 2, int(self.y))))
        else:
            pygame.draw.rect(surf, (130, 100, 60),
                             (ROAD_LEFT, int(self.y) - 8, ROAD_W, 16),
                             border_radius=4)
            t = font.render("SPEED BUMP", True, C_WHITE)
            surf.blit(t, t.get_rect(center=(ROAD_LEFT + ROAD_W // 2, int(self.y))))


# ─────────────────────────────────────────────────────────────────────────────
#  Game  (orchestrator)
# ─────────────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, settings: dict):
        diff_key       = settings.get("difficulty", "medium")
        self._diff     = DIFFICULTY[diff_key]
        car_color      = CAR_COLORS.get(settings.get("car_color", "red"), (220, 50, 50))

        self.player    = Player(car_color)

        # Scroll / physics
        self.scroll_speed = BASE_SPEED
        self._dash_off    = 0.0       # road-dash animation offset

        # Metrics
        self.distance         = 0.0   # metres
        self.score            = 0
        self.coins_collected  = 0
        self.level            = 1
        self._level_timer     = 0.0

        # Entities
        self.traffic     : list[TrafficCar] = []
        self.obstacles   : list[Obstacle]   = []
        self.powerups    : list[PowerUp]    = []
        self.coins       : list[Coin]       = []
        self.road_events : list[RoadEvent]  = []

        # Spawn timers (frames)
        self._t_traffic  = 0
        self._t_obstacle = 0
        self._t_powerup  = 0
        self._t_coin     = 0
        self._t_event    = 0

        # Active power-up state (Task 3.3 – only one at a time)
        self.active_powerup : dict | None = None  # {"type": str, "timer": float}

        # Slow / effects
        self._oil_slow = 0.0    # seconds of slowdown remaining

        # Game state
        self.game_over = False
        self.won       = False

        # Fonts (initialised after pygame.init in main)
        self._fnt_md = pygame.font.SysFont("segoeui", 22)
        self._fnt_sm = pygame.font.SysFont("segoeui", 17)

    # ── Main update ──────────────────────────────────────────────────────────
    def update(self, dt: float, keys):
        if self.game_over:
            return

        # Difficulty scaling (Task 3.2) – increase level every 30 s
        self._level_timer += dt
        if self._level_timer >= 30.0:
            self._level_timer = 0.0
            self.level       += 1
            self.scroll_speed = min(BASE_SPEED + self.level * 0.6, MAX_SPEED)

        # Effective speed
        spd = self.scroll_speed
        if self.active_powerup and self.active_powerup["type"] == "nitro":
            spd *= NITRO_MULT
        if self._oil_slow > 0:
            spd *= 0.5
            self._oil_slow -= dt

        # Player
        self.player.update(dt, keys)

        # Scroll metrics
        self._dash_off  = (self._dash_off + spd) % 80
        self.distance  += spd / 50.0          # pixels → rough metres
        self.score      = int(self.coins_collected * 10 + self.distance * 2)

        # Win condition
        if self.distance >= FINISH_DISTANCE:
            self.won      = True
            self.game_over = True
            return

        # Spawn
        self._spawn_traffic(spd)
        self._spawn_obstacles()
        self._spawn_powerups()
        self._spawn_coins()
        self._spawn_events()

        # Update entities
        for e in self.traffic:     e.update(spd)
        for e in self.obstacles:   e.update(spd)
        for e in self.powerups:    e.update(spd, dt)
        for e in self.coins:       e.update(spd)
        for e in self.road_events: e.update(spd)

        # Remove off-screen / expired
        self.traffic     = [e for e in self.traffic     if not e.off_screen()]
        self.obstacles   = [e for e in self.obstacles   if not e.off_screen()]
        self.powerups    = [e for e in self.powerups    if not e.expired()]
        self.coins       = [e for e in self.coins       if not e.off_screen()]
        self.road_events = [e for e in self.road_events if not e.off_screen()]

        # Active power-up countdown
        if self.active_powerup and self.active_powerup["timer"] > 0:
            self.active_powerup["timer"] -= dt
            if self.active_powerup["timer"] <= 0 and self.active_powerup["type"] == "nitro":
                self.active_powerup = None
                self.player.nitro   = False

        # Collisions
        self._check_collisions()

    # ── Spawners ─────────────────────────────────────────────────────────────
    def _spawn_traffic(self, spd):
        rate = max(18, self._diff["traffic_rate"] - self.level * 4)
        self._t_traffic += 1
        if self._t_traffic < rate:
            return
        self._t_traffic = 0
        lane = random.randint(0, NUM_LANES - 1)
        # Safe spawn – don't pick player's lane too often
        if lane == self.player.lane and random.random() < 0.65:
            others = [l for l in range(NUM_LANES) if l != self.player.lane]
            lane   = random.choice(others)
        # Don't stack at top
        for t in self.traffic:
            if t.lane == lane and t.y < TRAFFIC_H * 2:
                return
        self.traffic.append(TrafficCar(lane, spd))

    def _spawn_obstacles(self):
        rate = max(28, self._diff["obstacle_rate"] - self.level * 6)
        self._t_obstacle += 1
        if self._t_obstacle < rate:
            return
        self._t_obstacle = 0
        lane = random.randint(0, NUM_LANES - 1)
        # Safe spawn – avoid directly spawning on player (Task 3.2)
        if (lane == self.player.lane and
                self.player.y < WINDOW_H * 0.65 and
                random.random() < 0.75):
            return
        self.obstacles.append(Obstacle(lane))

    def _spawn_powerups(self):
        self._t_powerup += 1
        if self._t_powerup < 200 or self.powerups:
            if self._t_powerup >= 200 and self.powerups:
                self._t_powerup = 160   # keep checking
            return
        self._t_powerup = 0
        lane = random.randint(0, NUM_LANES - 1)
        self.powerups.append(PowerUp(lane))

    def _spawn_coins(self):
        rate = self._diff["coin_rate"]
        self._t_coin += 1
        if self._t_coin < rate:
            return
        self._t_coin = 0
        lane = random.randint(0, NUM_LANES - 1)
        self.coins.append(Coin(lane))

    def _spawn_events(self):
        self._t_event += 1
        if self._t_event < 320:
            return
        self._t_event = 0
        self.road_events.append(RoadEvent())

    # ── Collision detection ───────────────────────────────────────────────────
    def _check_collisions(self):
        pr = self.player.get_rect()

        # Traffic
        for car in self.traffic[:]:
            if pr.colliderect(car.get_rect()):
                if self.player.take_hit():
                    self.game_over = True
                    return
                self.traffic.remove(car)

        # Obstacles
        for obs in self.obstacles[:]:
            if pr.colliderect(obs.get_rect()):
                if obs.type == "oil":
                    self._oil_slow = OIL_SLOW_TIME
                    self.obstacles.remove(obs)
                elif self.player.take_hit():
                    self.game_over = True
                    return
                else:
                    self.obstacles.remove(obs)   # shield absorbed it

        # Power-ups (Task 3.3 – only one active at a time)
        for pu in self.powerups[:]:
            if pr.colliderect(pu.get_rect()):
                if self.active_powerup is None:  # rule: one at a time
                    self._apply_powerup(pu.type)
                    self.powerups.remove(pu)

        # Coins
        for c in self.coins[:]:
            if pr.colliderect(c.get_rect()):
                self.coins_collected += 1
                self.score += 10
                self.coins.remove(c)

        # Road events
        for ev in self.road_events:
            if pr.colliderect(ev.get_rect()):
                if ev.type == "nitro_strip" and self.active_powerup is None:
                    self.active_powerup = {"type": "nitro", "timer": 3.0}
                    self.player.apply_nitro()
                elif ev.type == "speed_bump":
                    self._oil_slow = max(self._oil_slow, 1.2)

    def _apply_powerup(self, ptype: str):
        """Apply a collected power-up (Task 3.3)."""
        if ptype == "nitro":
            self.active_powerup = {"type": "nitro", "timer": NITRO_DURATION}
            self.player.apply_nitro()
        elif ptype == "shield":
            self.player.apply_shield()
            self.active_powerup = {"type": "shield", "timer": -1}   # until hit
        elif ptype == "repair":
            # Instant: clear player's lane obstacles + reset oil slow
            self.obstacles = [o for o in self.obstacles if o.lane != self.player.lane]
            self._oil_slow = 0.0
            # No active slot consumed (instant effect)

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface):
        # Grass
        surf.fill(C_GRASS)
        # Road body
        pygame.draw.rect(surf, C_ROAD, (ROAD_LEFT, 0, ROAD_W, WINDOW_H))
        # Road edges
        pygame.draw.line(surf, C_ROAD_EDGE, (ROAD_LEFT, 0),  (ROAD_LEFT, WINDOW_H),  4)
        pygame.draw.line(surf, C_ROAD_EDGE, (ROAD_RIGHT, 0), (ROAD_RIGHT, WINDOW_H), 4)

        # Dashed lane dividers
        for i in range(1, NUM_LANES):
            lx = ROAD_LEFT + LANE_W * i
            y  = int(-self._dash_off) % 80
            while y < WINDOW_H:
                pygame.draw.line(surf, C_DASH, (lx, y), (lx, y + 40), 2)
                y += 80

        # Road events
        for ev in self.road_events:
            ev.draw(surf, self._fnt_sm)

        # Coins
        for c in self.coins:
            c.draw(surf)

        # Obstacles
        for obs in self.obstacles:
            obs.draw(surf, self._fnt_sm)

        # Power-ups
        for pu in self.powerups:
            pu.draw(surf, self._fnt_sm)

        # Traffic
        for car in self.traffic:
            car.draw(surf)

        # Player
        self.player.draw(surf)

        # HUD
        self._draw_hud(surf)

    def _draw_hud(self, surf: pygame.Surface):
        # Top bar
        bar = pygame.Surface((WINDOW_W, 52), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 150))
        surf.blit(bar, (0, 0))

        # Score
        surf.blit(self._fnt_md.render(f"Score: {self.score}", True, C_WHITE), (10, 14))

        # Distance – centre (Task 3.4)
        dist_txt = f"{int(self.distance)} m / {FINISH_DISTANCE} m"
        ds = self._fnt_md.render(dist_txt, True, C_WHITE)
        surf.blit(ds, ds.get_rect(midtop=(WINDOW_W // 2, 8)))

        # Distance progress bar
        bx, by, bw, bh = WINDOW_W // 2 - 140, 34, 280, 8
        pygame.draw.rect(surf, (80, 80, 80), (bx, by, bw, bh), border_radius=4)
        prog = min(1.0, self.distance / FINISH_DISTANCE)
        pygame.draw.rect(surf, C_GREEN, (bx, by, int(bw * prog), bh), border_radius=4)

        # Coins (top right)
        ct = self._fnt_md.render(f"Coins: {self.coins_collected}", True, (255, 215, 0))
        surf.blit(ct, ct.get_rect(topright=(WINDOW_W - 10, 14)))

        # Level
        lt = self._fnt_sm.render(f"Lv {self.level}", True, C_YELLOW)
        surf.blit(lt, lt.get_rect(topright=(WINDOW_W - 10, 38)))

        # Active power-up HUD (Task 3.3 rule 3 – display active + remaining time)
        if self.active_powerup:
            ptype = self.active_powerup["type"]
            color = POWERUP_COLORS[ptype]
            hb = pygame.Surface((190, 48), pygame.SRCALPHA)
            hb.fill((0, 0, 0, 160))
            surf.blit(hb, (8, WINDOW_H - 58))
            pygame.draw.rect(surf, color, (8, WINDOW_H - 58, 190, 48), width=2, border_radius=7)
            lbl = self._fnt_md.render(f"⚡ {ptype.upper()}", True, color)
            surf.blit(lbl, (14, WINDOW_H - 54))
            timer = self.active_powerup["timer"]
            if timer > 0:
                ts = self._fnt_sm.render(f"{timer:.1f} s", True, C_WHITE)
                surf.blit(ts, (14, WINDOW_H - 30))
            else:
                surf.blit(self._fnt_sm.render("active", True, C_WHITE), (14, WINDOW_H - 30))

        # Slow indicator
        if self._oil_slow > 0:
            sl = self._fnt_sm.render(f"SLOW  {self._oil_slow:.1f}s", True, (130, 130, 255))
            surf.blit(sl, (8, WINDOW_H - 75))

        # Shield indicator
        if self.player.shield:
            sh = self._fnt_sm.render("🛡 SHIELD ACTIVE", True, (100, 160, 255))
            surf.blit(sh, sh.get_rect(bottomright=(WINDOW_W - 10, WINDOW_H - 10)))

    # ── Result ────────────────────────────────────────────────────────────────
    def get_result(self) -> dict:
        return {
            "score":    self.score,
            "distance": round(self.distance),
            "coins":    self.coins_collected,
            "won":      self.won,
        }
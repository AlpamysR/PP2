import pygame


# ── Constants ─────────────────────────────────────────────────────────────────
BALL_RADIUS  = 25          # radius = 25  →  50×50 pixels bounding box
BALL_COLOR   = (220,  40,  40)   # red
SHADOW_COLOR = (180,  20,  20)   # darker red for 3-D shadow
SHINE_COLOR  = (255, 140, 140)   # lighter red for highlight
STEP         = 20          # pixels per key press


class Ball:
    """
    A red ball (radius 25) that moves by STEP pixels per key press
    and is clamped to the screen boundaries.
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.sw = screen_width
        self.sh = screen_height
        self.r  = BALL_RADIUS

        # Start at the centre of the screen
        self.x  = screen_width  // 2
        self.y  = screen_height // 2

    # ── Movement ──────────────────────────────────────────────────────────────
    def move(self, dx: int, dy: int) -> bool:
        """
        Try to move the ball by (dx, dy).
        Returns True if the move was applied, False if it was blocked
        by a boundary (ball stays in place).
        """
        new_x = self.x + dx
        new_y = self.y + dy

        # Boundary check: ignore moves that would push ball off-screen
        if new_x - self.r < 0 or new_x + self.r > self.sw:
            return False
        if new_y - self.r < 0 or new_y + self.r > self.sh:
            return False

        self.x = new_x
        self.y = new_y
        return True

    def handle_key(self, key) -> bool:
        """
        Map arrow keys → move().
        Returns True if the ball actually moved.
        """
        if   key == pygame.K_UP:    return self.move( 0,   -STEP)
        elif key == pygame.K_DOWN:  return self.move( 0,   +STEP)
        elif key == pygame.K_LEFT:  return self.move(-STEP,  0)
        elif key == pygame.K_RIGHT: return self.move(+STEP,  0)
        return False

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface):
        cx, cy, r = self.x, self.y, self.r

        # Drop shadow (slightly offset, semi-transparent via a temp surface)
        shadow_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 60),
                           (r + 5, r + 6), r)
        screen.blit(shadow_surf, (cx - r - 3, cy - r - 3))

        # Main ball body
        pygame.draw.circle(screen, BALL_COLOR, (cx, cy), r)

        # Inner darker ring for depth
        pygame.draw.circle(screen, SHADOW_COLOR, (cx, cy), r, 3)

        # Shine / specular highlight (small bright oval top-left)
        shine_x = cx - r // 3
        shine_y = cy - r // 3
        pygame.draw.ellipse(screen, SHINE_COLOR,
                            (shine_x - 6, shine_y - 4, 12, 8))

    # ── Position info ─────────────────────────────────────────────────────────
    @property
    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)
import pygame
import math
import datetime


def create_mickey_hand(length: int, color: tuple, width: int = 14) -> pygame.Surface:
    """
    Draws a Mickey-Mouse-style gloved hand surface programmatically
    (used when no image file is found).
    The hand points UPWARD on the surface so rotation works correctly.
    """
    size = length + 40
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    cx = size // 2

    # Arm / stick
    arm_top = 10
    arm_bottom = length
    pygame.draw.line(surf, color, (cx, arm_top), (cx, arm_bottom), width)

    # Glove (circle at the tip)
    glove_r = 18
    pygame.draw.circle(surf, color, (cx, arm_top), glove_r)

    # Finger bumps
    finger_color = (*color[:3], 200)
    for offset in (-12, 0, 12):
        pygame.draw.circle(surf, finger_color,
                           (cx + offset, arm_top - glove_r + 4), 9)

    return surf


class Clock:
    """
    Handles all clock rendering logic.
    Right hand → minutes hand
    Left hand  → seconds hand
    """

    BACKGROUND   = (30, 30, 30)
    FACE_COLOR   = (240, 240, 200)
    BORDER_COLOR = (180, 140,  60)
    TEXT_COLOR   = (20,  20,  20)
    MINUTE_COLOR = (220,  50,  50)   # red  – right hand
    SECOND_COLOR = (50,  100, 220)   # blue – left hand
    CENTER_DOT   = (255, 255, 255)

    def __init__(self, screen: pygame.Surface, hand_image_path: str | None = None):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.cx = self.width  // 2
        self.cy = self.height // 2
        self.radius = min(self.width, self.height) // 2 - 40

        self.font_time  = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_label = pygame.font.SysFont("Arial", 22)

        # Try to load a real image; fall back to drawn hand
        self.minute_hand = self._load_or_draw(hand_image_path, self.MINUTE_COLOR, int(self.radius * 0.75))
        self.second_hand = self._load_or_draw(hand_image_path, self.SECOND_COLOR, int(self.radius * 0.85))

    # ------------------------------------------------------------------
    def _load_or_draw(self, path, color, length) -> pygame.Surface:
        if path:
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (40, length))
                return img
            except Exception:
                pass
        return create_mickey_hand(length, color)

    # ------------------------------------------------------------------
    def _rotate_and_blit(self, surface: pygame.Surface, angle_deg: float):
        """
        Rotates `surface` (which points UPWARD at angle=0) by `angle_deg`
        clockwise, then blits it centred on the clock face.
        pygame.transform.rotate goes counter-clockwise, so we negate.
        """
        rotated = pygame.transform.rotate(surface, -angle_deg)
        rect = rotated.get_rect(center=(self.cx, self.cy))
        self.screen.blit(rotated, rect)

    # ------------------------------------------------------------------
    def _draw_face(self):
        # Outer border
        pygame.draw.circle(self.screen, self.BORDER_COLOR,
                           (self.cx, self.cy), self.radius + 8)
        # Face
        pygame.draw.circle(self.screen, self.FACE_COLOR,
                           (self.cx, self.cy), self.radius)

        # Hour marks (every 5 min = 30°)
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            outer = self.radius - 8
            inner = self.radius - 22
            x1 = self.cx + int(math.cos(angle) * outer)
            y1 = self.cy + int(math.sin(angle) * outer)
            x2 = self.cx + int(math.cos(angle) * inner)
            y2 = self.cy + int(math.sin(angle) * inner)
            pygame.draw.line(self.screen, self.BORDER_COLOR, (x1, y1), (x2, y2), 4)

        # Minute tick marks
        for i in range(60):
            if i % 5 == 0:
                continue
            angle = math.radians(i * 6 - 90)
            outer = self.radius - 8
            inner = self.radius - 14
            x1 = self.cx + int(math.cos(angle) * outer)
            y1 = self.cy + int(math.sin(angle) * outer)
            x2 = self.cx + int(math.cos(angle) * inner)
            y2 = self.cy + int(math.sin(angle) * inner)
            pygame.draw.line(self.screen, (160, 120, 40), (x1, y1), (x2, y2), 1)

    # ------------------------------------------------------------------
    def _draw_labels(self, minutes: int, seconds: int):
        # Digital readout at the bottom
        time_str  = f"{minutes:02d}:{seconds:02d}"
        time_surf = self.font_time.render(time_str, True, self.TEXT_COLOR)
        time_rect = time_surf.get_rect(center=(self.cx, self.cy + self.radius - 45))
        self.screen.blit(time_surf, time_rect)

        # Legend
        min_lbl  = self.font_label.render("Right = Minutes", True, self.MINUTE_COLOR)
        sec_lbl  = self.font_label.render("Left  = Seconds", True, self.SECOND_COLOR)
        self.screen.blit(min_lbl, (10, self.height - 55))
        self.screen.blit(sec_lbl, (10, self.height - 28))

    # ------------------------------------------------------------------
    def draw(self):
        now     = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        # Angles (0° = 12 o'clock = pointing up)
        minute_angle = minutes * 6          # 360° / 60
        second_angle = seconds * 6

        self.screen.fill(self.BACKGROUND)
        self._draw_face()

        # Hands (draw minutes first so seconds appear on top)
        self._rotate_and_blit(self.minute_hand, minute_angle)
        self._rotate_and_blit(self.second_hand, second_angle)

        # Centre dot
        pygame.draw.circle(self.screen, self.CENTER_DOT,
                           (self.cx, self.cy), 10)
        pygame.draw.circle(self.screen, self.BORDER_COLOR,
                           (self.cx, self.cy), 10, 2)

        self._draw_labels(minutes, seconds)
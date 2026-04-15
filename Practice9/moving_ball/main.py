import sys
import pygame
from ball import Ball


# ── Window configuration ──────────────────────────────────────────────────────
WINDOW_TITLE  = "Moving Ball Game"
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60

# ── Colours ───────────────────────────────────────────────────────────────────
BG_COLOR      = (255, 255, 255)   # white background
GRID_COLOR    = (230, 230, 230)   # subtle grid
TEXT_COLOR    = (60,  60,  60)
ACCENT_COLOR  = (220,  40,  40)
BORDER_COLOR  = (200, 200, 200)


def draw_grid(screen: pygame.Surface, step: int = 40):
    """Draw a light grid to make movement more visible."""
    w, h = screen.get_size()
    for x in range(0, w, step):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, h))
    for y in range(0, h, step):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (w, y))


def draw_hud(screen: pygame.Surface,
             font_info: pygame.font.Font,
             font_small: pygame.font.Font,
             ball: Ball):
    """Draw position info and keyboard hints."""
    w, h = screen.get_size()

    # ── Top-left: coordinates ─────────────────────────────────────────────
    bx, by = ball.pos
    coord_text = f"Position  x: {bx}   y: {by}"
    coord_surf = font_info.render(coord_text, True, TEXT_COLOR)
    screen.blit(coord_surf, (12, 8))

    # ── Bottom bar ────────────────────────────────────────────────────────
    bar_rect = pygame.Rect(0, h - 34, w, 34)
    pygame.draw.rect(screen, (245, 245, 245), bar_rect)
    pygame.draw.line(screen, BORDER_COLOR, (0, h - 34), (w, h - 34), 1)

    keys = [
        ("↑ ↓ ← →", "Move ball (20 px)"),
        ("Q / Esc",  "Quit"),
    ]
    col_w = w // len(keys)
    for i, (key, desc) in enumerate(keys):
        cx = i * col_w + col_w // 2
        k_s = font_small.render(key,  True, ACCENT_COLOR)
        d_s = font_small.render(desc, True, TEXT_COLOR)
        gap = 6
        total = k_s.get_width() + gap + d_s.get_width()
        screen.blit(k_s, (cx - total // 2,                   h - 24))
        screen.blit(d_s, (cx - total // 2 + k_s.get_width() + gap, h - 24))


def draw_boundary_flash(screen: pygame.Surface, flash_alpha: int):
    """Briefly tint the screen border red when a move is blocked."""
    if flash_alpha <= 0:
        return
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (255, 0, 0, flash_alpha),
                     overlay.get_rect(), 8)
    screen.blit(overlay, (0, 0))


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    font_info  = pygame.font.SysFont("Arial",    18)
    font_small = pygame.font.SysFont("Consolas", 15)

    ball        = Ball(WINDOW_WIDTH, WINDOW_HEIGHT)
    clock       = pygame.time.Clock()
    flash_alpha = 0   # red border flash when move is blocked

    while True:
        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _quit()

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    _quit()

                moved = ball.handle_key(event.key)

                # Trigger border flash on blocked move (arrow key but no move)
                if not moved and event.key in (
                        pygame.K_UP, pygame.K_DOWN,
                        pygame.K_LEFT, pygame.K_RIGHT):
                    flash_alpha = 120

        # ── Update ────────────────────────────────────────────────────────
        if flash_alpha > 0:
            flash_alpha = max(0, flash_alpha - 8)   # fade out

        # ── Render ────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)
        draw_grid(screen)
        ball.draw(screen)
        draw_hud(screen, font_info, font_small, ball)
        draw_boundary_flash(screen, flash_alpha)

        pygame.display.flip()
        clock.tick(FPS)


def _quit():
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
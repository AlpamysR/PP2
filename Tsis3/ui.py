"""
ui.py — All game screens without external UI libraries (Task 3.5).
Screens:  Main Menu · Username Entry · Settings · Game Over · Leaderboard
"""

import pygame
import sys
from persistence import load_leaderboard, save_settings

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG      = (12,  14,  28)
C_PANEL   = (24,  28,  50)
C_PRIMARY = (80, 145, 255)
C_ACCENT  = (255, 200,  50)
C_TEXT    = (225, 225, 225)
C_MUTED   = (140, 140, 160)
C_WHITE   = (255, 255, 255)
C_BLACK   = (  0,   0,   0)
C_GREEN   = ( 60, 200,  80)
C_RED     = (215,  55,  55)
C_DARK    = ( 35,  38,  60)

CAR_SWATCH = {
    "red":    (220,  50,  50),
    "blue":   ( 50, 110, 230),
    "green":  ( 40, 190,  70),
    "yellow": (240, 200,  50),
    "purple": (160,  80, 220),
}


# ─────────────────────────────────────────────────────────────────────────────
#  Reusable Button
# ─────────────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, label: str, font: pygame.font.Font,
                 color=C_DARK, hover=C_PRIMARY, text_color=C_WHITE):
        self.rect       = pygame.Rect(rect)
        self.label      = label
        self.font       = font
        self.color      = color
        self.hover      = hover
        self.text_color = text_color

    def draw(self, surf: pygame.Surface, active: bool = False):
        mx, my   = pygame.mouse.get_pos()
        hovered  = self.rect.collidepoint(mx, my)
        bg       = self.hover if (hovered or active) else self.color
        pygame.draw.rect(surf, bg, self.rect, border_radius=9)
        pygame.draw.rect(surf, C_PRIMARY, self.rect, width=2, border_radius=9)
        t = self.font.render(self.label, True, self.text_color)
        surf.blit(t, t.get_rect(center=self.rect.center))

    def clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _title(surf, text: str, font, y: int, color=C_ACCENT):
    t = font.render(text, True, color)
    surf.blit(t, t.get_rect(centerx=surf.get_width() // 2, top=y))


def _fill_bg(surf: pygame.Surface):
    surf.fill(C_BG)
    # subtle grid
    for x in range(0, surf.get_width(), 40):
        pygame.draw.line(surf, (22, 24, 44), (x, 0), (x, surf.get_height()))
    for y in range(0, surf.get_height(), 40):
        pygame.draw.line(surf, (22, 24, 44), (0, y), (surf.get_width(), y))


# ─────────────────────────────────────────────────────────────────────────────
#  3.5 – Main Menu
# ─────────────────────────────────────────────────────────────────────────────
def show_main_menu(screen: pygame.Surface, clock: pygame.time.Clock,
                   settings: dict) -> str:
    """
    Returns: 'play' | 'leaderboard' | 'settings' | 'quit'
    """
    W, H  = screen.get_size()
    fnt_t = pygame.font.SysFont("segoeui", 54, bold=True)
    fnt_b = pygame.font.SysFont("segoeui", 28)
    fnt_s = pygame.font.SysFont("segoeui", 18)

    cx = W // 2
    buttons = {
        "play":        Button((cx - 130, 240, 260, 52), "  Play",        fnt_b, hover=C_GREEN),
        "leaderboard": Button((cx - 130, 308, 260, 52), "  Leaderboard", fnt_b),
        "settings":    Button((cx - 130, 376, 260, 52), "  Settings",    fnt_b),
        "quit":        Button((cx - 130, 444, 260, 52), "  Quit",        fnt_b, hover=C_RED),
    }

    tick = 0
    while True:
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            for key, btn in buttons.items():
                if btn.clicked(event):
                    return key

        _fill_bg(screen)

        # Animated road preview strip
        strip_y = 140
        pygame.draw.rect(screen, (50, 50, 50), (cx - 250, strip_y, 500, 70), border_radius=6)
        for i in range(5):
            lx  = cx - 200 + i * 100
            off = (tick * 3) % 80
            for y in range(strip_y, strip_y + 70, 20):
                pygame.draw.line(screen, C_ACCENT, (lx, y - off % 20), (lx, y - off % 20 + 10), 2)

        _title(screen, "SPEED RACER", fnt_t, 60)
        sub = fnt_s.render(f"Difficulty: {settings.get('difficulty','medium').title()}"
                           f"   Car: {settings.get('car_color','red').title()}", True, C_MUTED)
        screen.blit(sub, sub.get_rect(centerx=cx, top=120))

        for btn in buttons.values():
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
#  3.4 – Username Entry
# ─────────────────────────────────────────────────────────────────────────────
def show_username_entry(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    """Returns the entered username (non-empty)."""
    W, H  = screen.get_size()
    fnt_t = pygame.font.SysFont("segoeui", 42, bold=True)
    fnt_m = pygame.font.SysFont("segoeui", 28)
    fnt_s = pygame.font.SysFont("segoeui", 20)
    cx    = W // 2

    name  = ""
    btn_ok = Button((cx - 100, H // 2 + 80, 200, 48), "Start", fnt_m, hover=C_GREEN)
    tick  = 0

    while True:
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 16:
                    name += event.unicode
            if btn_ok.clicked(event) and name.strip():
                return name.strip()

        _fill_bg(screen)
        _title(screen, "Enter Your Name", fnt_t, H // 2 - 130)

        # Input box
        box = pygame.Rect(cx - 160, H // 2 - 40, 320, 52)
        pygame.draw.rect(screen, C_PANEL, box, border_radius=8)
        pygame.draw.rect(screen, C_PRIMARY, box, width=2, border_radius=8)

        display = name + ("|" if (tick // 30) % 2 == 0 else "")
        nt = fnt_m.render(display, True, C_WHITE)
        screen.blit(nt, nt.get_rect(midleft=(box.left + 12, box.centery)))

        hint = fnt_s.render("Press Enter or click Start", True, C_MUTED)
        screen.blit(hint, hint.get_rect(centerx=cx, top=H // 2 + 30))

        btn_ok.draw(screen)
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
#  3.5 – Settings Screen
# ─────────────────────────────────────────────────────────────────────────────
def show_settings(screen: pygame.Surface, clock: pygame.time.Clock,
                  settings: dict) -> dict:
    """
    Lets user toggle sound, pick car colour, choose difficulty.
    Saves to settings.json and returns updated settings.
    """
    W, H  = screen.get_size()
    fnt_t = pygame.font.SysFont("segoeui", 42, bold=True)
    fnt_m = pygame.font.SysFont("segoeui", 26)
    fnt_s = pygame.font.SysFont("segoeui", 20)
    cx    = W // 2

    s = dict(settings)   # local copy

    # Sound toggle
    btn_sound = Button((cx + 60, 160, 140, 42), "", fnt_m)

    # Difficulty buttons
    diff_btns = {
        d: Button((cx - 200 + i * 140, 280, 120, 42), d.title(), fnt_m)
        for i, d in enumerate(["easy", "medium", "hard"])
    }

    # Car colour swatches
    car_btns = {}
    ci = 0
    for cname in CAR_SWATCH:
        car_btns[cname] = Button((cx - 260 + ci * 106, 390, 90, 42), cname.title(), fnt_m,
                                  color=CAR_SWATCH[cname], hover=CAR_SWATCH[cname])
        ci += 1

    btn_back = Button((cx - 110, H - 80, 220, 48), "← Save & Back", fnt_m, hover=C_GREEN)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(s); return s
            if btn_sound.clicked(event):
                s["sound"] = not s["sound"]
            for d, btn in diff_btns.items():
                if btn.clicked(event):
                    s["difficulty"] = d
            for cname, btn in car_btns.items():
                if btn.clicked(event):
                    s["car_color"] = cname
            if btn_back.clicked(event):
                save_settings(s); return s

        _fill_bg(screen)
        _title(screen, "Settings", fnt_t, 70)

        # Sound
        sl = fnt_m.render("Sound:", True, C_TEXT)
        screen.blit(sl, (cx - 200, 170))
        btn_sound.label = "ON  ✓" if s["sound"] else "OFF ✗"
        btn_sound.color = C_GREEN if s["sound"] else C_RED
        btn_sound.draw(screen)

        # Difficulty
        dl = fnt_m.render("Difficulty:", True, C_TEXT)
        screen.blit(dl, dl.get_rect(centerx=cx, top=245))
        for d, btn in diff_btns.items():
            btn.draw(screen, active=(s["difficulty"] == d))

        # Car colour
        ccl = fnt_m.render("Car Colour:", True, C_TEXT)
        screen.blit(ccl, ccl.get_rect(centerx=cx, top=350))
        for cname, btn in car_btns.items():
            btn.draw(screen, active=(s["car_color"] == cname))
            if s["car_color"] == cname:
                pygame.draw.rect(screen, C_WHITE, btn.rect, width=3, border_radius=9)

        btn_back.draw(screen)
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
#  3.5 – Game Over Screen
# ─────────────────────────────────────────────────────────────────────────────
def show_game_over(screen: pygame.Surface, clock: pygame.time.Clock,
                   result: dict) -> str:
    """
    Shows score, distance, coins, win/loss.
    Returns 'retry' | 'menu'.
    """
    W, H  = screen.get_size()
    fnt_t = pygame.font.SysFont("segoeui", 52, bold=True)
    fnt_m = pygame.font.SysFont("segoeui", 28)
    fnt_s = pygame.font.SysFont("segoeui", 22)
    cx    = W // 2

    title_text  = "  YOU WIN!" if result.get("won") else "  GAME OVER"
    title_color = C_GREEN       if result.get("won") else C_RED

    btn_retry = Button((cx - 135, H // 2 + 110, 120, 50), " Retry", fnt_m, hover=C_GREEN)
    btn_menu  = Button((cx + 15,  H // 2 + 110, 120, 50), " Menu",  fnt_m)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "retry"
                if event.key == pygame.K_ESCAPE: return "menu"
            if btn_retry.clicked(event): return "retry"
            if btn_menu.clicked(event):  return "menu"

        _fill_bg(screen)
        _title(screen, title_text, fnt_t, H // 2 - 180, color=title_color)

        # Stats panel
        panel = pygame.Rect(cx - 200, H // 2 - 100, 400, 190)
        pygame.draw.rect(screen, C_PANEL, panel, border_radius=10)
        pygame.draw.rect(screen, C_PRIMARY, panel, width=2, border_radius=10)

        rows = [
            ("Score",    str(result.get("score",    0))),
            ("Distance", f"{result.get('distance', 0)} m"),
            ("Coins",    str(result.get("coins",    0))),
        ]
        for i, (lbl, val) in enumerate(rows):
            yl = panel.top + 18 + i * 55
            lt = fnt_m.render(lbl, True, C_MUTED)
            vt = fnt_m.render(val,  True, C_ACCENT)
            screen.blit(lt, (panel.left + 24, yl))
            screen.blit(vt, vt.get_rect(right=panel.right - 24, top=yl))

        btn_retry.draw(screen)
        btn_menu.draw(screen)

        hint = fnt_s.render("[R] Retry   [Esc] Menu", True, C_MUTED)
        screen.blit(hint, hint.get_rect(centerx=cx, top=H // 2 + 175))

        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
#  3.4 / 3.5 – Leaderboard Screen (Top 10)
# ─────────────────────────────────────────────────────────────────────────────
def show_leaderboard(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    """Displays top-10 scores. Returns 'back'."""
    W, H  = screen.get_size()
    fnt_t = pygame.font.SysFont("segoeui", 44, bold=True)
    fnt_h = pygame.font.SysFont("segoeui", 22, bold=True)
    fnt_r = pygame.font.SysFont("segoeui", 21)
    cx    = W // 2

    btn_back = Button((cx - 110, H - 75, 220, 48), "← Back", fnt_h)
    entries  = load_leaderboard()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
            if btn_back.clicked(event):
                return "back"

        _fill_bg(screen)
        _title(screen, "🏆  Leaderboard", fnt_t, 50)

        # Header
        header_y = 115
        cols = [("Rank", cx - 280), ("Name", cx - 160), ("Score", cx + 60), ("Distance", cx + 180)]
        for label, lx in cols:
            ht = fnt_h.render(label, True, C_ACCENT)
            screen.blit(ht, (lx, header_y))
        pygame.draw.line(screen, C_PRIMARY, (cx - 300, header_y + 30), (cx + 280, header_y + 30), 1)

        # Rows
        if not entries:
            nt = fnt_r.render("No scores yet — be the first!", True, C_MUTED)
            screen.blit(nt, nt.get_rect(centerx=cx, top=170))
        else:
            for i, e in enumerate(entries[:10]):
                ry     = header_y + 42 + i * 36
                row_bg = pygame.Rect(cx - 302, ry - 2, 582, 32)
                if i % 2 == 0:
                    pygame.draw.rect(screen, C_PANEL, row_bg, border_radius=4)

                rank_color = [C_ACCENT, C_WHITE, (180, 110, 50)] if i < 3 else C_TEXT
                rc = rank_color if isinstance(rank_color, tuple) else rank_color[0]

                rank_t = fnt_r.render(f"#{i + 1}", True, C_ACCENT if i == 0 else C_TEXT)
                name_t = fnt_r.render(e.get("name", "?")[:14], True, C_TEXT)
                scr_t  = fnt_r.render(str(e.get("score", 0)), True, C_WHITE)
                dist_t = fnt_r.render(f"{e.get('distance', 0)} m", True, C_MUTED)

                screen.blit(rank_t, (cx - 280, ry))
                screen.blit(name_t, (cx - 160, ry))
                screen.blit(scr_t,  (cx + 60,  ry))
                screen.blit(dist_t, (cx + 180, ry))

        btn_back.draw(screen)
        pygame.display.flip()
        clock.tick(60)
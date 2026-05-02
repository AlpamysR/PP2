import pygame
import sys
from datetime import datetime

from tools import (
    PencilTool, LineTool, FillTool, TextTool,
    BRUSH_SIZES, BRUSH_LABELS,
)

# ─────────────────────────────────────────────
#  Window / Layout constants
# ─────────────────────────────────────────────
WINDOW_W   = 1200
WINDOW_H   = 720
TOOLBAR_H  = 60
CANVAS_TOP = TOOLBAR_H

CANVAS_RECT = pygame.Rect(0, CANVAS_TOP, WINDOW_W, WINDOW_H - CANVAS_TOP)

# ─────────────────────────────────────────────
#  Colours
# ─────────────────────────────────────────────
C_BG        = (30,  30,  30)
C_TOOLBAR   = (45,  45,  45)
C_BORDER    = (70,  70,  70)
C_TEXT      = (220, 220, 220)
C_ACTIVE    = (80,  140, 255)
C_CANVAS    = (255, 255, 255)

PALETTE = [
    (0,   0,   0),    # black
    (255, 255, 255),  # white
    (220, 60,  60),   # red
    (60,  200, 80),   # green
    (60,  120, 220),  # blue
    (240, 200, 50),   # yellow
    (240, 130, 40),   # orange
    (160, 80,  220),  # purple
    (60,  210, 210),  # cyan
    (240, 100, 160),  # pink
    (139, 90,  43),   # brown
    (128, 128, 128),  # grey
]

# ─────────────────────────────────────────────
#  Tiny UI helpers
# ─────────────────────────────────────────────
def draw_button(surface, rect, label, font, active=False, bg=None):
    """Draw a rounded toolbar button."""
    colour = C_ACTIVE if active else (bg or (65, 65, 65))
    pygame.draw.rect(surface, colour, rect, border_radius=6)
    pygame.draw.rect(surface, C_BORDER, rect, width=1, border_radius=6)
    text = font.render(label, True, C_TEXT)
    tr   = text.get_rect(center=rect.center)
    surface.blit(text, tr)


def draw_toolbar(surface, font, current_tool, brush_key, draw_color):
    """Render the full toolbar."""
    pygame.draw.rect(surface, C_TOOLBAR, (0, 0, WINDOW_W, TOOLBAR_H))
    pygame.draw.line(surface, C_BORDER, (0, TOOLBAR_H), (WINDOW_W, TOOLBAR_H))

    x = 8

    # ── Tool buttons ──
    tools = [("pencil", "✏ Pencil"), ("line", "╱ Line"),
             ("fill",   "⬛ Fill"),  ("text",  "T Text")]
    for key, label in tools:
        r = pygame.Rect(x, 10, 90, 38)
        draw_button(surface, r, label, font, active=(current_tool == key))
        x += 98

    x += 10
    pygame.draw.line(surface, C_BORDER, (x, 8), (x, TOOLBAR_H - 8))
    x += 14

    # ── Brush-size buttons ──
    for bkey in (1, 2, 3):
        r = pygame.Rect(x, 10, 74, 38)
        draw_button(surface, r, BRUSH_LABELS[bkey], font,
                    active=(brush_key == bkey))
        x += 82

    x += 10
    pygame.draw.line(surface, C_BORDER, (x, 8), (x, TOOLBAR_H - 8))
    x += 14

    # ── Colour palette ──
    swatch = 32
    for colour in PALETTE:
        r = pygame.Rect(x, 14, swatch, swatch)
        pygame.draw.rect(surface, colour, r, border_radius=4)
        if colour == draw_color:
            pygame.draw.rect(surface, C_ACTIVE, r, width=3, border_radius=4)
        else:
            pygame.draw.rect(surface, C_BORDER, r, width=1, border_radius=4)
        x += swatch + 4

    # ── Save hint ──
    hint = font.render("Ctrl+S  Save", True, (150, 150, 150))
    surface.blit(hint, hint.get_rect(midright=(WINDOW_W - 10, TOOLBAR_H // 2)))


# ─────────────────────────────────────────────
#  Hit-test helpers (return tool / brush / colour or None)
# ─────────────────────────────────────────────
def toolbar_hit(mx, my):
    """
    Returns one of:
      ('tool',  tool_name)
      ('brush', brush_key)
      ('color', rgb_tuple)
      None
    """
    if my >= TOOLBAR_H:
        return None

    x = 8
    tools = ["pencil", "line", "fill", "text"]
    for key in tools:
        if pygame.Rect(x, 10, 90, 38).collidepoint(mx, my):
            return ("tool", key)
        x += 98

    x += 24   # separator + gap
    for bkey in (1, 2, 3):
        if pygame.Rect(x, 10, 74, 38).collidepoint(mx, my):
            return ("brush", bkey)
        x += 82

    x += 24
    swatch = 32
    for colour in PALETTE:
        if pygame.Rect(x, 14, swatch, swatch).collidepoint(mx, my):
            return ("color", colour)
        x += swatch + 4

    return None


# ─────────────────────────────────────────────
#  3.4  Save Canvas
# ─────────────────────────────────────────────
def save_canvas(canvas: pygame.Surface):
    """
    Save the canvas as a PNG file with a timestamp in the name
    so saves never overwrite each other.
    Uses pygame.image.save — no extra libraries needed.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"canvas_{timestamp}.png"
    pygame.image.save(canvas, filename)
    print(f"[Saved]  {filename}")
    return filename


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Paint — TSIS2")

    font = pygame.font.SysFont("segoeui", 14)

    # ── Canvas surface (persistent drawing target) ──
    canvas = pygame.Surface((WINDOW_W, WINDOW_H - CANVAS_TOP))
    canvas.fill(C_CANVAS)

    # ── Overlay (live previews drawn here each frame) ──
    overlay = pygame.Surface((WINDOW_W, WINDOW_H - CANVAS_TOP), pygame.SRCALPHA)

    # ── Tool instances ──
    pencil_tool = PencilTool()
    line_tool   = LineTool()
    fill_tool   = FillTool()
    text_tool   = TextTool()

    # ── App state ──
    current_tool = "pencil"
    brush_key    = 2              # default: medium
    draw_color   = (0, 0, 0)     # default: black
    mouse_down   = False

    # ── Save-feedback message ──
    save_msg      = ""
    save_msg_time = 0

    clock = pygame.time.Clock()

    # ═════════════════════════════════════════
    #  Main loop
    # ═════════════════════════════════════════
    while True:
        brush_size = BRUSH_SIZES[brush_key]

        for event in pygame.event.get():

            # ── Quit ──────────────────────────────
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Keyboard ──────────────────────────
            elif event.type == pygame.KEYDOWN:

                # Text tool captures keystrokes first
                if text_tool.on_key_down(event, canvas, draw_color):
                    pass

                # 3.2 Brush-size shortcuts
                elif event.key == pygame.K_1:
                    brush_key = 1
                elif event.key == pygame.K_2:
                    brush_key = 2
                elif event.key == pygame.K_3:
                    brush_key = 3

                # 3.4 Save Canvas: Ctrl+S
                elif event.key == pygame.K_s and (
                        pygame.key.get_mods() & pygame.KMOD_CTRL):
                    fname = save_canvas(canvas)
                    save_msg      = f"Saved  {fname}"
                    save_msg_time = pygame.time.get_ticks()

                # Escape cancels text editing
                elif event.key == pygame.K_ESCAPE:
                    text_tool._cancel()

            # ── Mouse button down ──────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                hit    = toolbar_hit(mx, my)

                if hit:
                    kind, value = hit
                    if kind == "tool":
                        current_tool = value
                        text_tool._cancel()     # cancel any open text session
                    elif kind == "brush":
                        brush_key = value
                    elif kind == "color":
                        draw_color = value
                else:
                    # Click is on the canvas
                    mouse_down  = True
                    canvas_pos  = (mx, my - CANVAS_TOP)

                    if current_tool == "pencil":
                        pencil_tool.on_mouse_down(
                            canvas, canvas_pos, draw_color, brush_size)

                    elif current_tool == "line":
                        line_tool.on_mouse_down(canvas_pos)

                    elif current_tool == "fill":
                        fill_tool.on_mouse_down(
                            canvas, canvas_pos, draw_color)

                    elif current_tool == "text":
                        text_tool.on_mouse_down(canvas_pos)

            # ── Mouse move ────────────────────────
            elif event.type == pygame.MOUSEMOTION:
                mx, my     = event.pos
                canvas_pos = (mx, my - CANVAS_TOP)

                if mouse_down and CANVAS_RECT.collidepoint(mx, my):
                    if current_tool == "pencil":
                        pencil_tool.on_mouse_move(
                            canvas, canvas_pos, draw_color, brush_size)
                    elif current_tool == "line":
                        line_tool.on_mouse_move(canvas_pos)

            # ── Mouse button up ───────────────────
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mx, my     = event.pos
                canvas_pos = (mx, my - CANVAS_TOP)

                if current_tool == "pencil":
                    pencil_tool.on_mouse_up()
                elif current_tool == "line":
                    line_tool.on_mouse_up(
                        canvas, canvas_pos, draw_color, brush_size)

                mouse_down = False

        # ═══════════════════════════════════════
        #  Draw
        # ═══════════════════════════════════════
        screen.fill(C_BG)

        # Canvas
        screen.blit(canvas, (0, CANVAS_TOP))

        # Overlay (live previews)
        overlay.fill((0, 0, 0, 0))   # transparent each frame

        if current_tool == "line":
            line_tool.draw_preview(overlay, draw_color, brush_size)

        if current_tool == "text":
            text_tool.draw_preview(overlay, draw_color)

        screen.blit(overlay, (0, CANVAS_TOP))

        # Toolbar (on top)
        draw_toolbar(screen, font, current_tool, brush_key, draw_color)

        # Save confirmation message
        if save_msg and pygame.time.get_ticks() - save_msg_time < 2500:
            msg_surf = font.render(save_msg, True, (100, 220, 100))
            screen.blit(msg_surf, (10, WINDOW_H - 22))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
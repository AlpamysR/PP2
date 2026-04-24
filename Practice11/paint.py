import pygame
import sys
import math

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()

WIDTH, HEIGHT = 980, 680
TOOLBAR_H     = 60
CANVAS_TOP    = TOOLBAR_H
CANVAS_H      = HEIGHT - TOOLBAR_H - 18   # leave 18 px for hint bar at bottom

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()

font      = pygame.font.SysFont("consolas", 14, bold=True)
font_tiny = pygame.font.SysFont("consolas", 12)

# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE = [
    (  0,   0,   0), (255, 255, 255), (220,  50,  50), ( 50, 180,  50),
    ( 50, 130, 230), (255, 220,   0), (255, 140,   0), (160,  32, 240),
    ( 20, 200, 200), (255, 105, 180), (139,  69,  19), (128, 128, 128),
]

# ── Tools ─────────────────────────────────────────────────────────────────────
# NEW tools added: Square, RTri (right triangle), EqTri (equilateral), Rhombus
TOOLS = ["Pencil", "Rect", "Square", "Circle",
         "RTri", "EqTri", "Rhombus", "Eraser"]

TOOL_W, TOOL_H = 62, 34
SWATCH_SIZE    = 26
BRUSH_SIZES    = [2, 5, 10, 18]


# ── Toolbar ───────────────────────────────────────────────────────────────────

def draw_toolbar(surface, active_tool, active_color, brush_size):
    """Render tool buttons, colour palette, brush size buttons, colour preview."""
    pygame.draw.rect(surface, (40, 40, 40), (0, 0, WIDTH, TOOLBAR_H))
    pygame.draw.line(surface, (80, 80, 80), (0, TOOLBAR_H - 1),
                     (WIDTH, TOOLBAR_H - 1))

    # Tool buttons
    for i, tool in enumerate(TOOLS):
        x = 4 + i * (TOOL_W + 3)
        col = (80, 120, 200) if tool == active_tool else (70, 70, 70)
        pygame.draw.rect(surface, col, (x, 10, TOOL_W, TOOL_H), border_radius=4)
        lbl = font.render(tool, True, (255, 255, 255))
        surface.blit(lbl, (x + TOOL_W // 2 - lbl.get_width()  // 2,
                           10 + TOOL_H // 2 - lbl.get_height() // 2))

    # Colour swatches
    palette_x = 4 + len(TOOLS) * (TOOL_W + 3) + 6
    for j, c in enumerate(PALETTE):
        sx = palette_x + j * (SWATCH_SIZE + 2)
        pygame.draw.rect(surface, c, (sx, 17, SWATCH_SIZE, SWATCH_SIZE),
                         border_radius=3)
        if c == active_color:
            pygame.draw.rect(surface, (255, 255, 255),
                             (sx - 2, 15, SWATCH_SIZE + 4, SWATCH_SIZE + 4),
                             2, border_radius=4)

    # Active colour preview box
    prev_x = palette_x + len(PALETTE) * (SWATCH_SIZE + 2) + 6
    pygame.draw.rect(surface, active_color,
                     (prev_x, 10, 38, 38), border_radius=5)
    pygame.draw.rect(surface, (200, 200, 200),
                     (prev_x, 10, 38, 38), 2, border_radius=5)

    # Brush size buttons (far right)
    bx = WIDTH - len(BRUSH_SIZES) * 33 - 6
    for k, bs in enumerate(BRUSH_SIZES):
        r = pygame.Rect(bx + k * 33, 12, 28, 28)
        col = (80, 120, 200) if bs == brush_size else (70, 70, 70)
        pygame.draw.rect(surface, col, r, border_radius=4)
        pygame.draw.circle(surface, (255, 255, 255),
                           r.center, max(1, bs // 2))


def toolbar_click(mx, my):
    """Detect which toolbar element was clicked. Returns (kind, value) or None."""
    if my >= TOOLBAR_H:
        return None

    for i, tool in enumerate(TOOLS):
        x = 4 + i * (TOOL_W + 3)
        if x <= mx <= x + TOOL_W and 10 <= my <= 10 + TOOL_H:
            return ('tool', tool)

    palette_x = 4 + len(TOOLS) * (TOOL_W + 3) + 6
    for j, c in enumerate(PALETTE):
        sx = palette_x + j * (SWATCH_SIZE + 2)
        if sx <= mx <= sx + SWATCH_SIZE and 17 <= my <= 17 + SWATCH_SIZE:
            return ('color', c)

    bx = WIDTH - len(BRUSH_SIZES) * 33 - 6
    for k, bs in enumerate(BRUSH_SIZES):
        if bx + k * 33 <= mx <= bx + k * 33 + 28 and 12 <= my <= 40:
            return ('brush', bs)

    return None


# ── Shape drawing ─────────────────────────────────────────────────────────────

def _points_right_triangle(p1, p2):
    """
    Right-angle triangle with the right angle at p1.
    p1 = corner of the right angle
    p2 = opposite corner (diagonal)
    Returns list of 3 (x, y) points.
    """
    x1, y1 = p1
    x2, y2 = p2
    return [(x1, y1), (x2, y1), (x1, y2)]


def _points_equilateral_triangle(p1, p2):
    """
    Equilateral triangle.
    p1 = left base corner, p2 = right base corner (dragged horizontally).
    The apex is centred above (or below, depending on drag direction) the base.
    Returns list of 3 (x, y) points.
    """
    x1, y1 = p1
    x2, y2 = p2
    mx = (x1 + x2) / 2          # midpoint of base
    base = math.hypot(x2 - x1, y2 - y1)
    height = base * math.sqrt(3) / 2
    # Normal vector perpendicular to base, pointing "upward" (negative y)
    if base == 0:
        return [(x1, y1), (x2, y2), (x1, y1)]
    dx = (x2 - x1) / base
    dy = (y2 - y1) / base
    # Perpendicular: rotate 90° counter-clockwise
    apex = (mx - dy * height, (y1 + y2) / 2 + dx * height)
    # Flip so apex is above the base (standard orientation)
    apex = (mx + dy * height, (y1 + y2) / 2 - dx * height)
    return [(x1, y1), (x2, y2), apex]


def _points_rhombus(p1, p2):
    """
    Rhombus (diamond) defined by its bounding box corners p1 and p2.
    Returns 4 (x, y) points (top, right, bottom, left).
    """
    x1, y1 = p1
    x2, y2 = p2
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return [
        (cx, y1),   # top
        (x2, cy),   # right
        (cx, y2),   # bottom
        (x1, cy),   # left
    ]


def _draw_shape(surface, tool, p1, p2, color, thickness):
    """
    Draw the selected shape onto *surface* using two anchor points.

    p1 – where the mouse was pressed
    p2 – current (or final) mouse position
    Both coordinates are relative to the canvas surface (not screen).
    """
    x1, y1 = p1
    x2, y2 = p2

    if tool == "Rect":
        left   = min(x1, x2);  top    = min(y1, y2)
        w      = abs(x2 - x1); h      = abs(y2 - y1)
        pygame.draw.rect(surface, color, (left, top, w, h), thickness)

    elif tool == "Square":
        # Force equal width and height using the smaller dimension
        side = min(abs(x2 - x1), abs(y2 - y1))
        sx   = x1 if x2 >= x1 else x1 - side
        sy   = y1 if y2 >= y1 else y1 - side
        pygame.draw.rect(surface, color, (sx, sy, side, side), thickness)

    elif tool == "Circle":
        cx = (x1 + x2) // 2;  cy = (y1 + y2) // 2
        rx = abs(x2 - x1) // 2; ry = abs(y2 - y1) // 2
        if rx > 0 and ry > 0:
            pygame.draw.ellipse(surface, color,
                                (cx - rx, cy - ry, rx * 2, ry * 2), thickness)

    elif tool == "RTri":
        pts = _points_right_triangle(p1, p2)
        if len({p for p in pts}) > 1:
            pygame.draw.polygon(surface, color, pts, thickness)

    elif tool == "EqTri":
        pts = _points_equilateral_triangle(p1, p2)
        pygame.draw.polygon(surface, color, pts, thickness)

    elif tool == "Rhombus":
        pts = _points_rhombus(p1, p2)
        pygame.draw.polygon(surface, color, pts, thickness)


# ── Main application loop ─────────────────────────────────────────────────────

def main():
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill((255, 255, 255))

    active_tool  = "Pencil"
    active_color = (0, 0, 0)
    brush_size   = 5

    drawing      = False
    start_pos    = None
    preview_surf = None

    # Keyboard shortcuts mapped to tool names
    KEY_MAP = {
        pygame.K_p: "Pencil",
        pygame.K_r: "Rect",
        pygame.K_s: "Square",
        pygame.K_o: "Circle",
        pygame.K_t: "RTri",
        pygame.K_g: "EqTri",
        pygame.K_h: "Rhombus",
        pygame.K_e: "Eraser",
    }

    # Shape tools that use drag-to-draw with live preview
    SHAPE_TOOLS = {"Rect", "Square", "Circle", "RTri", "EqTri", "Rhombus"}

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard shortcuts ────────────────────────────────────────
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    canvas.fill((255, 255, 255))   # clear canvas
                elif event.key in KEY_MAP:
                    active_tool = KEY_MAP[event.key]

            # ── Mouse press ───────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                hit = toolbar_click(mx, my)
                if hit:
                    kind, val = hit
                    if kind == 'tool':   active_tool  = val
                    if kind == 'color':  active_color = val
                    if kind == 'brush':  brush_size   = val
                else:
                    drawing  = True
                    cy_off   = my - CANVAS_TOP
                    start_pos = (mx, cy_off)
                    # Immediate dot for free-draw tools
                    if active_tool in ("Pencil", "Eraser"):
                        col = (255, 255, 255) if active_tool == "Eraser" \
                              else active_color
                        pygame.draw.circle(canvas, col, start_pos, brush_size)

            # ── Mouse release ─────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and active_tool in SHAPE_TOOLS:
                    mx, my  = event.pos
                    end_pos = (mx, my - CANVAS_TOP)
                    _draw_shape(canvas, active_tool, start_pos, end_pos,
                                active_color, brush_size)
                drawing      = False
                preview_surf = None

            # ── Mouse drag ────────────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my   = event.pos
                canvas_y = max(0, my - CANVAS_TOP)

                if active_tool == "Pencil":
                    lx, ly = start_pos
                    pygame.draw.line(canvas, active_color,
                                     (lx, ly), (mx, canvas_y), brush_size)
                    start_pos = (mx, canvas_y)

                elif active_tool == "Eraser":
                    lx, ly = start_pos
                    pygame.draw.line(canvas, (255, 255, 255),
                                     (lx, ly), (mx, canvas_y), brush_size * 3)
                    start_pos = (mx, canvas_y)

                elif active_tool in SHAPE_TOOLS:
                    # Live preview: draw on a copy, don't modify the real canvas
                    preview_surf = canvas.copy()
                    _draw_shape(preview_surf, active_tool, start_pos,
                                (mx, canvas_y), active_color, brush_size)

        # ── Render ───────────────────────────────────────────────────────────
        screen.fill((30, 30, 30))
        screen.blit(preview_surf if preview_surf else canvas, (0, CANVAS_TOP))
        draw_toolbar(screen, active_tool, active_color, brush_size)

        # Hint bar at the very bottom
        hints = ("C=clear  P=pencil  R=rect  S=square  O=circle  "
                 "T=rtri  G=eqtri  H=rhombus  E=eraser")
        hint = font_tiny.render(hints, True, (140, 140, 140))
        screen.blit(hint, (4, HEIGHT - 16))

        pygame.display.flip()


if __name__ == "__main__":
    main()
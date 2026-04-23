import pygame
import sys

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()

WIDTH, HEIGHT = 900, 650
TOOLBAR_H     = 60            # height of the toolbar at the top
CANVAS_TOP    = TOOLBAR_H
CANVAS_H      = HEIGHT - TOOLBAR_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()

font      = pygame.font.SysFont("consolas", 15, bold=True)
font_big  = pygame.font.SysFont("consolas", 20, bold=True)

# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE = [
    (  0,   0,   0),   # Black
    (255, 255, 255),   # White
    (220,  50,  50),   # Red
    ( 50, 180,  50),   # Green
    ( 50, 130, 230),   # Blue
    (255, 220,   0),   # Yellow
    (255, 140,   0),   # Orange
    (160,  32, 240),   # Purple
    ( 20, 200, 200),   # Cyan
    (255, 105, 180),   # Pink
    (139,  69,  19),   # Brown
    (128, 128, 128),   # Gray
]

# ── Tools ─────────────────────────────────────────────────────────────────────
TOOLS = ["Pencil", "Rect", "Circle", "Eraser"]

# Tool-bar layout constants
TOOL_W, TOOL_H = 70, 36
SWATCH_SIZE    = 28
BRUSH_SIZES    = [2, 5, 10, 18]   # eraser / pencil thickness options


# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_toolbar(surface, active_tool, active_color, brush_size):
    """Render the tool-bar: tools, palette, brush sizes."""
    pygame.draw.rect(surface, (40, 40, 40), (0, 0, WIDTH, TOOLBAR_H))
    pygame.draw.line(surface, (80, 80, 80), (0, TOOLBAR_H - 1), (WIDTH, TOOLBAR_H - 1))

    # Tool buttons
    for i, tool in enumerate(TOOLS):
        x = 6 + i * (TOOL_W + 4)
        color = (80, 120, 200) if tool == active_tool else (70, 70, 70)
        pygame.draw.rect(surface, color, (x, 10, TOOL_W, TOOL_H), border_radius=5)
        label = font.render(tool, True, (255, 255, 255))
        surface.blit(label, (x + TOOL_W // 2 - label.get_width() // 2,
                              10 + TOOL_H // 2 - label.get_height() // 2))

    # Colour swatches
    palette_x = 6 + len(TOOLS) * (TOOL_W + 4) + 10
    for j, c in enumerate(PALETTE):
        sx = palette_x + j * (SWATCH_SIZE + 3)
        sy = 16
        pygame.draw.rect(surface, c, (sx, sy, SWATCH_SIZE, SWATCH_SIZE),
                         border_radius=4)
        if c == active_color:
            pygame.draw.rect(surface, (255, 255, 255),
                             (sx - 2, sy - 2, SWATCH_SIZE + 4, SWATCH_SIZE + 4),
                             2, border_radius=5)

    # Brush size buttons (right side)
    bx = WIDTH - (len(BRUSH_SIZES) * 34 + 10)
    for k, bs in enumerate(BRUSH_SIZES):
        rect = pygame.Rect(bx + k * 34, 12, 30, 30)
        color = (80, 120, 200) if bs == brush_size else (70, 70, 70)
        pygame.draw.rect(surface, color, rect, border_radius=4)
        pygame.draw.circle(surface, (255, 255, 255),
                           rect.center, max(1, bs // 2))

    # Active colour preview
    prev_x = palette_x + len(PALETTE) * (SWATCH_SIZE + 3) + 10
    pygame.draw.rect(surface, active_color,
                     (prev_x, 10, 44, 38), border_radius=6)
    pygame.draw.rect(surface, (200, 200, 200),
                     (prev_x, 10, 44, 38), 2, border_radius=6)


def toolbar_click(mx, my):
    """Return ('tool', name) | ('color', rgb) | ('brush', size) | None."""
    if my >= TOOLBAR_H:
        return None

    # Tool buttons
    for i, tool in enumerate(TOOLS):
        x = 6 + i * (TOOL_W + 4)
        if x <= mx <= x + TOOL_W and 10 <= my <= 10 + TOOL_H:
            return ('tool', tool)

    # Colour swatches
    palette_x = 6 + len(TOOLS) * (TOOL_W + 4) + 10
    for j, c in enumerate(PALETTE):
        sx = palette_x + j * (SWATCH_SIZE + 3)
        if sx <= mx <= sx + SWATCH_SIZE and 16 <= my <= 16 + SWATCH_SIZE:
            return ('color', c)

    # Brush sizes
    bx = WIDTH - (len(BRUSH_SIZES) * 34 + 10)
    for k, bs in enumerate(BRUSH_SIZES):
        if bx + k * 34 <= mx <= bx + k * 34 + 30 and 12 <= my <= 42:
            return ('brush', bs)

    return None


# ── Main application loop ─────────────────────────────────────────────────────

def main():
    # Canvas is a separate Surface so we can clear / save it independently
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill((255, 255, 255))    # start with white canvas

    active_tool  = "Pencil"
    active_color = (0, 0, 0)
    brush_size   = 5

    drawing      = False
    start_pos    = None            # for rectangle / circle: where drag started
    preview_surf = None            # temporary surface shown while dragging shapes

    running = True
    while running:
        clock.tick(60)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Key shortcuts ────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:      # C → clear canvas
                    canvas.fill((255, 255, 255))
                if event.key == pygame.K_p:      active_tool = "Pencil"
                if event.key == pygame.K_r:      active_tool = "Rect"
                if event.key == pygame.K_o:      active_tool = "Circle"
                if event.key == pygame.K_e:      active_tool = "Eraser"

            # ── Mouse button down ────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                hit = toolbar_click(mx, my)
                if hit:
                    kind, val = hit
                    if kind == 'tool':   active_tool  = val
                    if kind == 'color':  active_color = val
                    if kind == 'brush':  brush_size   = val
                else:
                    # Click is on the canvas
                    drawing   = True
                    # Offset y so coordinates are relative to canvas surface
                    canvas_y  = my - CANVAS_TOP
                    start_pos = (mx, canvas_y)
                    if active_tool in ("Pencil", "Eraser"):
                        # Draw a dot immediately on press
                        color = (255, 255, 255) if active_tool == "Eraser" \
                                else active_color
                        pygame.draw.circle(canvas, color,
                                           start_pos, brush_size)

            # ── Mouse button released ────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and active_tool in ("Rect", "Circle"):
                    mx, my   = event.pos
                    end_pos  = (mx, my - CANVAS_TOP)
                    # Commit the shape to the canvas
                    _draw_shape(canvas, active_tool, start_pos, end_pos,
                                active_color, brush_size)
                drawing      = False
                preview_surf = None

            # ── Mouse motion (drag) ──────────────────────────────────────
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my   = event.pos
                canvas_y = my - CANVAS_TOP
                if canvas_y < 0: canvas_y = 0   # clamp to canvas

                if active_tool == "Pencil":
                    # Draw a line segment from last recorded position
                    lx, ly = start_pos
                    pygame.draw.line(canvas, active_color,
                                     (lx, ly), (mx, canvas_y), brush_size)
                    start_pos = (mx, canvas_y)

                elif active_tool == "Eraser":
                    lx, ly = start_pos
                    pygame.draw.line(canvas, (255, 255, 255),
                                     (lx, ly), (mx, canvas_y), brush_size * 3)
                    start_pos = (mx, canvas_y)

                else:
                    # Rect / Circle: build a live preview surface
                    preview_surf = canvas.copy()
                    _draw_shape(preview_surf, active_tool, start_pos,
                                (mx, canvas_y), active_color, brush_size)

        # ── Draw ────────────────────────────────────────────────────────────
        screen.fill((30, 30, 30))
        # Show live preview if dragging a shape, otherwise the real canvas
        screen.blit(preview_surf if preview_surf else canvas, (0, CANVAS_TOP))
        draw_toolbar(screen, active_tool, active_color, brush_size)

        # Hint text
        hint = font.render("C=clear  P=pencil  R=rect  O=circle  E=eraser", True, (160, 160, 160))
        screen.blit(hint, (6, HEIGHT - 18))

        pygame.display.flip()


def _draw_shape(surface, tool, p1, p2, color, thickness):
    """Draw a rectangle or circle from two corner/anchor points onto surface."""
    x1, y1 = p1
    x2, y2 = p2
    if tool == "Rect":
        left   = min(x1, x2)
        top    = min(y1, y2)
        width  = abs(x2 - x1)
        height = abs(y2 - y1)
        pygame.draw.rect(surface, color, (left, top, width, height), thickness)
    elif tool == "Circle":
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        rx = abs(x2 - x1) // 2
        ry = abs(y2 - y1) // 2
        if rx > 0 and ry > 0:
            # pygame has no built-in ellipse with thickness, use draw.ellipse
            rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
            pygame.draw.ellipse(surface, color, rect, thickness)


if __name__ == "__main__":
    main()
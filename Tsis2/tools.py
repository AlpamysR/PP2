import pygame
from collections import deque


# ─────────────────────────────────────────────
#  3.2  Brush Size
# ─────────────────────────────────────────────
BRUSH_SIZES = {
    1: 2,   # small  — keyboard shortcut '1'
    2: 5,   # medium — keyboard shortcut '2'
    3: 10,  # large  — keyboard shortcut '3'
}

BRUSH_LABELS = {
    1: "S  2px",
    2: "M  5px",
    3: "L 10px",
}


# ─────────────────────────────────────────────
#  3.1  Pencil Tool
# ─────────────────────────────────────────────
class PencilTool:
    """
    Draws continuously while the mouse button is held down.
    Uses pygame.draw.line between consecutive mouse positions.
    """

    def __init__(self):
        self.last_pos = None   # previous mouse position

    def on_mouse_down(self, canvas: pygame.Surface, pos: tuple,
                      color: tuple, brush_size: int):
        """Begin a stroke — mark the starting point and draw a dot."""
        self.last_pos = pos
        pygame.draw.circle(canvas, color, pos, max(1, brush_size // 2))

    def on_mouse_move(self, canvas: pygame.Surface, pos: tuple,
                      color: tuple, brush_size: int):
        """Continue the stroke — draw a line from the last position."""
        if self.last_pos is not None:
            pygame.draw.line(canvas, color, self.last_pos, pos, brush_size)
        self.last_pos = pos

    def on_mouse_up(self):
        """End the stroke."""
        self.last_pos = None


# ─────────────────────────────────────────────
#  3.1  Straight Line Tool
# ─────────────────────────────────────────────
class LineTool:
    """
    Click to set the start point, drag to the end point, release to draw.
    Shows a live preview while dragging.
    """

    def __init__(self):
        self.start_pos   = None   # fixed start point
        self.preview_pos = None   # current mouse position while dragging

    # ── state helpers ──────────────────────────
    @property
    def is_drawing(self) -> bool:
        return self.start_pos is not None

    # ── events ─────────────────────────────────
    def on_mouse_down(self, pos: tuple):
        """Record the start point."""
        self.start_pos   = pos
        self.preview_pos = pos

    def on_mouse_move(self, pos: tuple):
        """Update the live-preview endpoint."""
        if self.is_drawing:
            self.preview_pos = pos

    def on_mouse_up(self, canvas: pygame.Surface, pos: tuple,
                    color: tuple, brush_size: int):
        """Commit the line to the canvas and reset."""
        if self.is_drawing:
            pygame.draw.line(canvas, color, self.start_pos, pos, brush_size)
            self.start_pos   = None
            self.preview_pos = None

    # ── rendering ──────────────────────────────
    def draw_preview(self, surface: pygame.Surface,
                     color: tuple, brush_size: int):
        """Render a semi-transparent preview line on top of the canvas."""
        if self.is_drawing and self.preview_pos:
            pygame.draw.line(surface, color,
                             self.start_pos, self.preview_pos, brush_size)


# ─────────────────────────────────────────────
#  3.3  Flood-Fill Tool
# ─────────────────────────────────────────────
class FillTool:
    """
    BFS flood fill using pygame.Surface.get_at() / .set_at().
    Stops at boundaries of a different color (exact color match).
    """

    @staticmethod
    def flood_fill(canvas: pygame.Surface, pos: tuple, fill_color: tuple):
        """
        Fill the region containing `pos` with `fill_color`.

        Parameters
        ----------
        canvas     : the drawing surface
        pos        : (x, y) where the user clicked
        fill_color : RGB tuple of the desired fill colour
        """
        x, y = pos
        if not canvas.get_rect().collidepoint(x, y):
            return

        # Normalise to plain RGB (drop alpha if present)
        target_color = tuple(canvas.get_at((x, y)))[:3]
        fill_rgb     = tuple(fill_color)[:3]

        if target_color == fill_rgb:
            return   # already the target colour — nothing to do

        w, h    = canvas.get_size()
        queue   = deque([(x, y)])
        visited = {(x, y)}

        while queue:
            cx, cy = queue.popleft()

            # Skip if another branch already changed this pixel
            if tuple(canvas.get_at((cx, cy)))[:3] != target_color:
                continue

            canvas.set_at((cx, cy), fill_color)   # ← Task 3.3 core step

            for nx, ny in ((cx - 1, cy), (cx + 1, cy),
                           (cx, cy - 1), (cx, cy + 1)):
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    def on_mouse_down(self, canvas: pygame.Surface, pos: tuple,
                      color: tuple, **_):
        """Trigger a flood fill at the clicked position."""
        self.flood_fill(canvas, pos, color)


# ─────────────────────────────────────────────
#  3.5  Text Tool
# ─────────────────────────────────────────────
class TextTool:
    """
    Click on the canvas to place a text cursor.
    Typed characters appear at that position in real time.
    Enter  → commit text permanently onto the canvas.
    Escape → cancel without drawing.
    """

    FONT_SIZE = 24

    def __init__(self):
        self.active       = False       # currently editing?
        self.position     = (0, 0)      # top-left of text block
        self.text_buffer  = ""          # characters typed so far
        self._font        = None        # initialised lazily (needs pygame)

    # ── font (lazy init after pygame.init) ──────
    def _get_font(self) -> pygame.font.Font:
        if self._font is None:
            self._font = pygame.font.SysFont("monospace", self.FONT_SIZE)
        return self._font

    # ── events ──────────────────────────────────
    def on_mouse_down(self, pos: tuple):
        """Place the cursor at the clicked position."""
        self.active      = True
        self.position    = pos
        self.text_buffer = ""

    def on_key_down(self, event: pygame.event.Event,
                    canvas: pygame.Surface, color: tuple) -> bool:
        """
        Handle keyboard input while the text tool is active.

        Returns True if the event was consumed.
        """
        if not self.active:
            return False

        if event.key == pygame.K_RETURN:
            self._commit(canvas, color)
            return True

        if event.key == pygame.K_ESCAPE:
            self._cancel()
            return True

        if event.key == pygame.K_BACKSPACE:
            self.text_buffer = self.text_buffer[:-1]
            return True

        # Append printable characters
        if event.unicode and event.unicode.isprintable():
            self.text_buffer += event.unicode
            return True

        return False

    # ── internal helpers ────────────────────────
    def _commit(self, canvas: pygame.Surface, color: tuple):
        """Render the buffered text permanently onto the canvas."""
        if self.text_buffer:
            font    = self._get_font()
            surface = font.render(self.text_buffer, True, color)
            canvas.blit(surface, self.position)
        self._cancel()

    def _cancel(self):
        self.active      = False
        self.text_buffer = ""

    # ── live preview ────────────────────────────
    def draw_preview(self, surface: pygame.Surface, color: tuple):
        """
        Draw the text buffer with a blinking cursor on the overlay surface.
        """
        if not self.active:
            return

        font = self._get_font()

        # Text typed so far
        if self.text_buffer:
            text_surf = font.render(self.text_buffer, True, color)
            surface.blit(text_surf, self.position)

        # Cursor line after the last character
        text_w = font.size(self.text_buffer)[0]
        cx = self.position[0] + text_w
        cy = self.position[1]
        if (pygame.time.get_ticks() // 500) % 2 == 0:   # blink every 500 ms
            pygame.draw.line(surface, color,
                             (cx, cy), (cx, cy + self.FONT_SIZE), 2)
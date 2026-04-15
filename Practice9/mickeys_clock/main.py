import sys
import os
import pygame
from clock import Clock


# ── Configuration ─────────────────────────────────────────────────────────────
WINDOW_TITLE  = "Mickey's Clock"
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 1          # 1 frame per second is enough; clock updates every second

# Optional: put your mickey_hand.png inside the images/ folder next to this file
IMAGES_DIR    = os.path.join(os.path.dirname(__file__), "images")
HAND_IMAGE    = os.path.join(IMAGES_DIR, "hands.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock_widget = Clock(
        screen,
        hand_image_path=HAND_IMAGE if os.path.isfile(HAND_IMAGE) else None
    )

    tick = pygame.time.Clock()

    while True:
        # ── Event handling ────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # ── Draw ──────────────────────────────────────────────────────────
        clock_widget.draw()
        pygame.display.flip()

        # ── Sync to ~1 fps (updates every second like a real clock) ───────
        tick.tick(FPS)


if __name__ == "__main__":
    main()
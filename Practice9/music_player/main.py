import sys
import os
import pygame
from player import MusicPlayer


# ── Configuration ─────────────────────────────────────────────────────────────
WINDOW_TITLE  = "Music Player"
WINDOW_WIDTH  = 620
WINDOW_HEIGHT = 540
FPS           = 30

MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    player = MusicPlayer(screen, MUSIC_DIR)
    clock  = pygame.time.Clock()

    while True:
        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _quit()

            elif event.type == pygame.KEYDOWN:
                should_quit = player.handle_key(event.key)
                if should_quit:
                    _quit()

        # ── Logic ─────────────────────────────────────────────────────────
        player.update()

        # ── Render ────────────────────────────────────────────────────────
        player.draw()
        pygame.display.flip()

        clock.tick(FPS)


def _quit():
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
import pygame
import sys

from persistence import load_settings, add_score
from racer       import Game, WINDOW_W, WINDOW_H
from ui          import (
    show_main_menu,
    show_username_entry,
    show_settings,
    show_game_over,
    show_leaderboard,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Run the in-game loop (returns result dict when session ends)
# ─────────────────────────────────────────────────────────────────────────────
def run_game(screen: pygame.Surface,
             clock:  pygame.time.Clock,
             settings: dict) -> dict:
    """
    Runs one racing session.
    Returns {"score": int, "distance": int, "coins": int, "won": bool}.
    """
    game = Game(settings)

    while not game.game_over:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.game_over = True   # exit to game-over screen

        keys = pygame.key.get_pressed()
        game.update(dt, keys)
        game.draw(screen)
        pygame.display.flip()

    return game.get_result()


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Speed Racer — TSIS3")
    clock = pygame.time.Clock()

    # Load persisted settings (Task 3.5)
    settings = load_settings()

    # State machine variables
    state       = "menu"
    username    = "Player"
    game_result = {}

    while True:
        # ── Main Menu ────────────────────────────────────────────────────────
        if state == "menu":
            action = show_main_menu(screen, clock, settings)
            if action == "play":
                state = "username"
            elif action == "leaderboard":
                state = "leaderboard"
            elif action == "settings":
                state = "settings"
            elif action == "quit":
                pygame.quit()
                sys.exit()

        # ── Username entry (Task 3.4) ─────────────────────────────────────
        elif state == "username":
            username = show_username_entry(screen, clock)
            state    = "game"

        # ── Settings (Task 3.5) ───────────────────────────────────────────
        elif state == "settings":
            settings = show_settings(screen, clock, settings)
            state    = "menu"

        # ── Leaderboard (Task 3.4 / 3.5) ────────────────────────────────
        elif state == "leaderboard":
            show_leaderboard(screen, clock)
            state = "menu"

        # ── In-game ──────────────────────────────────────────────────────
        elif state == "game":
            game_result = run_game(screen, clock, settings)
            # Persist the score (Task 3.4)
            add_score(username, game_result["score"], game_result["distance"])
            state = "gameover"

        # ── Game Over (Task 3.5) ─────────────────────────────────────────
        elif state == "gameover":
            action = show_game_over(screen, clock, game_result)
            if action == "retry":
                state = "game"
            else:
                state = "menu"


if __name__ == "__main__":
    main()
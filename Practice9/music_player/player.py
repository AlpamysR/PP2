import os
import pygame


# ── Colours & Layout ──────────────────────────────────────────────────────────
BG          = (15,  15,  25)
PANEL       = (25,  25,  45)
ACCENT      = (100, 180, 255)
ACCENT2     = (255, 100, 150)
WHITE       = (240, 240, 240)
GREY        = (130, 130, 150)
DARK_GREY   = (50,  50,  70)
GREEN       = (80,  220, 120)
RED         = (255,  80,  80)

BAR_H       = 12   # progress-bar height
CORNER_R    = 10   # rounded-rect radius


class MusicPlayer:
    """
    Wraps pygame.mixer and renders the full player UI.

    Keyboard controls
    -----------------
    P  – Play / Resume
    S  – Stop
    N  – Next track
    B  – Previous (Back) track
    Q  – Quit
    """

    def __init__(self, screen: pygame.Surface, music_dir: str):
        self.screen     = screen
        self.W, self.H  = screen.get_size()

        # ── Fonts ─────────────────────────────────────────────────────────
        self.fnt_title  = pygame.font.SysFont("Arial", 32, bold=True)
        self.fnt_track  = pygame.font.SysFont("Arial", 26, bold=True)
        self.fnt_info   = pygame.font.SysFont("Arial", 19)
        self.fnt_keys   = pygame.font.SysFont("Consolas", 17)
        self.fnt_small  = pygame.font.SysFont("Arial", 14)

        # ── Audio ─────────────────────────────────────────────────────────
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # ── Playlist ──────────────────────────────────────────────────────
        self.playlist   = self._scan(music_dir)
        self.index      = 0          # current track index
        self.is_playing = False
        self.is_stopped = True
        self.position   = 0.0        # simulated playback position (0.0–1.0)
        self._play_start_ticks = 0   # pygame.time.get_ticks() when play began
        self._track_len_ms     = 0   # estimated track length in ms

        # ── Progress-bar drag state ────────────────────────────────────────
        self._bar_rect  = None       # set during draw

    # ── Playlist helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _scan(directory: str) -> list[dict]:
        """Return a list of track dicts found in `directory`."""
        supported = (".mp3", ".wav", ".ogg", ".flac")
        tracks = []
        if not os.path.isdir(directory):
            return tracks
        for fname in sorted(os.listdir(directory)):
            if fname.lower().endswith(supported):
                path = os.path.join(directory, fname)
                tracks.append({
                    "path":  path,
                    "title": os.path.splitext(fname)[0].replace("_", " ").title(),
                    "file":  fname,
                })
        return tracks

    def _current(self) -> dict | None:
        if not self.playlist:
            return None
        return self.playlist[self.index]

    # ── Playback controls ─────────────────────────────────────────────────────
    def play(self):
        track = self._current()
        if track is None:
            return
        try:
            pygame.mixer.music.load(track["path"])
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_stopped = False
            self._play_start_ticks = pygame.time.get_ticks()
            # Estimate track length (pygame doesn't expose it for all formats)
            self._track_len_ms = self._estimate_length_ms(track["path"])
        except Exception as e:
            print(f"[MusicPlayer] Cannot play '{track['path']}': {e}")

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_stopped = True
        self.position   = 0.0

    def next_track(self):
        if not self.playlist:
            return
        self.index = (self.index + 1) % len(self.playlist)
        if self.is_playing:
            self.play()

    def prev_track(self):
        if not self.playlist:
            return
        self.index = (self.index - 1) % len(self.playlist)
        if self.is_playing:
            self.play()

    @staticmethod
    def _estimate_length_ms(path: str) -> int:
        """Best-effort length estimate without mutagen."""
        try:
            snd = pygame.mixer.Sound(path)
            return int(snd.get_length() * 1000)
        except Exception:
            return 180_000   # fallback: 3 minutes

    # ── Update (called every frame) ───────────────────────────────────────────
    def update(self):
        if self.is_playing:
            # Auto-advance when track ends
            if not pygame.mixer.music.get_busy():
                self.next_track()
                return

            elapsed = pygame.time.get_ticks() - self._play_start_ticks
            if self._track_len_ms > 0:
                self.position = min(elapsed / self._track_len_ms, 1.0)

    # ── Handle keyboard events ────────────────────────────────────────────────
    def handle_key(self, key) -> bool:
        """Returns True if the app should quit."""
        if key == pygame.K_p:
            if self.is_stopped:
                self.play()
            elif not self.is_playing:
                pygame.mixer.music.unpause()
                self.is_playing = True
        elif key == pygame.K_s:
            self.stop()
        elif key == pygame.K_n:
            self.next_track()
        elif key == pygame.K_b:
            self.prev_track()
        elif key == pygame.K_q or key == pygame.K_ESCAPE:
            return True          # signal quit
        return False

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG)
        self._draw_header()
        self._draw_now_playing()
        self._draw_progress_bar()
        self._draw_playlist()
        self._draw_controls_legend()

    # ─── Sub-draw helpers ─────────────────────────────────────────────────────
    def _draw_header(self):
        title = self.fnt_title.render("🎵  Music Player", True, ACCENT)
        self.screen.blit(title, (self.W // 2 - title.get_width() // 2, 18))
        # divider
        pygame.draw.line(self.screen, DARK_GREY,
                         (20, 60), (self.W - 20, 60), 1)

    def _draw_now_playing(self):
        track = self._current()
        y = 80

        # Panel background
        panel_rect = pygame.Rect(20, y, self.W - 40, 90)
        pygame.draw.rect(self.screen, PANEL, panel_rect, border_radius=CORNER_R)

        if track is None:
            msg = self.fnt_info.render("No tracks found in music/ folder", True, GREY)
            self.screen.blit(msg, (40, y + 30))
            return

        # Status badge
        if self.is_playing:
            badge_text, badge_col = "▶  PLAYING", GREEN
        elif not self.is_stopped:
            badge_text, badge_col = "⏸  PAUSED", ACCENT
        else:
            badge_text, badge_col = "⏹  STOPPED", RED

        badge = self.fnt_small.render(badge_text, True, badge_col)
        self.screen.blit(badge, (40, y + 10))

        # Track title
        name = self.fnt_track.render(track["title"], True, WHITE)
        self.screen.blit(name, (40, y + 30))

        # File name
        fname = self.fnt_small.render(track["file"], True, GREY)
        self.screen.blit(fname, (40, y + 62))

        # Track index indicator  e.g.  "2 / 5"
        idx_text = f"{self.index + 1} / {len(self.playlist)}"
        idx_surf = self.fnt_info.render(idx_text, True, ACCENT)
        self.screen.blit(idx_surf, (self.W - 40 - idx_surf.get_width(), y + 35))

    def _draw_progress_bar(self):
        y     = 190
        bar_x = 20
        bar_w = self.W - 40

        # Background track
        bg_rect = pygame.Rect(bar_x, y, bar_w, BAR_H)
        pygame.draw.rect(self.screen, DARK_GREY, bg_rect, border_radius=6)

        # Filled portion
        fill_w = int(bar_w * self.position)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x, y, fill_w, BAR_H)
            pygame.draw.rect(self.screen, ACCENT, fill_rect, border_radius=6)

        # Thumb
        thumb_x = bar_x + fill_w
        pygame.draw.circle(self.screen, ACCENT2,
                           (thumb_x, y + BAR_H // 2), BAR_H)

        # Store rect for potential mouse interaction
        self._bar_rect = bg_rect

        # Time labels
        elapsed_s = int(self.position * self._track_len_ms / 1000) if self._track_len_ms else 0
        total_s   = self._track_len_ms // 1000 if self._track_len_ms else 0
        left  = self.fnt_small.render(f"{elapsed_s // 60}:{elapsed_s % 60:02d}", True, GREY)
        right = self.fnt_small.render(f"{total_s   // 60}:{total_s   % 60:02d}", True, GREY)
        self.screen.blit(left,  (bar_x, y + BAR_H + 4))
        self.screen.blit(right, (bar_x + bar_w - right.get_width(), y + BAR_H + 4))

    def _draw_playlist(self):
        y_start = 230
        label   = self.fnt_info.render("Playlist", True, ACCENT)
        self.screen.blit(label, (20, y_start))
        pygame.draw.line(self.screen, DARK_GREY,
                         (20, y_start + 24), (self.W - 20, y_start + 24), 1)

        if not self.playlist:
            msg = self.fnt_small.render(
                "Place .mp3 / .wav / .ogg files in the music/ folder", True, GREY)
            self.screen.blit(msg, (30, y_start + 36))
            return

        row_h   = 34
        visible = (self.H - y_start - 110) // row_h   # how many rows fit

        # Centre current track in viewport
        start   = max(0, self.index - visible // 2)
        end     = min(len(self.playlist), start + visible)

        for i, track in enumerate(self.playlist[start:end], start=start):
            ry = y_start + 30 + (i - start) * row_h
            row_rect = pygame.Rect(20, ry, self.W - 40, row_h - 4)

            if i == self.index:
                pygame.draw.rect(self.screen, PANEL, row_rect, border_radius=6)
                num_col  = ACCENT2
                name_col = WHITE
            else:
                num_col  = GREY
                name_col = GREY

            num  = self.fnt_small.render(f"{i + 1:02d}", True, num_col)
            name = self.fnt_info.render(track["title"], True, name_col)
            self.screen.blit(num,  (30, ry + 8))
            self.screen.blit(name, (65, ry + 6))

    def _draw_controls_legend(self):
        keys = [
            ("[P]", "Play"),
            ("[S]", "Stop"),
            ("[N]", "Next"),
            ("[B]", "Back"),
            ("[Q]", "Quit"),
        ]
        y   = self.H - 52
        pygame.draw.line(self.screen, DARK_GREY, (20, y - 6), (self.W - 20, y - 6), 1)

        total_w = (self.W - 40)
        col_w   = total_w // len(keys)
        for i, (key, action) in enumerate(keys):
            x     = 20 + i * col_w + col_w // 2
            k_s   = self.fnt_keys.render(key,    True, ACCENT)
            a_s   = self.fnt_keys.render(action, True, GREY)
            self.screen.blit(k_s, (x - k_s.get_width() // 2,       y))
            self.screen.blit(a_s, (x - a_s.get_width() // 2, y + 20))
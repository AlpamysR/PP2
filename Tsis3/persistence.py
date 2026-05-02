"""
persistence.py — Handles reading and writing of settings.json
and leaderboard.json (Task 3.4 leaderboard persistence, Task 3.5 settings).
"""

import json
import os

SETTINGS_FILE    = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  "red",
    "difficulty": "medium",
}


# ── Settings ──────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    """Load settings from file; fall back to defaults for missing keys."""
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        return {**DEFAULT_SETTINGS, **data}
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    """Persist settings to settings.json."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


# ── Leaderboard ───────────────────────────────────────────────────────────────

def load_leaderboard() -> list:
    """Return the list of top-score entries (up to 10)."""
    try:
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_leaderboard(entries: list):
    """Write the leaderboard list to leaderboard.json."""
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def add_score(name: str, score: int, distance: float) -> list:
    """
    Insert a new entry, keep only the top 10 sorted by score,
    persist, and return the updated list.
    """
    entries = load_leaderboard()
    entries.append({
        "rank":     0,
        "name":     name,
        "score":    score,
        "distance": round(distance),
    })
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:10]
    for i, e in enumerate(entries):
        e["rank"] = i + 1
    save_leaderboard(entries)
    return entries
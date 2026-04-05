import json
import os

PREF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preferences.json")

DEFAULT_PREFS = {
    "theme": "modern",
    "auto_play_speed": 0.5,
    "fullscreen": False,
    "stats_panel_visible": True
}


def load_preferences():
    if not os.path.exists(PREF_PATH):
        save_preferences(DEFAULT_PREFS)
        return DEFAULT_PREFS.copy()

    try:
        with open(PREF_PATH, "r") as f:
            data = json.load(f)
    except Exception:
        save_preferences(DEFAULT_PREFS)
        return DEFAULT_PREFS.copy()

    # Ensure missing keys get defaults
    for key, value in DEFAULT_PREFS.items():
        data.setdefault(key, value)

    return data


def save_preferences(prefs):
    with open(PREF_PATH, "w") as f:
        json.dump(prefs, f, indent=4)
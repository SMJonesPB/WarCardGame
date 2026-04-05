import tkinter as tk
from gui.app import WarApp
from gui.splash import SplashScreen
from gui.theme_manager import THEMES
from preferences import load_preferences
import winsparkle
from config import APP_VERSION

def start_main_app():
    app = WarApp(root, theme_name)

def init_updates():
    winsparkle.win_sparkle_set_appcast_url(
        "https://raw.githubusercontent.com/SMJonesPB/WarCardGame/appcast.xml"
    )
    winsparkle.win_sparkle_set_app_details(
        "SMJonesPB",   # company/author
        "War",    # app name
        APP_VERSION   # version
    )
    winsparkle.win_sparkle_init()

if __name__ == "__main__":
    init_updates()
    root = tk.Tk()
    root.withdraw()

    # Load preferences to get theme
    prefs = load_preferences()
    theme_name = prefs.get("theme", "modern")
    theme = THEMES.get(theme_name, THEMES["modern"])

    # Show splash with theme
    SplashScreen(root, theme, on_finish=start_main_app)

    root.mainloop()
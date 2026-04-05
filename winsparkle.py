import ctypes
import os
import sys

# Locate WinSparkle.dll
def _dll_path():
    if hasattr(sys, "_MEIPASS"):
        # Running from PyInstaller bundle
        return os.path.join(sys._MEIPASS, "WinSparkle.dll")
    return os.path.join(os.path.dirname(__file__), "WinSparkle.dll")

_win_sparkle = ctypes.WinDLL(_dll_path())

# Function wrappers
def win_sparkle_set_appcast_url(url: str):
    _win_sparkle.win_sparkle_set_appcast_url(url.encode("utf-8"))

def win_sparkle_set_app_details(company: str, appname: str, version: str):
    _win_sparkle.win_sparkle_set_app_details(
        company.encode("utf-8"),
        appname.encode("utf-8"),
        version.encode("utf-8")
    )

def win_sparkle_init():
    _win_sparkle.win_sparkle_init()

def win_sparkle_check_update_with_ui():
    _win_sparkle.win_sparkle_check_update_with_ui()
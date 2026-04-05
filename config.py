import os, sys

def resource_path(relative):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(__file__), relative)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = resource_path("../Card Pictures")
APP_VERSION = "1.0.0.1"
RELEASE_NOTES_URL = "https://raw.githubusercontent.com/SMJonesPB/WarCardGame/release_notes.md"
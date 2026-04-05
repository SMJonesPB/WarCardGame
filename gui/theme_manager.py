import tkinter as tk
from tkinter import ttk


# ==========================
# Theme Definitions
# ==========================

THEMES = {
    "modern": {
        "bg": "#2b2b2b",
        "fg": "white",
        "table_bg": "#2b2b2b",
        "button_bg": "#444",
        "button_active": "#555",
        "frame_bg": "#2b2b2b",
        "text_bg": "#1e1e1e",
        "text_fg": "white",
    },

    "casino_dark": {
        "bg": "#0b3d1f",
        "fg": "#f5e6c8",
        "table_bg": "#0b3d1f",
        "button_bg": "#1a5c33",
        "button_active": "#267a47",
        "frame_bg": "#0b3d1f",
        "text_bg": "#062612",
        "text_fg": "#f5e6c8",
    },

    "casino_light": {
        "bg": "#0f7a2a",
        "fg": "black",
        "table_bg": "#0f7a2a",
        "button_bg": "#1fa347",
        "button_active": "#28c75a",
        "frame_bg": "#0f7a2a",
        "text_bg": "#0a5c1e",
        "text_fg": "black",
    }
}


# ==========================
# Theme Application
# ==========================

def apply_theme(app, theme_name):
    theme = THEMES.get(theme_name, THEMES["modern"])

    bg = theme["bg"]
    fg = theme["fg"]

    # Update root window
    app.configure(bg=bg)

    # Update ttk styles
    style = ttk.Style(app)
    style.theme_use("clam")

    style.configure(".", background=bg, foreground=fg, fieldbackground=bg)

    style.configure("TFrame", background=bg)
    style.configure("TLabelframe", background=bg, foreground=fg)
    style.configure("TLabelframe.Label", background=bg, foreground=fg)
    style.configure("TLabel", background=bg, foreground=fg)

    style.configure("TButton",
                    background=theme["button_bg"],
                    foreground=fg,
                    padding=6)
    style.map("TButton",
              background=[("active", theme["button_active"])])

    style.configure("TScale", background=bg)

    # Update text widget colors
    if hasattr(app, "log_text"):
        app.log_text.configure(bg=theme["text_bg"], fg=theme["text_fg"])

    # Update table background
    if hasattr(app, "table_frame"):
        app.table_frame.configure(style="TFrame")
        style.configure("Table.TFrame", background=theme["table_bg"])


    # Update all frames recursively
    _update_children_colors(app, theme)


def _update_children_colors(widget, theme):
    """Recursively update widget backgrounds."""
    for child in widget.winfo_children():
        try:
            child.configure(bg=theme["bg"])
        except:
            pass
        _update_children_colors(child, theme)
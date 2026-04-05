import tkinter as tk
from tkinter import ttk

class SplashScreen(tk.Toplevel):
    def __init__(self, master, theme, on_finish):
        super().__init__(master)

        self.on_finish = on_finish
        self.theme = theme

        # Theme-aware colors
        self.bg = theme["bg"]
        self.fg = theme["fg"]
        self.accent = theme["button_bg"]

        self.overrideredirect(True)
        self.configure(bg=self.bg)

        # Center window
        width, height = 420, 260
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (width // 2)
        y = (sh // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Title
        self.title_label = tk.Label(
            self, text="WAR",
            font=("Segoe UI", 22, "bold"),
            fg=self.fg, bg=self.bg
        )
        self.title_label.pack(pady=25)

        # Animated loading text
        self.loading_label = tk.Label(
            self, text="Loading",
            font=("Segoe UI", 14),
            fg=self.fg, bg=self.bg
        )
        self.loading_label.pack(pady=10)

        self.loading_frames = ["Loading", "Loading.", "Loading..", "Loading..."]
        self.frame_index = 0

        # Progress bar
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Splash.Horizontal.TProgressbar",
            troughcolor=self.bg,
            background=self.accent,
            bordercolor=self.bg,
            lightcolor=self.accent,
            darkcolor=self.accent
        )

        self.progress = ttk.Progressbar(
            self,
            orient="horizontal",
            mode="determinate",
            length=300,
            style="Splash.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=15)

        # Copyright
        self.copy_label = tk.Label(
            self,
            text="© 2026 SMJonesPB — All Rights Reserved",
            font=("Segoe UI", 9),
            fg=self.fg,
            bg=self.bg
        )
        self.copy_label.pack(side="bottom", pady=10)

        # Start animations
        self.animate_loading()
        self.animate_progress()

    # Animate "Loading..."
    def animate_loading(self):
        self.loading_label.config(text=self.loading_frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.loading_frames)
        self.after(300, self.animate_loading)

    # Animate progress bar
    def animate_progress(self):
        if self.progress["value"] < 100:
            self.progress["value"] += 2
            self.after(40, self.animate_progress)
        else:
            self.start_fade_out()

    # Fade-out animation
    def start_fade_out(self):
        self.fade_alpha = 1.0
        self.fade_step()

    def fade_step(self):
        self.fade_alpha -= 0.05
        if self.fade_alpha <= 0:
            self.destroy()
            self.on_finish()
            return

        self.attributes("-alpha", self.fade_alpha)
        self.after(30, self.fade_step)
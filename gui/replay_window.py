# gui/replay_window.py

import tkinter as tk
from tkinter import ttk


class ReplayWindow(tk.Toplevel):
    """
    A window that replays a stored ReplayLog step-by-step.
    """
    def __init__(self, master, replay_log, app_reference):
        """
        master: root window
        replay_log: ReplayLog instance
        app_reference: your WarApp instance (for card rendering)
        """
        super().__init__(master)
        self.title("Replay Viewer")
        self.geometry("600x500")
        self.configure(bg="#2b2b2b")

        self.replay_log = replay_log
        self.app = app_reference  # to use _update_card_display()

        self.current_index = 0
        self.auto_play = False
        self.auto_job = None

        # -----------------------------
        # UI Layout
        # -----------------------------
        title = ttk.Label(self, text="Replay Viewer", font=("Segoe UI", 16, "bold"))
        title.pack(pady=10)
        title_text = getattr(self.replay_log, "title", "Replay")
        game_num = getattr(self.replay_log, "game_number", None)

        if game_num is not None:
            title_text = f"{title_text} (Game #{game_num})"

        self.game_label = ttk.Label(self, text=title_text, font=("Segoe UI", 12))
        self.game_label.pack(pady=5)

        # --- Replay Summary Panel ---
        summary_frame = ttk.Frame(self)
        summary_frame.pack(pady=10)

        # Extract summary info
        rounds = getattr(self.replay_log, "total_rounds", "?")
        wars = getattr(self.replay_log, "total_wars", "?")
        max_chain = getattr(self.replay_log, "max_chain", "?")
        winner = getattr(self.replay_log, "final_winner", "?")
        game_num = getattr(self.replay_log, "game_number", "?")

        summary_text = (
            f"Game #{game_num} | "
            f"Rounds: {rounds} | "
            f"Wars: {wars} | "
            f"Max Chain: {max_chain} | "
            f"Winner: {winner}"
        )

        self.summary_label = ttk.Label(summary_frame, text=summary_text, font=("Segoe UI", 10))
        self.summary_label.pack()

        # Round info
        self.round_label = ttk.Label(self, text="Round: 0", font=("Segoe UI", 12))
        self.round_label.pack(pady=5)

        # War-depth indicator
        self.war_label = ttk.Label(self, text="", font=("Segoe UI", 11))
        self.war_label.pack(pady=5)

        # Card display frame
        self.cards_frame = ttk.Frame(self)
        self.cards_frame.pack(pady=10)

        self.p1_card_label = tk.Label(self.cards_frame, bg="#2b2b2b")
        self.p1_card_label.pack(side=tk.LEFT, padx=20)

        self.p2_card_label = tk.Label(self.cards_frame, bg="#2b2b2b")
        self.p2_card_label.pack(side=tk.RIGHT, padx=20)

        # Status
        self.status_label = ttk.Label(self, text="", font=("Segoe UI", 11))
        self.status_label.pack(pady=5)

        # War chain visualization
        self.chain_frame = ttk.Frame(self)
        self.chain_frame.pack(pady=10)

        self.chain_label = ttk.Label(self.chain_frame, text="", font=("Segoe UI", 11))
        self.chain_label.pack()
        self.max_chain_label = ttk.Label(self, text="", font=("Segoe UI", 10))
        self.max_chain_label.pack()

        self.max_chain_label.config(
            text=f"Max War Chain This Game: {self.replay_log.max_chain}"
        )



        # Controls
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=15)

        ttk.Button(control_frame, text="Next Round", command=self.next_round).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Restart Replay", command=self.restart).pack(side=tk.LEFT, padx=5)

        self.auto_btn = ttk.Button(control_frame, text="Auto Play", command=self.toggle_auto)
        self.auto_btn.pack(side=tk.LEFT, padx=5)

        # Start with first frame
        self.show_round(0)

    # -----------------------------
    # Replay Logic
    # -----------------------------

    def restart(self):
        self.current_index = 0
        self.stop_auto()
        self.show_round(0)
        self._render_war_chain(0)


    def toggle_auto(self):
        self.auto_play = not self.auto_play
        if self.auto_play:
            self.auto_btn.config(text="Auto: ON")
            self.schedule_next()
        else:
            self.auto_btn.config(text="Auto Play")
            self.stop_auto()

    def stop_auto(self):
        self.auto_play = False
        self.auto_btn.config(text="Auto Play")
        if self.auto_job:
            try:
                self.after_cancel(self.auto_job)
            except:
                pass
        self.auto_job = None

    def schedule_next(self):
        if not self.auto_play:
            return
        self.auto_job = self.after(600, self.next_round)  # 0.6 sec per round

    def next_round(self):
        if self.current_index + 1 < len(self.replay_log.rounds):
            self.current_index += 1
            self.show_round(self.current_index)
            if self.auto_play:
                self.schedule_next()
        else:
            self.status_label.config(text=f"Replay finished — Winner: {self.replay_log.final_winner}")
            self.stop_auto()

    # -----------------------------
    # Rendering a round
    # -----------------------------

    def show_round(self, index):
        data = self.replay_log.rounds[index]

        p1 = data["p1_card"]
        p2 = data["p2_card"]
        winner = data["winner"]
        depth = data["war_depth"]

        # Update round label
        self.round_label.config(text=f"Round: {index + 1}")

        # War-depth highlighting
        if depth > 0:
            self.war_label.config(text=f"WAR! Depth {depth}", foreground="red")
        else:
            self.war_label.config(text="", foreground="white")
        
        # War-chain visualization
        self._render_war_chain(depth)


        # Use WarApp's existing card renderer
        img1 = self.app.card_images.get(p1)
        img2 = self.app.card_images.get(p2)


        self.p1_card_label.image = img1
        self.p2_card_label.image = img2

        self.p1_card_label.config(image=img1)
        self.p2_card_label.config(image=img2)

        # Status
        if depth > 0:
            self.status_label.config(text=f"War! Depth {depth}")
        else:
            self.status_label.config(text=f"Round Winner: {winner}")

    def _render_war_chain(self, depth):
        """
        Visualizes the war chain depth.
        depth = 0 → no war
        depth = 1+ → show chain
        """
        if depth <= 0:
            self.chain_label.config(text="")
            return

        # Option 1: vertical flames
        flames = "🔥" * depth
        text = f"WAR CHAIN: {flames}  (Depth {depth})"

        self.chain_label.config(text=text, foreground="red")

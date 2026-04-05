import os
import time
from time import time
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import queue
import traceback
import time
from gui.release_notes_window import ReleaseNotesWindow
from engine.bias_engine import DeckBiasTracker
from stats.tracker import StatsTracker
from engine.war_engine import WarEngine
from config import IMAGE_FOLDER
from gui.theme_manager import apply_theme
from preferences import load_preferences, save_preferences
from gui.replay_window import ReplayWindow
from gui.bias_window import BiasWindow
from config import APP_VERSION


# ==========================
# Modern Flat Theme Styles
# ==========================

def apply_modern_theme(root):
    style = ttk.Style(root)

    # Use default theme as base
    style.theme_use("clam")

    # General widget styling
    style.configure(".", 
                    background="#2b2b2b",
                    foreground="white",
                    fieldbackground="#3c3c3c")

    # Buttons
    style.configure("TButton",
                    background="#444",
                    foreground="white",
                    padding=6)
    style.map("TButton",
              background=[("active", "#555")])

    # Frames
    style.configure("TFrame", background="#2b2b2b")
    style.configure("TLabelframe", background="#2b2b2b", foreground="white")
    style.configure("TLabelframe.Label", background="#2b2b2b", foreground="white")

    # Labels
    style.configure("TLabel", background="#2b2b2b", foreground="white")

    # Scale
    style.configure("TScale", background="#2b2b2b")


# ==========================
# Main GUI Application
# ==========================

class WarApp(tk.Toplevel):
    def __init__(self, master, theme):
        super().__init__(master)

        # 1. Load preferences FIRST
        self.prefs = load_preferences()
        self.current_theme = self.prefs["theme"]

        # 2. Apply theme BEFORE building UI
        apply_theme(self, self.current_theme)

        # 3. Load theme dict
        from gui.theme_manager import THEMES
        theme = THEMES[self.current_theme]
        self.bg = theme["bg"]
        self.fg = theme["fg"]
        self.accent = theme["button_bg"]

        # 4. Initialize attributes
        self.fullscreen = False
        self.auto_play = False
        self.auto_play_job = None
        self.card_images = {}
        self.card_image_folder = IMAGE_FOLDER
        self.card_width = 150
        self.card_height = 218
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)


        # 5. Create engine + stats
        self.engine = WarEngine(update_callback=self.update_deck_labels)
        self.stats = StatsTracker()

        # 6. Build UI AFTER theme has been applied
        self._build_ui()

        # 7. Build menu
        self._build_menu()
        replay_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Replays", menu=replay_menu)
        replay_menu.add_command(
            label="Shortest Game",
            command=lambda: self.open_replay(self.replay_engine.shortest)
        )

        replay_menu.add_command(
            label="Longest Game",
            command=lambda: self.open_replay(self.replay_engine.longest)
        )

        replay_menu.add_command(
            label="Most Wars",
            command=lambda: self.open_replay(self.replay_engine.most_wars)
        )

        replay_menu.add_command(
            label="Longest War Chain",
            command=lambda: self.open_replay(self.replay_engine.longest_chain)
        )

        replay_menu.add_command(
        label="Choose Replay...",
        command=lambda: (
            lambda log: self.open_replay(log) if log else None
            )(self.choose_replay_dialog())
        )


        # 8. Restore stats panel visibility
        if not self.prefs["stats_panel_visible"]:
            self.stats_frame.pack_forget()
            self.stats_toggle_btn.config(text="Show Stats")

        # 9. Restore fullscreen
        self.after(50, self._restore_fullscreen)

        # 10. Finish setup
        self._update_stats_labels()
        self._log("Game ready. Click Start to begin.")

    # ==========================
    # UI Construction
    # ==========================

    def _build_ui(self):
        # ---------- Top Controls ----------
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.start_btn = ttk.Button(control_frame, text="Start", command=self.start_game)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_auto_play)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(control_frame, text="Reset", command=self.reset_game)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.auto_btn = ttk.Button(control_frame, text="Auto-Play", command=self.toggle_auto_play)
        self.auto_btn.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=(20, 5))
        self.speed_var = tk.DoubleVar(value=self.prefs["auto_play_speed"])
        self.speed_slider = ttk.Scale(control_frame, from_=1.5, to=0.5,
                                    orient=tk.HORIZONTAL, variable=self.speed_var)
        self.speed_slider.pack(side=tk.LEFT, padx=5)
        self.speed_slider.configure(command=self._on_speed_change)


        self.sim_btn = ttk.Button(control_frame, text="Simulation Mode", command=self.run_simulation)
        self.sim_btn.pack(side=tk.LEFT, padx=20)

        self.stats_toggle_btn = ttk.Button(control_frame, text="Hide Stats", command=self.toggle_stats_panel)
        self.stats_toggle_btn.pack(side=tk.LEFT, padx=5)

        self.fullscreen_btn = ttk.Button(control_frame, text="Full Screen", command=self.toggle_fullscreen)
        self.fullscreen_btn.pack(side=tk.RIGHT, padx=5)

        # ---------- Table Area ----------
        self.table_frame = ttk.Frame(self, style="Table.TFrame")
        table_frame = self.table_frame
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Player 1
        p1_frame = ttk.Frame(table_frame)
        p1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(p1_frame, text="Player 1", font=("Segoe UI", 12, "bold")).pack(pady=5)
        self.p1_deck_label = ttk.Label(p1_frame, text="Deck: 26")
        self.p1_deck_label.pack(pady=5)

        # Create persistent center frame
        self.center_frame = ttk.Frame(table_frame)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.round_label = ttk.Label(self.center_frame, text="Round: 0", font=("Segoe UI", 12))
        self.round_label.pack(pady=5)

        # Create persistent cards frame INSIDE center_frame
        self.cards_frame = ttk.Frame(self.center_frame)
        self.cards_frame.pack(pady=10)

        # BOTH card labels must live in the SAME persistent frame
        self.center_p1_card = tk.Label(self.cards_frame, bg=self.bg)
        self.center_p1_card.pack(side=tk.LEFT, padx=20)

        self.center_p2_card = tk.Label(self.cards_frame, bg=self.bg)
        self.center_p2_card.pack(side=tk.RIGHT, padx=20)

        self.status_label = ttk.Label(self.center_frame, text="", font=("Segoe UI", 11))
        self.status_label.pack(pady=5)


        # Player 2
        p2_frame = ttk.Frame(table_frame)
        p2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(p2_frame, text="Player 2", font=("Segoe UI", 12, "bold")).pack(pady=5)
        self.p2_deck_label = ttk.Label(p2_frame, text="Deck: 26")
        self.p2_deck_label.pack(pady=5)

        # ---------- Bottom: Stats + History ----------
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Stats panel
        self.stats_frame = ttk.LabelFrame(bottom_frame, text="Stats")
        self.stats_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.game_stats_label = ttk.Label(self.stats_frame, text="", justify=tk.LEFT)
        self.game_stats_label.pack(anchor="w", padx=5, pady=5)

        self.session_stats_label = ttk.Label(self.stats_frame, text="", justify=tk.LEFT)
        self.session_stats_label.pack(anchor="w", padx=5, pady=5)

        # History log
        log_frame = ttk.LabelFrame(bottom_frame, text="History")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = tk.Text(log_frame, height=12, state=tk.DISABLED,
                                wrap=tk.WORD, bg="#1e1e1e", fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)


    # ==========================
    # Utility
    # ==========================

    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _load_card_image(self, card):
        if card is None:
            return None

        filename = self._card_to_filename(card)
        path = os.path.join(self.card_image_folder, filename)

        if filename in self.card_images:
            return self.card_images[filename]

        img = Image.open(path)
        img = img.resize((self.card_width, self.card_height), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img, master=self)
        self.card_images[filename] = tk_img
        return tk_img

    def _card_to_filename(self, card):
        # Card may be a tuple like ("6", "Heart")
        if isinstance(card, tuple):
            rank, suit = card
        else:
            rank = card.rank
            suit = card.suit

        # Normalize suit names to match your filenames
        suit_map = {
            "heart": "hearts",
            "hearts": "hearts",
            "diamond": "diamonds",
            "diamonds": "diamonds",
            "club": "clubs",
            "clubs": "clubs",
            "spade": "spades",
            "spades": "spades"
        }

        suit = suit.lower()
        suit = suit_map.get(suit, suit)

        rank = str(rank).lower()

        # ⭐ Your filenames use spaces, not underscores
        return f"{rank} of {suit}.png"

    def _update_card_display(self, p1_card, p2_card):
        img1 = self._load_card_image(p1_card)
        img2 = self._load_card_image(p2_card)

        # CRITICAL: store references on the label widgets
        self.center_p1_card.image = img1
        self.center_p2_card.image = img2

        self.center_p1_card.config(image=img1, text="")
        self.center_p2_card.config(image=img2, text="")

    def _update_stats_labels(self):
        game_text = (
            f"Game Stats:\n"
            f"  Rounds: {self.engine.rounds_played}\n"
            f"  Wars: {self.engine.wars}\n"
            f"  Max War Chain: {self.engine.max_war_chain}\n"
            f"  P1 Deck: {len(self.engine.p1)}\n"
            f"  P2 Deck: {len(self.engine.p2)}"
        )
        self.game_stats_label.config(text=game_text)

        s = self.stats.session_summary()
        session_text = (
            f"Session Stats:\n"
            f"  Games: {s['total_games']}\n"
            f"  P1 Wins: {s['p1_wins']}\n"
            f"  P2 Wins: {s['p2_wins']}\n"
            f"  Ties: {s['ties']}\n"
            f"  Avg Rounds: {s['avg_rounds']:.2f}\n"
            f"  Avg Wars: {s['avg_wars']:.2f}\n"
            f"  Max War Chain Overall: {s['max_war_chain_overall']}"
        )
        self.session_stats_label.config(text=session_text)

    def _on_speed_change(self, value):
        """Save auto-play speed to preferences whenever the slider moves."""
        self.prefs["auto_play_speed"] = float(value)
        save_preferences(self.prefs)

    def update_deck_labels(self):
        self.p1_deck_label.config(text=f"Deck: {len(self.engine.p1)}")
        self.p2_deck_label.config(text=f"Deck: {len(self.engine.p2)}")
        self.round_label.config(text=f"Round: {self.engine.rounds_played}")
        self.update_idletasks()

    def open_replay(self, replay_log):
        ReplayWindow(self, replay_log, self)




    # ==========================
    # Controls
    # ==========================

    def start_game(self):
        if self.engine.has_winner():
            self.engine.reset_decks()
            self._log("New game started.")
            self.status_label.config(text="New game started.")
            self._update_card_display(None, None)
        self.play_one_round()

    def reset_game(self):
        self.stop_auto_play()
        self.engine.reset_decks()
        self._update_card_display(None, None)
        self._update_stats_labels()
        self.status_label.config(text="Game reset.")
        self._log("Game reset.")

    def toggle_auto_play(self):
        self.auto_play = not self.auto_play

        if self.auto_play:
            self.auto_btn.config(text="Auto-Play: ON")
            self._schedule_next_round()
        else:
            self.auto_btn.config(text="Auto-Play")
            if self.auto_play_job:
                try:
                    self.after_cancel(self.auto_play_job)
                except:
                    pass
                self.auto_play_job = None



    def stop_auto_play(self):
        self.auto_play = False
        self.auto_btn.config(text="Auto-Play")
        if self.auto_play_job:
            self.after_cancel(self.auto_play_job)
            self.auto_play_job = None
        self._log("Auto-play stopped.")

    def _schedule_next_round(self):
        if not self.auto_play:
            return

        delay_ms = int(self.prefs["auto_play_speed"] * 1000)
        self.auto_play_job = self.after(delay_ms, self.play_one_round)



    def play_one_round(self):
        # Check for game over BEFORE playing
        winner = self.engine.has_winner()
        if winner:
            self.status_label.config(text=f"Game over: {winner}")
            self._log(f"Game over: {winner}")
            self.stats.record_game(self.engine, winner)
            self._update_stats_labels()
            self.auto_play = False
            self.auto_btn.config(text="Auto-Play")
            return

        # Play the round
        result = self.engine.play_round()

        # Update GUI
        for line in result["log_lines"]:
            self._log(line)

        self._update_card_display(result["p1_card"], result["p2_card"])
        self._update_stats_labels()

        # Check again for game over AFTER playing
        winner = self.engine.has_winner()
        if winner:
            self.status_label.config(text=f"Game over: {winner}")
            self._log(f"Game over: {winner}")
            self.stats.record_game(self.engine, winner)
            self._update_stats_labels()
            self.auto_play = False
            self.auto_btn.config(text="Auto-Play")
            return

        # ⭐ Only schedule next round if auto_play is still ON
        if self.auto_play:
            self._schedule_next_round()



    def run_simulation(self):
        from engine.probability_engine import ProbabilityEngine
        from engine.replay_engine import ReplayEngine
        
        self.sim_start_time = time.time()
        n = simpledialog.askinteger(
            "Simulation",
            "Run how many games?",
            minvalue=1,
            maxvalue=200000
        )
        if not n:
            return

        # fresh state
        self.sim_total = n
        self.sim_current = 0
        self.sim_cancelled = False
        self.sim_forced_war_ends = 0
        self.sim_prob = ProbabilityEngine()
        self.sim_replay = ReplayEngine()
        self.sim_bias = DeckBiasTracker()

        if hasattr(self, "sim_engine"):
            del self.sim_engine
        if hasattr(self, "sim_log"):
            del self.sim_log

        self._open_simulation_progress()

        # start loop ONCE
        self.after(10, self._simulation_step)

    def _simulation_step(self):
        try:
            self._simulation_step_impl()
        except Exception as e:
            print("SIMULATION ERROR:", e)
            print(traceback.format_exc())  # 🔑 full stack trace

            self.sim_cancelled = True
            if hasattr(self, "sim_window") and self.sim_window.winfo_exists():
                self.sim_window.destroy()
            messagebox.showerror("Simulation Error", f"Simulation stopped:\n{e}")

    
    def _simulation_step_impl(self):
        if self.sim_cancelled:
            if hasattr(self, "sim_window") and self.sim_window.winfo_exists():
                self.sim_window.destroy()
            messagebox.showinfo("Simulation", "Simulation cancelled.")
            return

        # start a new game if needed
        if not hasattr(self, "sim_engine"):
            from engine.war_engine import WarEngine
            self.sim_engine = WarEngine(update_callback=None)
            self.sim_log = self.sim_replay.start_new_log()
            self.sim_rounds_in_game = 0          # 🔑 add this

        # play ONE round
        result = self.sim_engine.play_round()
        self.sim_log.add_round(
            result["p1_card"],
            result["p2_card"],
            result["winner"],
            result["war_depth"]
        )
        self.sim_rounds_in_game += 1            # Track rounds

        winner = self.sim_engine.has_winner()

        # Safety valve: force‑end pathological games
        MAX_ROUNDS_PER_GAME = 5000
        if winner is None and self.sim_rounds_in_game >= MAX_ROUNDS_PER_GAME:
            # decide winner by deck size, or tie
            p1_len = len(self.sim_engine.p1)
            p2_len = len(self.sim_engine.p2)
            if p1_len > p2_len:
                winner = "P1"
            elif p2_len > p1_len:
                winner = "P2"
            else:
                winner = "tie"

        if winner is not None:
            self.sim_replay.finalize_log(self.sim_log, self.sim_engine, winner)
            self.sim_prob.record_game(self.sim_engine, winner)
            self.sim_bias.merge(self.sim_engine.bias)
            self.sim_current += 1

            if hasattr(self, "sim_progress") and self.sim_progress.winfo_exists():
                percent = int((self.sim_current / self.sim_total) * 100)
                self.sim_progress["value"] = percent
                
                # ETA calculation
                elapsed = time.time() - self.sim_start_time
                if self.sim_current > 0:
                    rate = self.sim_current / elapsed
                    remaining = (self.sim_total - self.sim_current) / rate
                    eta_text = f"ETA: {remaining:.1f}s"
                else:
                    eta_text = "ETA: calculating..."

                # Update window title or add a label
                self.sim_window.title(f"Simulation Running — {eta_text}")

            del self.sim_engine
            del self.sim_log
            del self.sim_rounds_in_game

            if self.sim_current >= self.sim_total:
                if hasattr(self, "sim_window") and self.sim_window.winfo_exists():
                    self.sim_window.destroy()

                self.replay_engine = self.sim_replay

                win_rates = self.sim_prob.win_rates()
                self._log("Simulation complete.")
                self._log(f"P1 Win Rate: {win_rates['p1']*100:.3f}%")
                self._log(f"P2 Win Rate: {win_rates['p2']*100:.3f}%")
                self._log(f"Tie Rate: {win_rates['tie']*100:.3f}%")
                self._log(f"Avg Rounds: {self.sim_prob.average_rounds():.2f}")
                self._log(f"Avg Wars: {self.sim_prob.average_wars():.2f}")
                self._log(f"Avg Max Chain: {self.sim_prob.average_max_chain():.2f}")
                self._log(f"Shortest Game: {self.sim_replay.shortest.total_rounds}")
                self._log(f"Longest Game: {self.sim_replay.longest.total_rounds}")
                self._log(f"Most Wars: {self.sim_replay.most_wars.total_wars}")
                self._log(f"Longest War Chain: {self.sim_replay.longest_chain.max_chain}")
                self._log(f"Forced War Ends: {self.sim_forced_war_ends}")
                messagebox.showinfo("Simulation", "Simulation complete.")
                bias = self.sim_bias.rank_stats
                self._log("Deck Bias Analysis:")
                for rank, stats in bias.items():
                    win_rate = stats["wins"] / max(1, stats["wins"] + stats["losses"])
                    self._log(f"Rank {rank}: Win% {win_rate*100:.3f}, Cards Won {stats['cards_won']}")

                # --- Deck Bias Analysis Button ---
                bias_button = ttk.Button(
                    self,
                    text="Open Deck Bias Analysis",
                    command=lambda: BiasWindow(self, self.sim_bias.rank_stats)
                )
                bias_button.pack(pady=5)

                # Ask user which replay to open
                replay_log = self.choose_replay_dialog()
                if replay_log:
                    self.open_replay(replay_log)

                return

        # schedule next tick
        self.after(1, self._simulation_step)


    def _open_simulation_progress(self):
        win = tk.Toplevel(self)
        win.title("Simulation Running")
        win.geometry("350x150")

        ttk.Label(win, text="Running simulation...").pack(pady=10)

        self.sim_progress = ttk.Progressbar(win, length=300, mode="determinate")
        self.sim_progress.pack(pady=10)

        ttk.Button(win, text="Cancel", command=self._cancel_simulation).pack(pady=10)

        self.sim_window = win

    def _simulation_progress(self, current, total):
        percent = int((current / total) * 100)
        self.sim_progress["value"] = percent
        self.sim_window.update_idletasks()


    def _simulation_done(self, prob, replay, elapsed, cancelled):
        self.sim_window.destroy()

        if cancelled:
            messagebox.showinfo("Simulation", "Simulation cancelled.")
            return

        self.replay_engine = replay

        win_rates = prob.win_rates()
        self._log(f"Simulation complete in {elapsed:.2f}s")
        self._log(f"P1 Win Rate: {win_rates['p1']*100:.3f}%")
        self._log(f"P2 Win Rate: {win_rates['p2']*100:.3f}%")
        self._log(f"Tie Rate: {win_rates['tie']*100:.3f}%")
        self._log(f"Avg Rounds: {prob.average_rounds():.2f}")
        self._log(f"Avg Wars: {prob.average_wars():.2f}")
        self._log(f"Avg Max Chain: {prob.average_max_chain():.2f}")

        # Replay summary
        self._log(f"Shortest Game: {replay.shortest.total_rounds}")
        self._log(f"Longest Game: {replay.longest.total_rounds}")
        self._log(f"Most Wars: {replay.most_wars.total_wars}")
        self._log(f"Longest War Chain: {replay.longest_chain.max_chain}")

        messagebox.showinfo("Simulation", "Simulation complete.")

    def _cancel_simulation(self):
        self.sim_cancelled = True



    def _poll_simulation_queue(self):
        try:
            while True:
                msg = self.sim_queue.get_nowait()

                if msg[0] == "progress":
                    _, current, total = msg
                    percent = int((current / total) * 100)

                    if hasattr(self, "sim_progress") and self.sim_progress.winfo_exists():
                        self.sim_progress["value"] = percent

                elif msg[0] == "done":
                    _, prob, replay, elapsed, cancelled = msg

                    if hasattr(self, "sim_window") and self.sim_window.winfo_exists():
                        self.sim_window.destroy()

                    if cancelled:
                        messagebox.showinfo("Simulation", "Simulation cancelled.")
                        return

                    self.replay_engine = replay

                    win_rates = prob.win_rates()
                    self._log(f"Simulation complete in {elapsed:.2f}s")
                    self._log(f"P1 Win Rate: {win_rates['p1']*100:.3f}%")
                    self._log(f"P2 Win Rate: {win_rates['p2']*100:.3f}%")
                    self._log(f"Tie Rate: {win_rates['tie']*100:.3f}%")
                    self._log(f"Avg Rounds: {prob.average_rounds():.2f}")
                    self._log(f"Avg Wars: {prob.average_wars():.2f}")
                    self._log(f"Avg Max Chain: {prob.average_max_chain():.2f}")

                    self._log(f"Shortest Game: {replay.shortest.total_rounds}")
                    self._log(f"Longest Game: {replay.longest.total_rounds}")
                    self._log(f"Most Wars: {replay.most_wars.total_wars}")
                    self._log(f"Longest War Chain: {replay.longest_chain.max_chain}")

                    messagebox.showinfo("Simulation", "Simulation complete.")
                    return

        except queue.Empty:
            pass

        except Exception as e:
            print("ERROR IN POLLING LOOP:", e)

        # This MUST always run
        self.after(50, self._poll_simulation_queue)



    def toggle_stats_panel(self):
        if self.stats_frame.winfo_ismapped():
            self.stats_frame.pack_forget()
            self.stats_toggle_btn.config(text="Show Stats")
            self.prefs["stats_panel_visible"] = False
        else:
            self.stats_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
            self.stats_toggle_btn.config(text="Hide Stats")
            self.prefs["stats_panel_visible"] = True

        save_preferences(self.prefs)


    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)
        self.fullscreen_btn.config(text="Exit Full Screen" if self.fullscreen else "Full Screen")
        self.prefs["fullscreen"] = self.fullscreen
        save_preferences(self.prefs)

    def _restore_fullscreen(self):
        if self.prefs.get("fullscreen", False):
            self.attributes("-fullscreen", True)
            self.fullscreen = True
            self.fullscreen_btn.config(text="Exit Full Screen")




    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # ----- Settings -----
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)

        theme_menu.add_command(label="Modern Flat",
                            command=lambda: self.set_theme("modern"))
        theme_menu.add_command(label="Casino Dark",
                            command=lambda: self.set_theme("casino_dark"))
        theme_menu.add_command(label="Casino Light",
                            command=lambda: self.set_theme("casino_light"))

        # Other settings
        settings_menu.add_separator()
        settings_menu.add_command(label="Reset Session Stats",
                                command=self.reset_session_stats)
        settings_menu.add_separator()
        settings_menu.add_command(label="Toggle Full Screen",
                                command=self.toggle_fullscreen)
        
        # ----- Help -----
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_window)
        help_menu.add_command(
        label="Release Notes",
        command=lambda: ReleaseNotesWindow(self)
        )

        
    def set_theme(self, theme_name):
        # Save theme
        self.current_theme = theme_name
        self.prefs["theme"] = theme_name
        save_preferences(self.prefs)

        # Destroy old UI
        for widget in self.winfo_children():
            widget.destroy()

        # Apply theme BEFORE rebuilding UI
        apply_theme(self, theme_name)

        # Rebuild UI
        self._build_ui()
        self._build_menu()

        # Restore fullscreen if needed
        self.after(50, self._restore_fullscreen)

        self._log(f"Theme changed to: {theme_name.replace('_', ' ').title()}")



    def reset_session_stats(self):
        self.stats.reset_session()
        self._update_stats_labels()
        self._log("Session stats reset.")

    def show_about_window(self):
        about = tk.Toplevel(self)
        about.title("About War")
        about.geometry("350x250")
        about.configure(bg="#2b2b2b")

        ttk.Label(about, text="War - Card Game", font=("Segoe UI", 14, "bold")).pack(pady=10)
        ttk.Label(about, text="Created by SMJonesPB\nPowered by Python + Tkinter",
                font=("Segoe UI", 11)).pack(pady=5)

        ttk.Label(about, text="Features:",
                font=("Segoe UI", 11, "bold")).pack(pady=(15, 5))

        ttk.Label(about,
                text="- Auto-play mode\n"
                    "- Simulation engine\n"
                    "- Theme switcher\n"
                    "- Stats tracking\n"
                    "- Card image rendering\n"
                    "- Preferences saved automatically\n"
                    "- Replay viewer\n"
                    "- Deck bias analysis",
                justify="left").pack(pady=5)
        
        version_label = ttk.Label(
        about,
        text=f"Version {APP_VERSION}",
        font=("Segoe UI", 10)
        )
        version_label.pack(pady=(0, 10))

        ttk.Button(about, text="Close", command=about.destroy).pack(pady=15)

    def choose_replay_dialog(self):
        """
        Opens a small dialog asking which replay the user wants to view.
        Returns the chosen ReplayLog or None.
        """
        dialog = tk.Toplevel(self)
        dialog.title("Select Replay")
        dialog.geometry("300x250")
        dialog.grab_set()  # modal

        ttk.Label(dialog, text="Choose a replay to view:", font=("Segoe UI", 12)).pack(pady=10)

        choice_var = tk.StringVar(value="")

        # Radio buttons
        options = [
            ("Shortest Game", "shortest"),
            ("Longest Game", "longest"),
            ("Most Wars", "most_wars"),
            ("Longest War Chain", "longest_chain"),
        ]

        for text, value in options:
            ttk.Radiobutton(dialog, text=text, variable=choice_var, value=value).pack(anchor="w", padx=20)

        # Confirm button
        def confirm():
            dialog.destroy()

        ttk.Button(dialog, text="Open Replay", command=confirm).pack(pady=15)

        dialog.wait_window()  # wait for dialog to close

        choice = choice_var.get()
        if not choice:
            return None

        # Map choice to actual replay log
        return getattr(self.replay_engine, choice)
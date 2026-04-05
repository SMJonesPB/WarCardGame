import tkinter as tk
from tkinter import ttk

class BiasWindow(tk.Toplevel):
    def __init__(self, parent, bias_stats):
        super().__init__(parent)
        self.title("Deck Bias Analysis")
        self.geometry("600x500")
        self.bias_stats = bias_stats

        # --- Treeview Style Fix ---
        style = ttk.Style(self)
        style.configure("Bias.Treeview",
                        background="white",
                        foreground="black",
                        fieldbackground="white")
        style.configure("Bias.Treeview.Heading",
                        font=("Segoe UI", 10, "bold"))

        title = ttk.Label(self, text="Deck Bias Analysis", font=("Segoe UI", 16, "bold"))
        title.pack(pady=10)

        self._build_table()

    def _build_table(self):
        columns = ("rank", "wins", "losses", "cards_won", "cards_lost", "win_rate")

        tree = ttk.Treeview(self,
                            columns=columns,
                            show="headings",
                            height=20,
                            style="Bias.Treeview")   # <-- Apply style
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Column headings
        headings = {
            "rank": "Rank",
            "wins": "Wins",
            "losses": "Losses",
            "cards_won": "Cards Won",
            "cards_lost": "Cards Lost",
            "win_rate": "Win %"
        }

        for col in columns:
            tree.heading(col, text=headings[col],
                         command=lambda c=col: self._sort(tree, c, False))
            tree.column(col, anchor="center", width=90)

        # Insert rows
        for rank in range(2, 15):
            stats = self.bias_stats[rank]
            wins = stats["wins"]
            losses = stats["losses"]
            total = wins + losses
            win_rate = (wins / total) if total > 0 else 0

            tree.insert("", "end", values=(
                rank,
                wins,
                losses,
                stats["cards_won"],
                stats["cards_lost"],
                f"{win_rate:.3f}"
            ))

        self.tree = tree

    def _sort(self, tree, col, reverse):
        data = [(tree.set(k, col), k) for k in tree.get_children("")]

        # Numeric sort when possible
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)

        for index, (_, k) in enumerate(data):
            tree.move(k, "", index)

        tree.heading(col, command=lambda: self._sort(tree, col, not reverse))
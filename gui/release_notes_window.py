import tkinter as tk
from tkinter import ttk
import urllib.request
import ssl
from config import APP_VERSION, RELEASE_NOTES_URL

class ReleaseNotesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f"Release Notes – {APP_VERSION}")
        self.geometry("600x500")

        title = ttk.Label(self, text=f"Release Notes – {APP_VERSION}",
                          font=("Segoe UI", 16, "bold"))
        title.pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.text = tk.Text(frame, wrap="word", font=("Segoe UI", 10))
        self.text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=scrollbar.set)

        self._load_notes()

    def _load_notes(self):
        try:
            # GitHub requires SSL context
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(RELEASE_NOTES_URL, context=context) as f:
                content = f.read().decode("utf-8")
        except Exception as e:
            content = f"Failed to load release notes.\n\n{e}"

        self._insert_markdown(content)

    def _insert_markdown(self, md):
        for line in md.splitlines():
            if line.startswith("# "):
                self.text.insert("end", line[2:] + "\n", "h1")
            elif line.startswith("## "):
                self.text.insert("end", line[3:] + "\n", "h2")
            elif line.startswith("- "):
                self.text.insert("end", "• " + line[2:] + "\n")
            else:
                self.text.insert("end", line + "\n")

        # Simple formatting tags
        self.text.tag_config("h1", font=("Segoe UI", 14, "bold"))
        self.text.tag_config("h2", font=("Segoe UI", 12, "bold"))

        self.text.config(state="disabled")
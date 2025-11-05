import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import sys
import threading
import cv2

from templates.binary_choice import BinaryChoiceGame
from templates.numeric_input import NumericInputGame
from templates.puzzle import PuzzleGame


def on_enter(e, btn, color):
    btn['background'] = color
    btn['fg'] = "#ffffff"

def on_leave(e, btn, color, fgcolor):
    btn['background'] = color
    btn['fg'] = fgcolor

class GameLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎈 Kids Game Hub 🎈")
        
        start_w, start_h = 720, 800
        self.root.geometry(f"{start_w}x{start_h}")
        self.root.minsize(560, 520)
        self.root.resizable(True, True)

        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        ww, wh = map(int, self.root.geometry().split("+")[0].split("x"))
        x = (sw - ww) // 2
        y = (sh - wh) // 2
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")

        bg = "#FFF6D5"
        header_bg = "#FFE082"
        self.card_bg = "#FFFFFF"
        self.root.configure(bg=bg)

        self.app_stop_event = threading.Event()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        header = tk.Frame(self.root, bg=header_bg, padx=12, pady=14, highlightthickness=0, bd=0)
        title = tk.Label(header, text="🎮  Fun & Games!  🎲",
                         font=("Comic Sans MS", 28, "bold"), fg="#6A1B9A", bg=header_bg)
        subtitle = tk.Label(header, text="Tap a game to start! 😊",
                            font=("Comic Sans MS", 16, "bold"), fg="#0277BD", bg=header_bg)
        title.pack()
        subtitle.pack()
        header.grid(row=0, column=0, sticky="ew")

        self.create_widgets()

        exit_button = tk.Button(self.root, text="Exit", command=self.root.destroy, font=("Comic Sans MS", 16, "bold"), bg="#FF7043", fg="#FFFFFF", relief="flat", bd=0, highlightthickness=0, cursor="hand2")
        exit_button.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

    def create_widgets(self):
        card = tk.Frame(self.root, bg=self.card_bg, padx=16, pady=16, highlightthickness=0, bd=0)
        card.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 10))
        card.grid_columnconfigure(0, weight=1)

        games_dir = "created_games"
        if not os.path.exists(games_dir):
            ttk.Label(card, text="'created_games' directory not found.", font=("Helvetica", 12)).pack(pady=20)
            return

        game_files = []
        for game_name in sorted(os.listdir(games_dir)):
            game_dir = os.path.join(games_dir, game_name)
            if os.path.isdir(game_dir):
                game_file = os.path.join(game_dir, f"{game_name}.json")
                if os.path.exists(game_file):
                    game_files.append((game_name, game_file))

        if not game_files:
            ttk.Label(card, text="No games found.", font=("Helvetica", 12)).pack(pady=20)
            return

        BTN_FONT = ("Comic Sans MS", 20, "bold")
        BTN_HEIGHT = 2
        GAP_Y = 12

        row = 0
        for game_name, game_file in game_files:
            # Assign colors and emojis based on game name or a rotating scheme
            colors = [("#81D4FA", "#0288D1"), ("#A5D6A7", "#43A047"), ("#FFD54F", "#FFA000"), ("#FFAB91", "#FF7043")]
            base_color, hover_color = colors[row % len(colors)]
            emojis = ["🖐", "🥗", "🧩", "🍎"]
            emoji = emojis[row % len(emojis)]

            btn = tk.Button(
                card,
                text=f"{emoji}  {game_name}",
                font=BTN_FONT,
                height=BTN_HEIGHT,
                bg=base_color,
                fg="#1B2836",
                activebackground=hover_color,
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                command=lambda g=game_file: self.launch_game(g)
            )
            btn.grid(row=row, column=0, sticky="ew", padx=36, pady=GAP_Y)
            btn.bind("<Enter>", lambda e, b=btn, col=hover_color: on_enter(e, b, col))
            btn.bind("<Leave>", lambda e, b=btn, col=base_color, fgc="#1B2836": on_leave(e, b, col, fgc))
            row += 1

    def on_closing(self):
        self.app_stop_event.set()
        self.root.destroy()

    def launch_game(self, game_file):
        try:
            with open(game_file, 'r') as f:
                game_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            messagebox.showerror("Error", f"Failed to load game data: {e}")
            return

        template_name = game_data.get("template")
        game = None

        game_directory = os.path.dirname(game_file)

        if template_name == "Binary Choice":
            game = BinaryChoiceGame(game_data, game_directory, self.app_stop_event)
        elif template_name == "Numeric Input":
            game = NumericInputGame(game_data, game_directory, self.app_stop_event)
        elif template_name == "Puzzle":
            image_path = game_data.get("image_path")
            if not image_path or not os.path.exists(image_path):
                messagebox.showerror("Error", f"Puzzle image not found at: {image_path}")
                return
            
            img = cv2.imread(image_path)
            if img is None:
                messagebox.showerror("Error", f"Failed to load or decode puzzle image. Please check the file: {image_path}")
                return
            
            game = PuzzleGame(game_data, game_directory, self.app_stop_event)

        if game:
            self.root.withdraw()
            try:
                game.run()
            except Exception as e:
                messagebox.showerror("Game Error", f"An error occurred during the game: {e}")
            finally:
                self.root.deiconify()
        else:
            messagebox.showerror("Error", f"Unknown or missing game template: '{template_name}'")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncherApp(root)
    root.mainloop()
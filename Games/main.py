import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import sys
import threading
import cv2
from pathlib import Path

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
        
        # Get the absolute path to the Games directory
        self.script_dir = Path(__file__).parent.resolve()
        self.created_games_dir = self.script_dir / "created_games"
        
        start_w, start_h = 720, 800
        self.root.geometry(f"{start_w}x{start_h}")
        self.root.minsize(560, 520)
        self.root.resizable(True, True)

        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Center the window on screen
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        ww, wh = map(int, self.root.geometry().split("+")[0].split("x"))
        x = (sw - ww) // 2
        y = (sh - wh) // 2
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")
        
        # Force window to front and give it focus
        self.root.lift()
        self.root.focus_force()

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
        # Create a container frame for the card with scrollbar
        container = tk.Frame(self.root, bg="#FFF6D5")
        container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 10))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create canvas and scrollbar
        canvas = tk.Canvas(container, bg=self.card_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # Create the scrollable frame
        scrollable_frame = tk.Frame(canvas, bg=self.card_bg, padx=16, pady=16)
        
        # Configure canvas scrolling
        def _configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Center the scrollable frame in the canvas
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            x_position = max(0, (canvas_width - frame_width) // 2)
            canvas.coords(canvas_window, x_position, 0)
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Recenter when canvas is resized
        canvas.bind("<Configure>", _configure_scroll_region)
        
        # Pack canvas and scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        if not self.created_games_dir.exists():
            ttk.Label(scrollable_frame, text="'created_games' directory not found.", font=("Helvetica", 12)).pack(pady=20)
            return

        game_files = []
        for game_dir in sorted(self.created_games_dir.iterdir()):
            if game_dir.is_dir():
                game_name = game_dir.name
                game_file = game_dir / f"{game_name}.json"
                if game_file.exists():
                    game_files.append((game_name, str(game_file)))

        if not game_files:
            ttk.Label(scrollable_frame, text="No games found.", font=("Helvetica", 12)).pack(pady=20)
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
                scrollable_frame,
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
            btn.pack(fill="x", pady=GAP_Y, padx=36)
            btn.bind("<Enter>", lambda e, b=btn, col=hover_color: on_enter(e, b, col))
            btn.bind("<Leave>", lambda e, b=btn, col=base_color, fgc="#1B2836": on_leave(e, b, col, fgc))
            row += 1

    def on_closing(self):
        self.app_stop_event.set()
        self.root.destroy()

    def launch_game(self, game_file):
        try:
            print(f"[DEBUG] Loading game file: {game_file}")
            with open(game_file, 'r') as f:
                game_data = json.load(f)
            print(f"[DEBUG] Game data loaded: {game_data.get('title')}")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            error_msg = f"Failed to load game data: {e}"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror("Error", error_msg)
            return

        template_name = game_data.get("template")
        game = None

        # Use Path for proper path handling
        game_directory = str(Path(game_file).parent)
        print(f"[DEBUG] Game directory: {game_directory}")
        print(f"[DEBUG] Template: {template_name}")

        if template_name == "Binary Choice":
            try:
                game = BinaryChoiceGame(game_data, game_directory, self.app_stop_event)
            except Exception as e:
                import traceback
                error_msg = f"Failed to initialize Binary Choice game: {e}\n{traceback.format_exc()}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Error", str(e))
                return
        elif template_name == "Numeric Input":
            try:
                game = NumericInputGame(game_data, game_directory, self.app_stop_event)
            except Exception as e:
                import traceback
                error_msg = f"Failed to initialize Numeric Input game: {e}\n{traceback.format_exc()}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Error", str(e))
                return
        elif template_name == "Puzzle":
            # Handle both absolute and relative paths
            image_path = game_data.get("image_path")
            if not os.path.isabs(image_path):
                image_path = os.path.join(game_directory, image_path)
            
            print(f"[DEBUG] Puzzle image path: {image_path}")
            print(f"[DEBUG] Puzzle image exists: {os.path.exists(image_path)}")
                
            if not image_path or not os.path.exists(image_path):
                error_msg = f"Puzzle image not found at: {image_path}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Error", error_msg)
                return
            
            img = cv2.imread(image_path)
            if img is None:
                error_msg = f"Failed to load or decode puzzle image. Please check the file: {image_path}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Error", error_msg)
                return
            
            try:
                game = PuzzleGame(game_data, game_directory, self.app_stop_event)
            except Exception as e:
                import traceback
                error_msg = f"Failed to initialize Puzzle game: {e}\n{traceback.format_exc()}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Error", str(e))
                return

        if game:
            self.root.withdraw()
            try:
                print(f"[DEBUG] Starting game...")
                game.run()
                print(f"[DEBUG] Game ended normally")
            except Exception as e:
                import traceback
                error_msg = f"An error occurred during the game: {e}\n{traceback.format_exc()}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Game Error", str(e))
            finally:
                self.root.deiconify()
        else:
            error_msg = f"Unknown or missing game template: '{template_name}'"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncherApp(root)
    root.mainloop()
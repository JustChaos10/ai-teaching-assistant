import threading
import tkinter as tk
from tkinter import messagebox

# ---------- GAME LAUNCH HELPERS ----------

def launch_game(game_function, menu_win):
    """Hide menu, run the game, then restore the menu when it exits."""
    try:
        menu_win.attributes("-topmost", False)
    except Exception:
        pass
    menu_win.withdraw()

    def game_wrapper():
        try:
            # Let the next window take focus
            game_function()
        except Exception:
            try:
                messagebox.showerror("Oops!", "Something went wrong starting the game.")
            except Exception:
                pass
        finally:
            try:
                menu_win.after(0, lambda: (menu_win.deiconify(), menu_win.lift(), menu_win.focus_force()))
            except Exception:
                pass

    threading.Thread(target=game_wrapper, daemon=True).start()

# Import inside launcher functions so the menu loads even if a game is missing
def launch_finger_counting_game():
    from finger_counting_game import runner_finger_counting_game
    runner_finger_counting_game()

def launch_healthy_vs_junk():
    from healthyVSjunk import run_healthy_vs_junk_food_game
    run_healthy_vs_junk_food_game()

def launch_picture_puzzle():
    # Your puzzle script must provide main()
    from puzzle import main as puzzle_main
    puzzle_main()

def launch_fruits_vegetables():
    from fruits_vs_vegetables import main as fruits_main
    fruits_main()

# ---------- HOVER EFFECTS ----------
def on_enter(e, btn, color):
    btn['background'] = color
    btn['fg'] = "#ffffff"

def on_leave(e, btn, color, fgcolor):
    btn['background'] = color
    btn['fg'] = fgcolor

# ---------- MAIN MENU ----------
def open_menu():
    root = tk.Tk()
    root.title("🎈 Kids Game Hub 🎈")

    # Start size; resizable; centered
    start_w, start_h = 720, 800
    root.geometry(f"{start_w}x{start_h}")
    root.minsize(560, 520)
    root.resizable(True, True)

    # Center window
    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    ww, wh = map(int, root.geometry().split("+")[0].split("x"))
    x = (sw - ww) // 2
    y = (sh - wh) // 2
    root.geometry(f"{ww}x{wh}+{x}+{y}")

    # Colors
    bg = "#FFF6D5"        # warm pale yellow
    header_bg = "#FFE082" # soft amber
    card_bg = "#FFFFFF"
    root.configure(bg=bg)

    # Grid weights: header fixed, content grows
    root.grid_rowconfigure(0, weight=0)  # header
    root.grid_rowconfigure(1, weight=1)  # card/content
    root.grid_rowconfigure(2, weight=0)  # spacer
    root.grid_rowconfigure(3, weight=0)  # exit
    root.grid_columnconfigure(0, weight=1)

    # Header
    header = tk.Frame(root, bg=header_bg, padx=12, pady=14, highlightthickness=0, bd=0)
    title = tk.Label(header, text="🎮  Fun & Games!  🎲",
                     font=("Comic Sans MS", 28, "bold"), fg="#6A1B9A", bg=header_bg)
    subtitle = tk.Label(header, text="Tap a game to start! 😊",
                        font=("Comic Sans MS", 16, "bold"), fg="#0277BD", bg=header_bg)
    title.pack()
    subtitle.pack()
    header.grid(row=0, column=0, sticky="ew")

    # Card container (content area)
    card = tk.Frame(root, bg=card_bg, padx=16, pady=16, highlightthickness=0, bd=0)
    card.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 10))
    card.grid_columnconfigure(0, weight=1)  # buttons stretch full width

    # Uniform button style (ensures equal sizes)
    BTN_FONT = ("Comic Sans MS", 20, "bold")
    BTN_HEIGHT = 2  # lines of text
    GAP_Y = 12

    def make_game_button(parent, label, emoji, command, base, hover, fg):
        btn = tk.Button(
            parent,
            text=f"{emoji}  {label}",
            font=BTN_FONT,
            height=BTN_HEIGHT,
            bg=base,
            fg=fg,
            activebackground=hover,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=command
        )
        # Full width; equal spacing
        btn.grid(row=make_game_button.row, column=0, sticky="ew", padx=36, pady=GAP_Y)
        make_game_button.row += 1
        btn.bind("<Enter>", lambda e, b=btn, col=hover: on_enter(e, b, col))
        btn.bind("<Leave>", lambda e, b=btn, col=base, fgc=fg: on_leave(e, b, col, fgc))
        return btn
    make_game_button.row = 0

    # Buttons (same width via sticky='ew' + grid column weight)
    make_game_button(card, "Finger Counting", "🖐",
                     lambda: launch_game(launch_finger_counting_game, root),
                     base="#81D4FA", hover="#0288D1", fg="#1B2836")

    make_game_button(card, "Healthy vs Junk", "🥗",
                     lambda: launch_game(launch_healthy_vs_junk, root),
                     base="#A5D6A7", hover="#43A047", fg="#1B2836")

    make_game_button(card, "Picture Puzzle", "🧩",
                     lambda: launch_game(launch_picture_puzzle, root),
                     base="#FFD54F", hover="#FFA000", fg="#3E2723")

    make_game_button(card, "Fruits vs Vegetables", "🍎",
                     lambda: launch_game(launch_fruits_vegetables, root),
                     base="#FFAB91", hover="#FF7043", fg="#3E2723")

    # Spacer row to keep exit off the card
    spacer = tk.Frame(root, bg=bg, height=4, highlightthickness=0, bd=0)
    spacer.grid(row=2, column=0, sticky="ew")

    # Exit button
    exit_btn = tk.Button(
        root, text="🚪  Exit", font=("Comic Sans MS", 18, "bold"),
        bg="#F06292", fg="#ffffff", activebackground="#AD1457", activeforeground="#ffffff",
        command=root.destroy, bd=0, relief="flat", cursor="hand2"
    )
    exit_btn.grid(row=3, column=0, pady=14)
    exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg="#AD1457"))
    exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg="#F06292"))

    root.mainloop()

if __name__ == "__main__":
    open_menu()

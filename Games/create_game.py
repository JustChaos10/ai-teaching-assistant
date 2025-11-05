
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import shutil

class GameCreationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Creator & Manager")
        self.root.geometry("700x600")

        self.template_var = tk.StringVar()
        self.game_name_var = tk.StringVar()
        self.image_paths = []
        self.music_path = None
        self.music_filename_var = tk.StringVar()
        self.answers = {}
        self.games_to_delete = {}

        self.create_widgets()
        self.refresh_game_list()

    def create_widgets(self):
        # Main paned window
        main_pane = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Creator Frame ---
        creator_frame = ttk.LabelFrame(main_pane, text="Create New Game", padding="10")
        main_pane.add(creator_frame, weight=1)
        self.setup_creator_widgets(creator_frame)

        # --- Manager Frame ---
        manager_frame = ttk.LabelFrame(main_pane, text="Manage Existing Games", padding="10")
        main_pane.add(manager_frame, weight=1)
        self.setup_manager_widgets(manager_frame)

    def setup_creator_widgets(self, parent_frame):
        parent_frame.columnconfigure(1, weight=1)

        ttk.Label(parent_frame, text="Select Game Template:").grid(row=0, column=0, sticky=tk.W, pady=5)
        template_options = ["Binary Choice", "Numeric Input", "Puzzle"]
        self.template_dropdown = ttk.Combobox(parent_frame, textvariable=self.template_var, values=template_options, state="readonly")
        self.template_dropdown.grid(row=0, column=1, sticky=tk.EW, pady=5)
        self.template_dropdown.bind("<<ComboboxSelected>>", self.on_template_select)

        ttk.Label(parent_frame, text="Game Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.game_name_entry = ttk.Entry(parent_frame, textvariable=self.game_name_var)
        self.game_name_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)

        self.add_images_button = ttk.Button(parent_frame, text="Add Images", command=self.add_images)
        self.add_images_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.add_music_button = ttk.Button(parent_frame, text="Add Music", command=self.add_music)
        self.add_music_button.grid(row=3, column=0, pady=5)

        self.music_label = ttk.Label(parent_frame, textvariable=self.music_filename_var)
        self.music_label.grid(row=3, column=1, sticky=tk.W, pady=5)

        self.options_frame = ttk.Frame(parent_frame)
        self.options_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW)

        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        self.save_and_new_button = ttk.Button(buttons_frame, text="Save and Create Another", command=self.save_and_new)
        self.save_and_new_button.grid(row=0, column=0, padx=5, sticky=tk.EW)

        self.save_and_exit_button = ttk.Button(buttons_frame, text="Save and Exit", command=self.save_and_exit)
        self.save_and_exit_button.grid(row=0, column=1, padx=5, sticky=tk.EW)

    def setup_manager_widgets(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)

        self.game_list_frame = ttk.Frame(parent_frame)
        self.game_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        delete_button = ttk.Button(parent_frame, text="Delete Selected Games", command=self.delete_selected_games)
        delete_button.pack(pady=10)

    def refresh_game_list(self):
        for widget in self.game_list_frame.winfo_children():
            widget.destroy()

        games_dir = "created_games"
        if not os.path.exists(games_dir):
            ttk.Label(self.game_list_frame, text="'created_games' directory not found.").pack()
            return

        game_names = sorted([d for d in os.listdir(games_dir) if os.path.isdir(os.path.join(games_dir, d))])
        if not game_names:
            ttk.Label(self.game_list_frame, text="No games found.").pack()
            return

        self.games_to_delete = {}
        for game_name in game_names:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.game_list_frame, text=game_name, variable=var)
            cb.pack(anchor=tk.W, padx=10)
            self.games_to_delete[game_name] = var

    def delete_selected_games(self):
        selected_games = [game for game, var in self.games_to_delete.items() if var.get()]
        if not selected_games:
            messagebox.showinfo("Info", "No games selected for deletion.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the following games?\n\n- {'\n- '.join(selected_games)}")
        if not confirm:
            return

        try:
            for game_name in selected_games:
                game_dir = os.path.join("created_games", game_name)
                shutil.rmtree(game_dir)
            messagebox.showinfo("Success", "Selected games have been deleted.")
            self.refresh_game_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete games: {e}")

    def on_template_select(self, event):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        template = self.template_var.get()
        if not self.image_paths: return
        if template == "Binary Choice": self.create_binary_choice_options()
        elif template == "Numeric Input": self.create_numeric_input_options()
        elif template == "Puzzle": self.create_puzzle_options()

    def add_images(self):
        files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*.jpg *.png")])
        if files:
            self.image_paths.extend(files)
            self.on_template_select(None)

    def add_music(self):
        file = filedialog.askopenfilename(title="Select Music", filetypes=[("WAV Files", "*.wav")])
        if file:
            self.music_path = file
            self.music_filename_var.set(os.path.basename(file))

    def create_binary_choice_options(self):
        ttk.Label(self.options_frame, text="Set Answers:").pack(pady=5)
        for path in self.image_paths:
            frame = ttk.Frame(self.options_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=os.path.basename(path)).pack(side=tk.LEFT, padx=5)
            answer_var = tk.StringVar(value="yes")
            ttk.Radiobutton(frame, text="Yes", variable=answer_var, value="yes").pack(side=tk.RIGHT)
            ttk.Radiobutton(frame, text="No", variable=answer_var, value="no").pack(side=tk.RIGHT)
            self.answers[path] = answer_var

    def create_numeric_input_options(self):
        ttk.Label(self.options_frame, text="Set Answers:").pack(pady=5)
        for path in self.image_paths:
            frame = ttk.Frame(self.options_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=os.path.basename(path)).pack(side=tk.LEFT, padx=5)
            answer_var = tk.IntVar(value=1)
            ttk.Spinbox(frame, from_=1, to=5, textvariable=answer_var, width=5).pack(side=tk.RIGHT)
            self.answers[path] = answer_var

    def create_puzzle_options(self):
        ttk.Label(self.options_frame, text="Puzzle Settings:").pack(pady=5)
        frame = ttk.Frame(self.options_frame)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text="Number of Rows:").pack(side=tk.LEFT, padx=5)
        rows_var = tk.IntVar(value=4)
        ttk.Spinbox(frame, from_=2, to=10, textvariable=rows_var, width=5).pack(side=tk.RIGHT)
        self.answers['rows'] = rows_var

    def save_game(self):
        game_name = self.game_name_var.get()
        template = self.template_var.get()
        if not game_name or not template or not self.image_paths:
            messagebox.showerror("Error", "Please fill in all fields and add images.")
            return False
        try:
            game_dir = os.path.join("created_games", game_name)
            os.makedirs(game_dir, exist_ok=True)
            game_data = {"title": game_name, "template": template, "items": []}
            if template in ["Binary Choice", "Numeric Input"]:
                for path in self.image_paths:
                    new_path = os.path.join(game_dir, os.path.basename(path))
                    shutil.copy(path, new_path)
                    game_data["items"].append({"image_path": new_path, "question": "What is this?", "answer": self.answers[path].get()})
            elif template == "Puzzle":
                path = self.image_paths[0]
                new_path = os.path.join(game_dir, os.path.basename(path))
                shutil.copy(path, new_path)
                game_data["image_path"] = new_path
                game_data["rows"] = self.answers['rows'].get()

            if self.music_path:
                music_filename = os.path.basename(self.music_path)
                new_music_path = os.path.join(game_dir, music_filename)
                shutil.copy(self.music_path, new_music_path)
                game_data["bg_music"] = music_filename
            json_path = os.path.join(game_dir, f"{game_name}.json")
            with open(json_path, 'w') as f:
                json.dump(game_data, f, indent=4)
            messagebox.showinfo("Success", f"Game '{game_name}' created successfully!")
            self.refresh_game_list()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create game: {e}")
            return False

    def clear_form(self):
        self.game_name_var.set("")
        self.template_var.set("")
        self.image_paths = []
        self.music_path = None
        self.music_filename_var.set("")
        self.answers = {}
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def save_and_new(self):
        if self.save_game():
            self.clear_form()

    def save_and_exit(self):
        if self.save_game():
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameCreationApp(root)
    root.mainloop()

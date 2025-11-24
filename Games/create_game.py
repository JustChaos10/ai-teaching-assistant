
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import shutil
from pathlib import Path
import sys
from datetime import datetime

class GameCreationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Creator & Manager")
        self.root.geometry("700x600")

        # Get the absolute path to the Games directory
        self.script_dir = Path(__file__).parent.resolve()
        self.created_games_dir = self.script_dir / "created_games"
        
        # Create a log file for debugging
        self.log_file = self.script_dir / "game_creator_debug.log"
        self.log(f"=== Game Creator Started at {datetime.now()} ===")
        self.log(f"Script directory: {self.script_dir}")
        self.log(f"Created games directory: {self.created_games_dir}")
        self.log(f"Current working directory: {os.getcwd()}")
        
        # Ensure created_games directory exists
        self.created_games_dir.mkdir(exist_ok=True)
        self.log(f"Created games directory exists: {self.created_games_dir.exists()}")

        self.template_var = tk.StringVar()
        self.game_name_var = tk.StringVar()
        self.image_paths = []
        self.music_path = None
        self.music_filename_var = tk.StringVar()
        self.answers = {}
        self.games_to_delete = {}

        self.create_widgets()
        self.refresh_game_list()
    
    def log(self, message):
        """Write debug messages to log file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except Exception as e:
            print(f"Failed to write to log: {e}")

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

        if not self.created_games_dir.exists():
            ttk.Label(self.game_list_frame, text="'created_games' directory not found.").pack()
            return

        game_names = sorted([d.name for d in self.created_games_dir.iterdir() if d.is_dir()])
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

        games_list = '\n- '.join(selected_games)
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the following games?\n\n- {games_list}")
        if not confirm:
            return

        try:
            for game_name in selected_games:
                game_dir = self.created_games_dir / game_name
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
        
        self.log(f"\n=== Attempting to save game ===")
        self.log(f"Game name: {game_name}")
        self.log(f"Template: {template}")
        self.log(f"Number of images: {len(self.image_paths)}")
        
        if not game_name or not template or not self.image_paths:
            messagebox.showerror("Error", "Please fill in all fields and add images.")
            self.log("ERROR: Missing required fields")
            return False
        try:
            game_dir = self.created_games_dir / game_name
            self.log(f"Target game directory: {game_dir}")
            
            game_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"Game directory created/verified: {game_dir.exists()}")
            
            game_data = {"title": game_name, "template": template, "items": []}
            if template in ["Binary Choice", "Numeric Input"]:
                for idx, path in enumerate(self.image_paths):
                    image_filename = os.path.basename(path)
                    new_path = game_dir / image_filename
                    
                    self.log(f"Copying image {idx + 1}/{len(self.image_paths)}")
                    self.log(f"  Source: {path}")
                    self.log(f"  Source exists: {os.path.exists(path)}")
                    self.log(f"  Destination: {new_path}")
                    
                    shutil.copy(str(path), str(new_path))
                    
                    self.log(f"  Copy successful: {new_path.exists()}")
                    
                    # Store only the filename, not the full path
                    game_data["items"].append({
                        "image_path": image_filename, 
                        "question": "What is this?", 
                        "answer": self.answers[path].get()
                    })
            elif template == "Puzzle":
                path = self.image_paths[0]
                image_filename = os.path.basename(path)
                new_path = game_dir / image_filename
                
                self.log(f"Copying puzzle image")
                self.log(f"  Source: {path}")
                self.log(f"  Source exists: {os.path.exists(path)}")
                self.log(f"  Destination: {new_path}")
                
                shutil.copy(str(path), str(new_path))
                self.log(f"  Copy successful: {new_path.exists()}")
                
                # Store only the filename, not the full path
                game_data["image_path"] = image_filename
                game_data["rows"] = self.answers['rows'].get()

            if self.music_path:
                music_filename = os.path.basename(self.music_path)
                new_music_path = game_dir / music_filename
                self.log(f"Copying music: {self.music_path} -> {new_music_path}")
                shutil.copy(str(self.music_path), str(new_music_path))
                game_data["bg_music"] = music_filename
                
            json_path = game_dir / f"{game_name}.json"
            self.log(f"Writing JSON to: {json_path}")
            
            with open(json_path, 'w') as f:
                json.dump(game_data, f, indent=4)
            
            self.log(f"Game created successfully!")
            self.log(f"JSON content: {json.dumps(game_data, indent=2)}")
            
            messagebox.showinfo("Success", f"Game '{game_name}' created successfully!")
            self.refresh_game_list()
            return True
        except Exception as e:
            import traceback
            error_msg = f"Failed to create game: {e}\n{traceback.format_exc()}"
            self.log(f"ERROR: {error_msg}")
            messagebox.showerror("Error", f"Failed to create game: {e}")
            return False
            messagebox.showinfo("Success", f"Game '{game_name}' created successfully!")
            self.refresh_game_list()
            return True
        except Exception as e:
            import traceback
            error_msg = f"Failed to create game: {e}\n\n{traceback.format_exc()}"
            print(error_msg)  # Print to console for debugging
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

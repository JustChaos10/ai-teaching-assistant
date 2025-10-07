import os
import sys
import subprocess
import threading
from typing import Optional, Dict, Any

class GameManager:
    """
    Unified game manager to handle launching and integration of all image detector games
    with the main teaching assistant application.
    """
    
    def __init__(self):
        self.image_detector_path = "image detector"
        self.available_games = {
            "finger_counting": {
                "script": "finger_counting_game.py",
                "function": "runner_finger_counting_game",
                "name": "Finger Counting Game",
                "description": "Count fingers and learn numbers"
            },
            "healthy_food": {
                "script": "healthyVSjunk.py", 
                "function": "run_healthy_vs_junk_food_game",
                "name": "Healthy vs Junk Food",
                "description": "Learn about healthy eating habits"
            },
            "puzzle": {
                "script": "puzzle.py",
                "function": "main",
                "name": "Picture Puzzle",
                "description": "Solve picture puzzles"
            },
            "game_menu": {
                "script": "main_ui.py",
                "function": "open_menu", 
                "name": "Games Menu",
                "description": "Access all games from a central menu"
            },
            "fruits_vegetables": {
                "script": "fruits_vs_vegetables.py",
                "function": "main",
                "name": "Fruits vs Vegetables",
                "description": "Learn to classify fruits and vegetables using placards"
            }
        }
    
    def list_available_games(self) -> Dict[str, Dict[str, str]]:
        """Return a dictionary of available games and their information."""
        return self.available_games
    
    def is_game_available(self, game_name: str) -> bool:
        """Check if a specific game is available and its script exists."""
        if game_name not in self.available_games:
            return False
        
        script_path = os.path.join(self.image_detector_path, self.available_games[game_name]["script"])
        return os.path.exists(script_path)
    
    def launch_game_subprocess(self, game_name: str) -> bool:
        """
        Launch a game as a separate subprocess.
        Returns True if launch was successful, False otherwise.
        """
        if not self.is_game_available(game_name):
            print(f"Game '{game_name}' is not available")
            return False

        game_info = self.available_games[game_name]

        try:
            print(f"Launching {game_info['name']}...")

            # Get absolute paths
            original_cwd = os.getcwd()
            image_detector_abs_path = os.path.abspath(self.image_detector_path)
            script_abs_path = os.path.join(image_detector_abs_path, game_info["script"])

            print(f"[DEBUG] Original CWD: {original_cwd}")
            print(f"[DEBUG] Image detector path: {image_detector_abs_path}")
            print(f"[DEBUG] Script path: {script_abs_path}")
            print(f"[DEBUG] Script exists: {os.path.exists(script_abs_path)}")

            # Verify script exists
            if not os.path.exists(script_abs_path):
                print(f"Error: Script not found at {script_abs_path}")
                return False

            # Use the same Python executable that's running the main app
            python_exe = sys.executable
            print(f"[DEBUG] Using Python executable: {python_exe}")

            # Launch the game as a subprocess with absolute paths
            process = subprocess.Popen([
                python_exe, script_abs_path
            ], cwd=image_detector_abs_path, shell=False,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)

            print(f"Successfully launched {game_info['name']} (PID: {process.pid})")
            return True

        except Exception as e:
            print(f"Error launching {game_info['name']}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def launch_game_threaded(self, game_name: str) -> bool:
        """
        Launch a game in a separate thread to avoid blocking the main application.
        Returns True if thread creation was successful, False otherwise.
        """
        if not self.is_game_available(game_name):
            print(f"Game '{game_name}' is not available")
            return False
        
        def game_thread():
            self.launch_game_subprocess(game_name)
        
        try:
            thread = threading.Thread(target=game_thread, daemon=True)
            thread.start()
            return True
        except Exception as e:
            print(f"Error creating thread for {game_name}: {e}")
            return False
    
    def launch_game_inline(self, game_name: str) -> Optional[Any]:
        """
        Import and run a game function directly (inline).
        This method is more integrated but may cause GUI conflicts.
        Returns the result of the game function or None if failed.
        """
        if not self.is_game_available(game_name):
            print(f"Game '{game_name}' is not available")
            return None
        
        game_info = self.available_games[game_name]
        
        try:
            # Add the image detector path to sys.path temporarily
            original_path = sys.path.copy()
            sys.path.insert(0, os.path.abspath(self.image_detector_path))
            
            # Import the module and get the function
            module_name = game_info["script"].replace(".py", "")
            module = __import__(module_name)
            game_function = getattr(module, game_info["function"])
            
            # Run the game function
            result = game_function()
            
            # Restore original sys.path
            sys.path = original_path
            
            return result
            
        except Exception as e:
            print(f"Error running {game_info['name']} inline: {e}")
            # Restore original sys.path on error
            sys.path = original_path
            return None
    
    def launch_game(self, game_name: str, method: str = "subprocess") -> bool:
        """
        Launch a game using the specified method.
        
        Args:
            game_name: Name of the game to launch
            method: Launch method - "subprocess", "threaded", or "inline"
        
        Returns:
            True if launch was successful, False otherwise
        """
        if method == "subprocess":
            return self.launch_game_subprocess(game_name)
        elif method == "threaded":
            return self.launch_game_threaded(game_name)
        elif method == "inline":
            result = self.launch_game_inline(game_name)
            return result is not None
        else:
            print(f"Unknown launch method: {method}")
            return False
    
    def get_game_description(self, game_name: str) -> str:
        """Get a description of the specified game."""
        if game_name in self.available_games:
            return self.available_games[game_name]["description"]
        return f"Unknown game: {game_name}"
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if all required dependencies for the games are available.
        Returns a dictionary of dependency names and their availability status.
        """
        dependencies = {
            "cv2": False,
            "numpy": False,
            "mediapipe": False,
            "pygame": False,
            "tkinter": False
        }
        
        for dep in dependencies:
            try:
                __import__(dep)
                dependencies[dep] = True
            except ImportError:
                pass
        
        return dependencies
    
    def get_status_report(self) -> str:
        """Generate a status report of game availability and dependencies."""
        report = ["=== Game Manager Status Report ===\n"]
        
        # Check dependencies
        deps = self.check_dependencies()
        report.append("Dependencies:")
        for dep, available in deps.items():
            status = "[OK]" if available else "[MISSING]"
            report.append(f"  {status} {dep}")

        report.append("\nAvailable Games:")
        for game_name, game_info in self.available_games.items():
            available = self.is_game_available(game_name)
            status = "[READY]" if available else "[NOT FOUND]"
            report.append(f"  {status} {game_info['name']} ({game_name})")
            if available:
                report.append(f"      {game_info['description']}")
        
        return "\n".join(report)

# Convenience function for backward compatibility
def launch_game(game_name: str, method: str = "subprocess") -> bool:
    """Convenience function to launch a game using the GameManager."""
    manager = GameManager()
    return manager.launch_game(game_name, method)

if __name__ == "__main__":
    # Test the GameManager
    manager = GameManager()
    print(manager.get_status_report())
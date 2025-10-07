import os
import sys
import subprocess
import re
import inflect

# Backend imports
parent_dir_of_repo = "./backend"
sys.path.insert(0, os.path.abspath(parent_dir_of_repo))
from backend.rag_system import RAGSystem
from backend.free_speech_services import FreeTTSService

# Import the game manager and teaching prompts
from game_manager import GameManager
from teaching_prompts import (
    get_teaching_prompt, 
    format_teaching_response, 
    detect_subject, 
    should_suggest_game
)
from module_executor import ModuleExecutor

# This class encapsulates all the backend logic from your original script.
class ChatbotLogic:
    def __init__(self):
        print("Initializing Chatbot Logic...")
        # ----------------- SETUP -----------------
        self.p = inflect.engine()
        self.rag = RAGSystem()
        auto_ingest_docs(self.rag)
        
        # Initialize game manager and module executor
        self.game_manager = GameManager()
        self.module_executor = ModuleExecutor(self)

        # ----------------- TTS SETUP -----------------
        print("Initializing FREE TTS Service...")
        try:
            self.tts_service = FreeTTSService()
            print("FREE TTS Service initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize FREE TTS service: {e}")
            self.tts_service = None

        print("Chatbot Logic Initialized Successfully.")

    def get_response(self, text: str) -> str:
        """
        Queries the RAG system to get a teaching-focused response.
        Enhanced with subject detection, game suggestions, and custom teaching modules.
        """
        # First, check if this is a game launch command
        game_response = self._handle_game_commands(text)
        if game_response:
            return game_response

        # Check if this is related to a custom teaching module
        module_response, module_handled = self.module_executor.handle_module_request(text)
        if module_handled:
            return module_response

        # Detect the subject area
        detected_subject = detect_subject(text)

        # Check if we should suggest a game
        should_game, game_name = should_suggest_game(text, detected_subject)

        # Get teaching-focused prompt
        teaching_prompt = get_teaching_prompt(detected_subject, context=f"Child asked: {text}")

        # Get base response from RAG system
        base_response = self.rag.query(text)

        # Format response with teaching enhancements
        enhanced_response = format_teaching_response(
            base_response,
            include_encouragement=True,
            suggest_activity=should_game
        )

        # Add game suggestion if appropriate
        if should_game and game_name:
            if game_name == 'finger_counting':
                enhanced_response += "\n\nWould you like to play a finger counting game? I can help you practice counting with your fingers! Just say 'launch finger game' and we can start!"
            elif game_name == 'healthy_food':
                enhanced_response += "\n\nI have a fun healthy eating game! We can learn about nutritious foods together. Say 'start healthy game' to begin!"
            elif game_name == 'puzzle':
                enhanced_response += "\n\nHow about we solve some picture puzzles together? Say 'open puzzle game' to start the fun!"
            elif game_name == 'game_menu':
                enhanced_response += "\n\nI have lots of educational games we can play! Say 'show games' to see all the fun activities available!"

        # Check if we have custom modules that might be relevant
        if len(enhanced_response.strip()) < 100:  # If response is short, suggest custom modules
            matching_module = self.module_executor.find_module_by_topic(text)
            if matching_module:
                enhanced_response += f"\n\nI also have a special learning activity about '{matching_module.title}' that might interest you! Would you like to try it?"

        return enhanced_response

    def _handle_game_commands(self, text: str) -> str:
        """
        Check if the input text contains game launch commands and launch games accordingly.

        Args:
            text: User input text

        Returns:
            Response string if game command detected, None otherwise
        """
        text_lower = text.lower()

        # Define game launch patterns
        game_patterns = {
            'finger_counting': [
                'launch finger game', 'start finger game', 'finger counting game',
                'finger count', 'counting game', 'finger game'
            ],
            'healthy_food': [
                'start healthy game', 'healthy eating game', 'food game',
                'healthy vs junk', 'nutrition game', 'healthy food game'
            ],
            'puzzle': [
                'open puzzle game', 'puzzle game', 'picture puzzle',
                'solve puzzle', 'start puzzle'
            ],
            'game_menu': [
                'show games', 'game menu', 'see games', 'all games',
                'available games', 'what games', 'games list'
            ],
            'fruits_vegetables': [
                'fruits and vegetables', 'fruit vegetable game',
                'fruits vs vegetables', 'fruit game', 'vegetable game'
            ]
        }

        # Check for game launch commands
        for game_name, patterns in game_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    print(f"Game command detected: {pattern} -> {game_name}")
                    success = self.launch_game(game_name)

                    if success:
                        return f"Great! I'm launching the {self.game_manager.available_games[game_name]['name']} for you! Have fun learning!"
                    else:
                        return f"I'm sorry, I couldn't start the {game_name} game right now. Let me try to help you in another way!"

        # Check for general game requests
        general_game_words = ['play game', 'start game', 'game please', 'let\'s play']
        if any(phrase in text_lower for phrase in general_game_words):
            return ("I have several fun educational games we can play! Try saying:\n"
                   "• 'launch finger game' for counting practice\n"
                   "• 'start healthy game' for nutrition learning\n"
                   "• 'open puzzle game' for picture puzzles\n"
                   "• 'show games' to see the full menu\n"
                   "Which one sounds fun to you?")

        return None  # No game command detected

    def generate_tts(self, text: str, output_path="output.wav") -> str:
        """
        Generates TTS audio from text and SAVES it to a file using online service.
        CRITICAL CHANGE: This function NO LONGER plays the audio.
        It just creates the file and returns the path.
        """
        try:
            if not self.tts_service:
                print("[WARNING] TTS service not available.")
                return ""

            safe_text = self._clean_text(text)
            result_path = self.tts_service.generate_speech(safe_text, output_path)

            if result_path:
                print(f"[TTS] Audio generated successfully: {result_path}")
                return result_path
            else:
                print("[WARNING] Failed to generate audio")
                return ""

        except Exception as e:
            print(f"[TTS] Error: {str(e)}")
            return ""

    def launch_game(self, game_name: str, method: str = "subprocess"):
        """
        Launches a game using the GameManager.
        
        Args:
            game_name: Name of the game to launch (finger_counting, healthy_food, puzzle, game_menu)
            method: Launch method - "subprocess" (default), "threaded", or "inline"
        """
        # Map common game name variations to standard names
        game_mapping = {
            "finger": "finger_counting",
            "counting": "finger_counting", 
            "fingers": "finger_counting",
            "healthy": "healthy_food",
            "food": "healthy_food",
            "junk": "healthy_food",
            "healthy_vs_junk": "healthy_food",
            "puzzle": "puzzle",
            "menu": "game_menu",
            "games": "game_menu",
            "game_menu": "game_menu"
        }
        
        # Normalize the game name
        normalized_name = game_mapping.get(game_name.lower(), game_name.lower())
        
        # Launch the game
        success = self.game_manager.launch_game(normalized_name, method)
        
        if success:
            game_info = self.game_manager.available_games.get(normalized_name, {})
            print(f"Successfully launched {game_info.get('name', normalized_name)}")
        else:
            print(f"Failed to launch game: {game_name}")
            # Provide helpful information about available games
            available = list(self.game_manager.available_games.keys())
            print(f"Available games: {', '.join(available)}")
        
        return success
    
    def get_available_games(self):
        """Return information about available games."""
        return self.game_manager.list_available_games()
    
    def get_game_status(self):
        """Get a status report of all games and dependencies."""
        return self.game_manager.get_status_report()


    def _clean_text(self, text: str) -> str:
        """
        Private helper method for cleaning text.
        (Copied directly from your clean_text function)
        """
        # --- All your text cleaning logic from teacher_chatbot.py goes here ---
        # (I've omitted the full code for brevity, but you should copy it here)
        SYMBOL_MAP = {'+': 'plus', '-': 'minus', '*': 'times', '/': 'divided by', '=': 'equals', '%': 'percent', '>': 'greater than', '<': 'less than', '&': 'and', '@': 'at', '#': 'number', '$': 'dollar', '^': 'caret', '√': 'square root'}
        for symbol, word in SYMBOL_MAP.items():
            text = text.replace(symbol, f' {word} ')
        def replace_digits(match):
            num = int(match.group(0))
            return self.p.number_to_words(num)
        text = re.sub(r'\b\d+\b', replace_digits, text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if not text or len(text.strip()) < 3:
            return "Let's try again with a different question!"
        return text

# Helper function also moved from the original script
def auto_ingest_docs(rag, docs_folder="./docs"):
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
        return
    supported_exts = {".pdf", ".docx", ".pptx", ".txt"}
    files = [f for f in os.listdir(docs_folder) if os.path.isfile(os.path.join(docs_folder, f))]
    for file_name in files:
        ext = os.path.splitext(file_name)[1].lower()
        if ext in supported_exts:
            file_path = os.path.join(docs_folder, file_name)
            try:
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                rag.ingest_file(file_name, file_bytes)
            except Exception as e:
                print(f"Failed to ingest {file_name}: {e}")
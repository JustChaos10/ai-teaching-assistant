import cv2
import os
import random
from .base_game import BaseGame
from detector import ColorDetector

class BinaryChoiceGame(BaseGame):
    def __init__(self, game_data, game_directory, app_stop_event=None):
        super().__init__(game_data, game_directory, app_stop_event, window_name=game_data.get('title', 'Binary Choice Game'))
        self.items = game_data.get('items', [])
        self.item_queue = []
        self.current_item = None
        self.input_processor = ColorDetector()

    def load_game_assets(self):
        for item in self.items:
            # Handle both absolute and relative paths
            image_path = item['image_path']
            
            # Check if it's an old-style path that includes "created_games"
            if 'created_games' in image_path and not os.path.isabs(image_path):
                # Extract just the filename from old-style relative paths
                image_path = os.path.basename(image_path)
            
            # If still not absolute, join with game directory
            if not os.path.isabs(image_path):
                image_path = os.path.join(self.game_directory, image_path)
            
            # Check if image exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Load the image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            item['image_obj'] = img

    def prepare_new_round(self):
        super().prepare_new_round()
        if not self.item_queue:
            random.shuffle(self.items)
            self.item_queue = self.items.copy()
        self.current_item = self.item_queue.pop(0)

    def is_round_ready(self) -> bool:
        return self.current_item is not None

    def get_current_item(self):
        return self.current_item

    def get_item_image(self, item):
        return item.get('image_obj')

    def get_question_text(self, item) -> str:
        return item.get('question', 'Is it healthy?')

    def check_answer(self, item, answer) -> bool:
        return answer.lower() == item['answer'].lower()

    def get_feedback_text(self, item, correct) -> str:
        return "Correct!" if correct else f"Wrong! The answer is {item['answer']}"
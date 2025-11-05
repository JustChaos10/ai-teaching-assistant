import cv2
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
            item['image_obj'] = cv2.imread(item['image_path'])

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
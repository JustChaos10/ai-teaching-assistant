import cv2
import random
import numpy as np
import pygame
from .base_game import BaseGame
from utils.image_processing import make_bg, cv_color, BG, GOOD, ACCENT, ACCENT_DARK, PANEL, PANEL_SHADOW, TEXT, put_center_text, PANEL_BORDER, draw_panel

class Button:
    def __init__(self, rect, label, callback):
        self.rect = rect
        self.label = label
        self.callback = callback
        self.hover = False

    def draw(self, frame):
        x, y, w, h = self.rect
        base_color = ACCENT if self.hover else PANEL
        txt_color = PANEL if self.hover else ACCENT_DARK
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), cv_color(base_color), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), cv_color(ACCENT_DARK), 2)
        put_center_text(frame, self.label, (x + w // 2, y + h // 2), 0.8, txt_color, thickness=2)

    def handle_click(self, pos):
        x, y, w, h = self.rect
        if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
            self.callback()
            return True
        return False

class PuzzleGame(BaseGame):
    def __init__(self, game_data, game_directory, app_stop_event=None):
        super().__init__(game_data, game_directory, app_stop_event, window_name=game_data.get('title', 'Puzzle Game'), has_camera=False, scale_factor=0.75, width_to_height_ratio=1.5)
        self.image_path = game_data.get('image_path')
        self.rows = game_data.get('rows', 4)
        self.strips = []
        self.order = []
        self.selected_pos = None
        self.show_numbers = True
        self.badge_w = 60
        
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        btn_h = 40
        btn_w = 120
        spacing = 10
        y = self.win_height - 60

        # Left-aligned buttons
        self.buttons.append(Button((20, y, btn_w, btn_h), "Shuffle", self.shuffle_puzzle))
        
        difficulties = {"Easy": 4, "Medium": 6, "Hard": 8}
        x = 20 + btn_w + spacing
        for name, rows in difficulties.items():
            self.buttons.append(Button((x, y, 100, btn_h), name, lambda r=rows: self.set_difficulty(r)))
            x += 100 + spacing
            
        self.buttons.append(Button((x, y, 150, btn_h), "Numbers: On", self.toggle_numbers))

        # Right-aligned buttons
        x_right = self.win_width - btn_w - 20
        self.buttons.append(Button((x_right, y, btn_w, btn_h), "Exit", self.exit_game))

        x_right -= (btn_w + spacing)
        mute_label = "Unmute" if self.audio_muted else "Mute"
        self.buttons.append(Button((x_right, y, btn_w, btn_h), mute_label, self.toggle_mute))

    def shuffle_puzzle(self):
        random.shuffle(self.order)
        self.selected_pos = None

    def set_difficulty(self, rows):
        self.rows = rows
        self.prepare_new_round()

    def toggle_numbers(self):
        self.show_numbers = not self.show_numbers
        for btn in self.buttons:
            if "Numbers" in btn.label:
                btn.label = f"Numbers: {'On' if self.show_numbers else 'Off'}"

    def exit_game(self):
        self.running = False

    def toggle_mute(self):
        self.audio_muted = not self.audio_muted
        self._set_music_paused(self.audio_muted)
        for btn in self.buttons:
            if "Mute" in btn.label or "Unmute" in btn.label:
                btn.label = "Unmute" if self.audio_muted else "Mute"

    def load_game_assets(self):
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            raise FileNotFoundError(f"Image not found at {self.image_path}")

    def prepare_new_round(self):
        self.strips = []
        self.order = []
        
        h, w, _ = self.image.shape
        
        puzzle_area_w = self.game_area_w - 100
        puzzle_area_h = self.win_height - 100

        image_w = puzzle_area_w
        if self.show_numbers:
            image_w -= self.badge_w

        scale_w = image_w / w
        scale_h = puzzle_area_h / h
        scale = min(scale_w, scale_h)

        new_w = int(w * scale)
        new_h = int(h * scale)
        resized_image = cv2.resize(self.image, (new_w, new_h))

        h, w, _ = resized_image.shape

        h = (h // self.rows) * self.rows
        resized_image = resized_image[:h, :]

        strip_h = h // self.rows
        for i in range(self.rows):
            y = i * strip_h
            strip = resized_image[y:y + strip_h, :]
            self.strips.append(strip)
        self.order = list(range(self.rows))
        random.shuffle(self.order)

    def is_round_ready(self) -> bool:
        return bool(self.strips)

    def get_current_item(self):
        return self.strips

    def get_item_image(self, item):
        return None

    def get_question_text(self, item) -> str:
        return "Click two strips to swap them."

    def get_user_input(self):
        return None

    def check_answer(self, item, answer) -> bool:
        return self.order == list(range(self.rows))

    def run(self):
        self._init_pygame()
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self._on_mouse)

        self.load_game_assets()
        self.prepare_new_round()

        while self.running:
            if self.app_stop_event and self.app_stop_event.is_set():
                self.running = False

            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                self.running = False

            if not self.running:
                continue

            if self.check_answer(None, None):
                self.score = self.points_to_win
                break

            frame = self._draw_puzzle_state()
            
            draw_panel(frame, self.bottombar_rect, PANEL, PANEL_BORDER, shadow=True)
            
            for btn in self.buttons:
                btn.hover = btn.rect[0] <= self.mouse_pos[0] <= btn.rect[0] + btn.rect[2] and \
                            btn.rect[1] <= self.mouse_pos[1] <= btn.rect[1] + btn.rect[3]
                btn.draw(frame)

            cv2.imshow(self.window_name, frame)

            if self.mouse_clicked:
                self.mouse_clicked = False
                clicked_on_button = False
                for btn in self.buttons:
                    if btn.handle_click(self.mouse_pos):
                        clicked_on_button = True
                        break
                if not clicked_on_button:
                    self._handle_puzzle_click()

            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                self.running = False

        self._display_end_screen()
        pygame.mixer.quit()
        cv2.destroyAllWindows()

    def _draw_puzzle_state(self):
        frame = make_bg(self.win_height, self.win_width, BG)

        if not self.strips: return frame

        strip_h, strip_w, _ = self.strips[0].shape
        
        puzzle_area_w = strip_w
        if self.show_numbers:
            puzzle_area_w += self.badge_w
            
        puzzle_area_h = self.rows * (strip_h + 5) - 5
        x_start_puzzle = (self.game_area_w - puzzle_area_w) // 2
        y_start_puzzle = (self.win_height - puzzle_area_h - 80) // 2 # Center puzzle vertically

        cv2.rectangle(frame, (x_start_puzzle - 5, y_start_puzzle - 5), 
                      (x_start_puzzle + puzzle_area_w + 5, y_start_puzzle + puzzle_area_h + 5),
                      cv_color(PANEL_SHADOW), -1)
        cv2.rectangle(frame, (x_start_puzzle - 2, y_start_puzzle - 2), 
                      (x_start_puzzle + puzzle_area_w + 2, y_start_puzzle + puzzle_area_h + 2),
                      cv_color(PANEL_BORDER), -1)

        for i, idx in enumerate(self.order):
            y = y_start_puzzle + i * (strip_h + 5)
            x = x_start_puzzle
            
            if self.show_numbers:
                badge_x = x
                cv2.rectangle(frame, (badge_x, y), (badge_x + self.badge_w, y + strip_h), cv_color((255, 247, 215)), -1)
                cv2.rectangle(frame, (badge_x, y), (badge_x + self.badge_w, y + strip_h), cv_color((210, 190, 150)), 2)
                put_center_text(frame, str(idx + 1), (badge_x + self.badge_w // 2, y + strip_h // 2), 1.0, (80, 55, 0), thickness=2)
                x += self.badge_w

            frame[y:y + strip_h, x:x + strip_w] = self.strips[idx]
            
            if self.selected_pos == i:
                cv2.rectangle(frame, (x_start_puzzle, y), (x_start_puzzle + puzzle_area_w, y + strip_h), cv_color(GOOD), 4)
        return frame

    def _handle_puzzle_click(self):
        if not self.strips: return

        strip_h, strip_w, _ = self.strips[0].shape
        puzzle_area_w = strip_w
        if self.show_numbers:
            puzzle_area_w += self.badge_w
        puzzle_area_h = self.rows * (strip_h + 5) - 5
        x_start_puzzle = (self.game_area_w - puzzle_area_w) // 2
        y_start_puzzle = (self.win_height - puzzle_area_h - 80) // 2

        mx, my = self.mouse_pos
        if not (x_start_puzzle < mx < x_start_puzzle + puzzle_area_w):
            return

        for i in range(self.rows):
            y = y_start_puzzle + i * (strip_h + 5)
            if y < my < y + strip_h:
                if self.selected_pos is None:
                    self.selected_pos = i
                else:
                    self.order[self.selected_pos], self.order[i] = self.order[i], self.order[self.selected_pos]
                    self.selected_pos = None
                break

import cv2
import pygame
import time
import os
import random
import threading
import tkinter as tk
from tkinter import messagebox
from abc import ABC, abstractmethod
from utils.image_processing import (
    make_bg, draw_panel, put_center_text, draw_image_in_panel, 
    draw_tick_or_cross_over_image, cv_color, BG, BG_DARK, PANEL, PANEL_BORDER, 
    PANEL_SHADOW, TEXT, TEXT_SUB, GOOD, BAD, ACCENT, ACCENT_DARK, GRAY,
    MARGIN, TOPBAR_H, BOTTOMBAR_H, SHADOW_OFFSET
)

class ConfettiParticle:
    def __init__(self, x, y, w_max, h_max):
        self.x = x
        self.y = y
        self.w_max = w_max
        self.h_max = h_max
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-8, -2)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.size = random.randint(5, 10)
        self.gravity = 0.2

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def draw(self, img):
        if self.y < self.h_max and self.x > 0 and self.x < self.w_max:
            cv2.circle(img, (int(self.x), int(self.y)), self.size, cv_color(self.color), -1)

class BaseGame(ABC):
    def __init__(self, game_data, game_directory, app_stop_event=None, window_name="Game", scale_factor=0.8, has_camera=True, width_to_height_ratio=1.0):
        self.game_data = game_data
        self.game_directory = game_directory
        self.app_stop_event = app_stop_event
        self.input_processor = None
        self.window_name = window_name
        self.scale_factor = scale_factor
        self.has_camera = has_camera
        self.width_to_height_ratio = width_to_height_ratio

        self.score = 0
        self.total_wrong = 0
        self.points_to_win = game_data.get('points_to_win', 5)
        self.max_total_wrong = game_data.get('max_total_wrong', 3)

        self.audio_muted = False
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.running = True

        self.round_timer_duration = 15
        self.round_start_time = None
        self.timed_out = False

        self.screen_w, self.screen_h = self._get_screen_dimensions()
        self.win_height = int(self.screen_h * self.scale_factor)
        
        self.sidebar_width = 320 if self.has_camera else 0
        self.win_width = int(self.win_height * self.width_to_height_ratio) + self.sidebar_width

        self._setup_layouts()

    def _get_screen_dimensions(self):
        root = tk.Tk()
        root.withdraw()
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.destroy()
        return w, h

    def _setup_layouts(self):
        self.game_area_w = self.win_width - self.sidebar_width
        game_area_w = self.game_area_w

        # Main game area rects
        self.topbar_rect = (12, 10, game_area_w - 24, TOPBAR_H - 16)
        self.content_rect = (MARGIN, TOPBAR_H + MARGIN, game_area_w - 2 * MARGIN, self.win_height - TOPBAR_H - BOTTOMBAR_H - 2 * MARGIN)
        self.bottombar_rect = (0, self.win_height - BOTTOMBAR_H, self.win_width, BOTTOMBAR_H)

        content_x, content_y, content_w, content_h = self.content_rect
        caption_h = int(max(80, 0.2 * content_h))
        self.image_panel_rect = (content_x + 16, content_y + 16, content_w - 32, content_h - caption_h - 24)
        self.caption_panel_rect = (content_x + 16, content_y + content_h - caption_h, content_w - 32, caption_h - 8)

        if self.has_camera:
            sidebar_x = game_area_w
            self.sidebar_rect = (sidebar_x, 0, self.sidebar_width, self.win_height)
            
            cam_h = self.sidebar_width * 9 // 16 # 16:9 aspect ratio
            self.cam_feed_rect = (sidebar_x + 15, 20, self.sidebar_width - 30, cam_h)

            timer_y = self.cam_feed_rect[1] + self.cam_feed_rect[3] + 20
            self.timer_rect = (sidebar_x + 15, timer_y, self.sidebar_width - 30, 105)

            score_bar_y = self.timer_rect[1] + self.timer_rect[3] + 20
            self.score_bar_rect = (sidebar_x + 15, score_bar_y, self.sidebar_width - 30, 50)

            mute_btn_y = self.score_bar_rect[1] + self.score_bar_rect[3] + 20
            self.mute_btn_rect = (sidebar_x + 15, mute_btn_y, self.sidebar_width - 30, 60)

            self.exit_btn_rect = (sidebar_x + 15, self.win_height - BOTTOMBAR_H + 10, self.sidebar_width - 30, 60)

    def _init_pygame(self):
        pygame.mixer.init()
        self.sounds = self._load_sounds()
        self._try_play_music(0.35)

    def _load_sounds(self):
        sounds = {}
        sounds_dir = os.path.join(os.path.dirname(__file__), '..', 'sounds')
        sound_files = {
            'correct': 'correct.wav',
            'wrong': 'wrong.wav',
            'win': 'win.wav',
            'lose': 'lose.wav',
        }
        for name, filename in sound_files.items():
            path = os.path.join(sounds_dir, filename)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                sounds[name] = pygame.mixer.Sound(path)

        # Load background music
        bg_music_path = None
        bg_music_filename = self.game_data.get('bg_music')
        if bg_music_filename:
            path = os.path.join(self.game_directory, bg_music_filename)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                bg_music_path = path
        else:
            # Load a default background music
            path = os.path.join(sounds_dir, 'bg_music_food.wav')
            if os.path.exists(path) and os.path.getsize(path) > 0:
                bg_music_path = path
        
        if bg_music_path:
            try:
                pygame.mixer.music.load(bg_music_path)
            except pygame.error as e:
                print(f"Could not load background music: {e}")

        return sounds

    def _try_play_music(self, vol=0.35):
        try:
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Could not play music: {e}")

    def _set_music_paused(self, paused: bool):
        try:
            if paused:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Error in _set_music_paused: {e}")

    def _on_mouse(self, event, x, y, flags, userdata):
        self.mouse_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_clicked = True

    def _draw_score_bar(self, img):
        x, y, w, h = self.score_bar_rect
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(PANEL_SHADOW), -1)
        fill_w = max(0, min(w, int(w * (self.score / max(1, self.points_to_win)))))
        if fill_w > 0:
            cv2.rectangle(img, (x, y), (x + fill_w, y + h), cv_color(GOOD), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(PANEL_BORDER), 3)
        label = f"Score: {self.score} / {self.points_to_win}"
        put_center_text(img, label, (x + w // 2, y + h // 2 + 4), 0.95, TEXT, thickness=2)

    def _draw_strikes_bottom(self, img):
        radius = max(18, int(self.win_height * 0.025))
        pad = max(26, int(self.win_width * 0.018))
        y = self.win_height - BOTTOMBAR_H // 2 + 6
        game_area_w = self.win_width - self.sidebar_width
        total_w = self.max_total_wrong * (2 * radius) + (self.max_total_wrong - 1) * pad
        x_start = (game_area_w - total_w) // 2 + radius
        for i in range(self.max_total_wrong):
            cx = x_start + i * (2 * radius + pad)
            cy = y
            cv2.circle(img, (cx, cy), radius, cv_color(GRAY), 3)
            if i < self.total_wrong:
                off = int(radius * 0.7)
                cv2.line(img, (cx - off, cy - off), (cx + off, cy + off), cv_color(BAD), 5)
                cv2.line(img, (cx + off, cy - off), (cx - off, cy + off), cv_color(BAD), 5)

    def _draw_button(self, img, rect, label, hover=False):
        x, y, w, h = rect
        base_color = ACCENT if hover else PANEL
        txt_color = PANEL if hover else ACCENT_DARK
        cv2.rectangle(img, (x + 3, y + 3), (x + w + 3, y + h + 3), cv_color(PANEL_SHADOW), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(base_color), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(ACCENT_DARK), 2)
        put_center_text(img, label, (x + w // 2, y + h // 2 + 4), 0.9, txt_color, thickness=2)

    def _point_in_rect(self, pt, rect):
        x, y = pt
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def _draw_caption(self, img, text):
        x, y, w, h = self.caption_panel_rect
        draw_panel(img, (x, y, w, h), PANEL, PANEL_BORDER, 2, shadow=True)
        scale = max(1.0, w / 800)
        put_center_text(img, f"{text}", (x + w // 2, y + h // 2 + 8), scale, TEXT, thickness=4)

    def run(self):
        self._init_pygame()
        cv2.namedWindow(self.window_name)
        x = (self.screen_w - self.win_width) // 2
        y = (self.screen_h - self.win_height) // 2
        cv2.moveWindow(self.window_name, x, y)
        cv2.setMouseCallback(self.window_name, self._on_mouse)

        cap = None
        if self.input_processor:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                # Handle camera not found
                pass # Or display a message on the main window

        self.load_game_assets()
        self.prepare_new_round()

        while self.running:
            if self.app_stop_event and self.app_stop_event.is_set():
                self.running = False

            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                self.running = False

            if not self.running:
                continue

            if self.score >= self.points_to_win or self.total_wrong >= self.max_total_wrong:
                break

            if not self.is_round_ready():
                self.prepare_new_round()

            current_item = self.get_current_item()
            
            # --- Drawing Start ---
            frame = make_bg(self.win_height, self.win_width, BG)
            if self.has_camera:
                cv2.rectangle(frame, self.sidebar_rect, cv_color(BG), -1)
                game_area_w = self.win_width - self.sidebar_width
                cv2.line(frame, (game_area_w, 0), (game_area_w, self.win_height), cv_color(PANEL_BORDER), 2)

            # Draw main game area elements
            draw_image_in_panel(frame, self.get_item_image(current_item), self.image_panel_rect)
            draw_panel(frame, self.bottombar_rect, PANEL, PANEL_BORDER, 2, shadow=True)
            self._draw_strikes_bottom(frame)
            self._draw_caption(frame, self.get_question_text(current_item))

            # Draw sidebar elements
            if self.has_camera:
                self._draw_score_bar(frame)
                hover_mute = self._point_in_rect(self.mouse_pos, self.mute_btn_rect)
                self._draw_button(frame, self.mute_btn_rect, "Unmute" if self.audio_muted else "Mute", hover=hover_mute)
                hover_exit = self._point_in_rect(self.mouse_pos, self.exit_btn_rect)
                self._draw_button(frame, self.exit_btn_rect, "Exit", hover=hover_exit)

            # --- Timer Logic ---
            if self.round_start_time:
                elapsed_round_time = time.time() - self.round_start_time
                remaining_time = self.round_timer_duration - elapsed_round_time

                if remaining_time <= 0:
                    self.timed_out = True
                    self.running = False
                    continue

                # Draw timer
                if self.has_camera: # Only draw timer if there is a sidebar
                    draw_panel(frame, self.timer_rect, PANEL, PANEL_BORDER, 2, shadow=False)
                    time_header_text = "Time"
                    put_center_text(frame, time_header_text, (self.timer_rect[0] + self.timer_rect[2] // 2, self.timer_rect[1] + 25), 0.9, TEXT_SUB, thickness=2)
                    timer_text = f"{int(remaining_time)}"
                    put_center_text(frame, timer_text, (self.timer_rect[0] + self.timer_rect[2] // 2, self.timer_rect[1] + self.timer_rect[3] // 2 + 20), 2.5, TEXT, thickness=5)

            # Handle camera and input
            user_answer = None
            if self.has_camera and cap and self.input_processor:
                ret, cam_frame = cap.read()
                if ret:
                    cam_frame = cv2.flip(cam_frame, 1)
                    user_answer = self.input_processor.process_frame(cam_frame)

                    # Draw camera feed in the sidebar
                    resized_cam = cv2.resize(cam_frame, (self.cam_feed_rect[2], self.cam_feed_rect[3]))
                    frame[self.cam_feed_rect[1]:self.cam_feed_rect[1] + self.cam_feed_rect[3], self.cam_feed_rect[0]:self.cam_feed_rect[0] + self.cam_feed_rect[2]] = resized_cam
            # --- Drawing End ---

            if self.mouse_clicked:
                self.mouse_clicked = False
                if hover_mute:
                    self.audio_muted = not self.audio_muted
                    self._set_music_paused(self.audio_muted)
                elif hover_exit:
                    self.running = False

            if user_answer is not None:
                correct = self.check_answer(current_item, user_answer)

                if correct:
                    self.score += 1
                    if self.sounds.get('correct') and not self.audio_muted: self.sounds['correct'].play()
                else:
                    self.total_wrong += 1
                    if self.sounds.get('wrong') and not self.audio_muted: self.sounds['wrong'].play()

                feedback_frame = frame.copy()
                self._draw_caption(feedback_frame, self.get_feedback_text(current_item, correct))
                draw_tick_or_cross_over_image(feedback_frame, self.image_panel_rect, correct)
                cv2.imshow(self.window_name, feedback_frame)
                cv2.waitKey(1200)

                if self.input_processor:
                    self.input_processor.reset()
                self.prepare_new_round()

            cv2.imshow(self.window_name, frame)

            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                self.running = False

        if self.timed_out:
            timeout_msg_frame = make_bg(300, 600, BG_DARK)
            put_center_text(timeout_msg_frame, "No input detected", (300, 150), 1.2, (255, 255, 255), thickness=3)
            cv2.imshow(self.window_name, timeout_msg_frame)
            cv2.waitKey(5000)

        if cap:
            cap.release()
        self._display_end_screen()
        pygame.mixer.quit()
        cv2.destroyAllWindows()

    def _display_end_screen(self):
        if not self.running: return

        pygame.mixer.music.stop()
        won = self.score >= self.points_to_win
        bg_color = BG if won else BG_DARK
        msg = "YOU WIN!" if won else "Game Over"
        msg_color = GOOD if won else BAD

        if won:
            if self.sounds.get('win') and not self.audio_muted: self.sounds['win'].play()
            confetti = [ConfettiParticle(random.randint(0, self.win_width), random.randint(-self.win_height, 0), self.win_width, self.win_height) for _ in range(150)]
        else:
            if self.sounds.get('lose') and not self.audio_muted: self.sounds['lose'].play()

        start_time = time.time()
        while time.time() - start_time < 5.0:
            end_frame = make_bg(self.win_height, self.win_width, bg_color)
            
            if won:
                center_panel_rect = (MARGIN, TOPBAR_H + MARGIN, self.win_width - 2 * MARGIN, self.win_height - TOPBAR_H - BOTTOMBAR_H - 2 * MARGIN)
                draw_panel(end_frame, center_panel_rect, PANEL, PANEL_BORDER, 2, shadow=True)
            
            put_center_text(end_frame, msg, (self.win_width // 2, self.win_height // 2 - 16), 2.0, msg_color, thickness=4, font=cv2.FONT_HERSHEY_TRIPLEX)
            put_center_text(end_frame, f"Exiting in {5 - int(time.time() - start_time)}...", (self.win_width // 2, self.win_height - BOTTOMBAR_H // 2 + 8), 0.95, TEXT_SUB, thickness=2)

            if won:
                for p in confetti:
                    p.update()
                    p.draw(end_frame)

            cv2.imshow(self.window_name, end_frame)
            if cv2.waitKey(15) & 0xFF == 27:
                break

    # ----- Abstract methods for subclasses to implement -----
    @abstractmethod
    def load_game_assets(self):
        pass

    def prepare_new_round(self):
        self.round_start_time = time.time()

    @abstractmethod
    def is_round_ready(self) -> bool:
        pass

    @abstractmethod
    def get_current_item(self):
        pass

    @abstractmethod
    def get_item_image(self, item):
        pass

    @abstractmethod
    def get_question_text(self, item) -> str:
        return ""

    @abstractmethod
    def check_answer(self, item, answer) -> bool:
        return False

    def get_feedback_text(self, item, correct) -> str:
        return "Correct!" if correct else "Wrong!"

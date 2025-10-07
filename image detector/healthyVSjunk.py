def run_healthy_vs_junk_food_game():
    import cv2
    import numpy as np
    import random
    import os
    import tkinter as tk
    import pygame
    import time
    import detector

    # ---------- STYLE / CONSTANTS (from Finger Counting Game) ----------
    MARGIN = 16
    TOPBAR_H = 60
    BOTTOMBAR_H = 80
    SHADOW_OFFSET = 8

    # Colors (RGB)
    BG = (248, 250, 255)
    BG_DARK = (40, 45, 60)
    PANEL = (255, 255, 255)
    PANEL_BORDER = (190, 205, 255)
    PANEL_SHADOW = (220, 228, 255)

    TEXT = (40, 50, 70)
    TEXT_SUB = (90, 105, 140)
    GOOD = (0, 180, 120)
    BAD = (210, 60, 80)
    ACCENT = (90, 130, 255)
    ACCENT_DARK = (60, 100, 230)
    GRAY = (120, 120, 120)

    # --- Game Configuration ---
    POINTS_TO_WIN = 5
    MAX_WRONGS = 3
    WINDOW_NAME = "Healthy vs. Junk Food Game"
    SCALE_FACTOR = 0.65

    # --- Asset Paths ---
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    if not os.path.exists("images"):
        os.makedirs("images")

    SOUNDS_DIR = "sounds"
    SOUND_CORRECT_PATH = os.path.join(SOUNDS_DIR, "correct.wav")
    SOUND_WRONG_PATH = os.path.join(SOUNDS_DIR, "wrong.wav")
    SOUND_WIN_PATH = os.path.join(SOUNDS_DIR, "win.wav")
    SOUND_LOSE_PATH = os.path.join(SOUNDS_DIR, "lose.wav")
    SOUND_BG_PATH = os.path.join(SOUNDS_DIR, "bg_music_food.wav") # Different music file

    for p in [SOUND_CORRECT_PATH, SOUND_WRONG_PATH, SOUND_WIN_PATH, SOUND_LOSE_PATH, SOUND_BG_PATH]:
        if not os.path.exists(p): open(p, 'a').close()

    FOOD_ITEMS = [
        {"name": "Apple", "type": "healthy", "image": os.path.join("images", "apple.jpg")},
        {"name": "Broccoli", "type": "healthy", "image": os.path.join("images", "broccoli.jpg")},
        {"name": "Carrot", "type": "healthy", "image": os.path.join("images", "carrot.jpg")},
        {"name": "Pizza", "type": "junk", "image": os.path.join("images", "pizza.jpg")},
        {"name": "Burger", "type": "junk", "image": os.path.join("images", "burger.jpg")},
        {"name": "Donut", "type": "junk", "image": os.path.join("images", "donut.jpg")},
    ]

    for item in FOOD_ITEMS:
        if not os.path.exists(item["image"]):
            img = np.full((200, 200, 3), (200, 200, 200), dtype=np.uint8)
            cv2.putText(img, item["name"], (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
            cv2.imwrite(item["image"], img)

    # ---------- INIT: audio ----------
    pygame.mixer.init()
    SOUND_CORRECT = pygame.mixer.Sound(SOUND_CORRECT_PATH) if os.path.exists(SOUND_CORRECT_PATH) and os.path.getsize(SOUND_CORRECT_PATH) > 0 else None
    SOUND_WRONG = pygame.mixer.Sound(SOUND_WRONG_PATH) if os.path.exists(SOUND_WRONG_PATH) and os.path.getsize(SOUND_WRONG_PATH) > 0 else None
    SOUND_WIN = pygame.mixer.Sound(SOUND_WIN_PATH) if os.path.exists(SOUND_WIN_PATH) and os.path.getsize(SOUND_WIN_PATH) > 0 else None
    SOUND_LOSE = pygame.mixer.Sound(SOUND_LOSE_PATH) if os.path.exists(SOUND_LOSE_PATH) and os.path.getsize(SOUND_LOSE_PATH) > 0 else None

    audio_muted = False

    def try_play_music(path, vol=0.35):
        try:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(vol)
                pygame.mixer.music.play(-1)
                return True
        except Exception as e:
            print(f"Could not play music: {e}")
        return False

    def set_music_paused(paused: bool):
        try:
            if paused:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
        except Exception:
            pass

    try_play_music(SOUND_BG_PATH, 0.35)

    # ---------- Screen size ----------
    def get_screen_dimensions():
        root = tk.Tk()
        root.withdraw()
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.destroy()
        return w, h

    screen_width, screen_height = get_screen_dimensions()
    win_width = int(screen_width * SCALE_FACTOR*0.6)
    win_height = int(screen_height * SCALE_FACTOR)

    # ---------- Confetti Class for Win Screen ----------
    class ConfettiParticle:
        def __init__(self, x, y, w_max, h_max):
            self.x, self.y, self.w_max, self.h_max = x, y, w_max, h_max
            self.vx, self.vy = random.uniform(-2, 2), random.uniform(-8, -2)
            self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            self.size, self.gravity = random.randint(5, 10), 0.2
        def update(self):
            self.vy += self.gravity; self.x += self.vx; self.y += self.vy
        def draw(self, img):
            if self.y < self.h_max and self.x > 0 and self.x < self.w_max:
                cv2.circle(img, (int(self.x), int(self.y)), self.size, cv_color(self.color), -1)

    # ---------- OpenCV UI helpers ----------
    def cv_color(rgb): return (rgb[2], rgb[1], rgb[0])
    def make_bg(h, w, rgb):
        frame = np.zeros((h, w, 3), dtype=np.uint8); frame[:, :] = np.array(cv_color(rgb), dtype=np.uint8)[None, None, :]; return frame
    def draw_panel(img, rect, fill, border, border_th=2, shadow=True):
        x, y, w, h = rect
        if shadow: cv2.rectangle(img, (x + SHADOW_OFFSET, y + SHADOW_OFFSET), (x + w + SHADOW_OFFSET, y + h + SHADOW_OFFSET), cv_color(PANEL_SHADOW), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(fill), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(border), border_th)
    def put_center_text(img, text, center_xy, font_scale, color, thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX):
        size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        x = int(center_xy[0] - size[0] / 2); y = int(center_xy[1] + size[1] / 2)
        cv2.putText(img, text, (x, y), font, font_scale, cv_color(color), thickness, cv2.LINE_AA)

    # ---------- Layout elements ----------
    topbar_rect = (MARGIN, MARGIN, win_width - 2 * MARGIN, TOPBAR_H)
    content_rect = (MARGIN, TOPBAR_H + 2 * MARGIN, win_width - 2 * MARGIN, win_height - TOPBAR_H - BOTTOMBAR_H - 3 * MARGIN)
    bottombar_rect = (0, win_height - BOTTOMBAR_H, win_width, BOTTOMBAR_H)
    content_x, content_y, content_w, content_h = content_rect
    caption_h = int(max(80, 0.2 * content_h))
    image_panel_rect = (content_x + MARGIN, content_y, content_w - 2 * MARGIN, content_h - caption_h - MARGIN)
    caption_panel_rect = (content_x + MARGIN, content_y + content_h - caption_h, content_w - 2 * MARGIN, caption_h)

    # ---------- UI Drawing Functions ----------
    def draw_score_bar(img, score, points_to_win):
        SCORE_W = 400; SCORE_H = 34
        SCORE_X = (win_width - SCORE_W) // 2; SCORE_Y = MARGIN + (TOPBAR_H - SCORE_H) // 2
        cv2.rectangle(img, (SCORE_X, SCORE_Y), (SCORE_X + SCORE_W, SCORE_Y + SCORE_H), cv_color(PANEL_SHADOW), -1)
        fill_w = max(0, min(SCORE_W, int(SCORE_W * (score / max(1, points_to_win)))))
        if fill_w > 0: cv2.rectangle(img, (SCORE_X, SCORE_Y), (SCORE_X + fill_w, SCORE_Y + SCORE_H), cv_color(GOOD), -1)
        cv2.rectangle(img, (SCORE_X, SCORE_Y), (SCORE_X + SCORE_W, SCORE_Y + SCORE_H), cv_color(PANEL_BORDER), 3)
        put_center_text(img, f"Score: {score} / {points_to_win}", (SCORE_X + SCORE_W // 2, SCORE_Y + SCORE_H // 2 + 2), 0.8, TEXT, 2)

    def draw_strikes(img, wrongs, max_wrongs):
        radius = 18; pad = 20; y = win_height - BOTTOMBAR_H // 2
        total_w = max_wrongs * (2 * radius) + (max_wrongs - 1) * pad
        x_start = (win_width - total_w) // 2 + radius
        for i in range(max_wrongs):
            cx, cy = x_start + i * (2 * radius + pad), y
            cv2.circle(img, (cx, cy), radius, cv_color(GRAY), 3)
            if i < wrongs:
                off = int(radius * 0.7)
                cv2.line(img, (cx - off, cy - off), (cx + off, cy + off), cv_color(BAD), 5)
                cv2.line(img, (cx + off, cy - off), (cx - off, cy + off), cv_color(BAD), 5)

    btn_h = 48; btn_w = 150; btn_y = win_height - BOTTOMBAR_H // 2 - btn_h // 2
    mute_btn_rect = (MARGIN * 2, btn_y, btn_w, btn_h)
    def draw_button(img, rect, label, hover=False):
        x, y, w, h = rect
        base_color = ACCENT if hover else PANEL; txt_color = PANEL if hover else ACCENT_DARK
        cv2.rectangle(img, (x + 4, y + 4), (x + w + 4, y + h + 4), cv_color(PANEL_SHADOW), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(base_color), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(ACCENT_DARK), 2)
        put_center_text(img, label, (x + w // 2, y + h // 2 + 2), 0.8, txt_color, 2)

    def point_in_rect(pt, rect): x, y = pt; rx, ry, rw, rh = rect; return rx <= x <= rx + rw and ry <= y <= ry + rh

    def draw_caption(img, food_name):
        x, y, w, h = caption_panel_rect
        draw_panel(img, (x, y, w, h), PANEL, PANEL_BORDER, 2)
        put_center_text(img, f"Is {food_name} healthy?", (x + w // 2, y + h // 2 + 4), 1.0, TEXT, 3)

    def draw_image_in_panel(img, food_image, fit_rect):
        x, y, w, h = fit_rect
        draw_panel(img, (x, y, w, h), PANEL, PANEL_BORDER, 2)
        if food_image is None: put_center_text(img, "Image missing", (x + w // 2, y + h // 2), 1.0, TEXT); return
        ph, pw = food_image.shape[:2]
        s = min((w - MARGIN) / max(1, pw), (h - MARGIN) / max(1, ph))
        nw, nh = int(pw * s), int(ph * s)
        resized = cv2.resize(food_image, (nw, nh), interpolation=cv2.INTER_AREA)
        ox, oy = x + (w - nw) // 2, y + (h - nh) // 2
        img[oy:oy + nh, ox:ox + nw] = resized

    def draw_tick_or_cross(img, correct=True):
        x, y, w, h = image_panel_rect
        size = int(min(w, h) * 0.5); thickness = int(size * 0.1)
        center_x, center_y = x + w // 2, y + h // 2
        color = GOOD if correct else BAD
        if correct:
            pts = np.array([ [center_x - size // 3, center_y], [center_x - size // 8, center_y + size // 4], [center_x + size // 2, center_y - size // 4] ], np.int32)
            cv2.polylines(img, [pts], isClosed=False, color=cv_color(color), thickness=thickness)
        else:
            offset = size // 3
            cv2.line(img, (center_x - offset, center_y - offset), (center_x + offset, center_y + offset), cv_color(color), thickness)
            cv2.line(img, (center_x + offset, center_y - offset), (center_x - offset, center_y + offset), cv_color(color), thickness)

    # ---------- Mouse handling ----------
    mouse_pos, mouse_clicked = (0, 0), False
    def on_mouse(event, x, y, flags, userdata):
        nonlocal mouse_pos, mouse_clicked
        mouse_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN: mouse_clicked = True

    cv2.namedWindow(WINDOW_NAME); cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    # ---------- Core Game Logic ----------
    score, wrongs = 0, 0
    random.shuffle(FOOD_ITEMS); food_queue = FOOD_ITEMS.copy()
    running = True
    while running:
        if score >= POINTS_TO_WIN or wrongs >= MAX_WRONGS: break
        if not food_queue: random.shuffle(FOOD_ITEMS); food_queue = FOOD_ITEMS.copy()

        item = food_queue.pop(0)
        food_image = cv2.imread(item["image"])
        if food_image is None: print(f"Warning: Could not load image '{item['image']}'. Skipping."); continue

        frame = make_bg(win_height, win_width, BG)
        draw_panel(frame, topbar_rect, PANEL, PANEL_BORDER)
        draw_score_bar(frame, score, POINTS_TO_WIN)
        draw_image_in_panel(frame, food_image, image_panel_rect)
        draw_caption(frame, item["name"])
        draw_panel(frame, bottombar_rect, PANEL, PANEL_BORDER, shadow=False)
        draw_strikes(frame, wrongs, MAX_WRONGS)
        hover_mute = point_in_rect(mouse_pos, mute_btn_rect)
        draw_button(frame, mute_btn_rect, "Unmute" if audio_muted else "Mute", hover_mute)
        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == 27: running = False; continue
        if mouse_clicked:
            mouse_clicked = False
            if hover_mute: audio_muted = not audio_muted; set_music_paused(audio_muted); continue

        user_answer = detector.get_input()
        if user_answer is None: 
            print("Input cancelled. Exiting.");
            correct = 0 
        
        correct = (user_answer == "yes" and item["type"] == "healthy") or \
                  (user_answer == "no" and item["type"] == "junk")

        if correct:
            score += 1
            if SOUND_CORRECT and not audio_muted: SOUND_CORRECT.play()
        else:
            wrongs += 1
            if SOUND_WRONG and not audio_muted: SOUND_WRONG.play()
        
        feedback_frame = frame.copy()
        draw_tick_or_cross(feedback_frame, correct)
        cv2.imshow(WINDOW_NAME, feedback_frame)
        cv2.waitKey(1200)

    # ---------- End screen ----------
    if running:
        pygame.mixer.music.stop()
        won = score >= POINTS_TO_WIN
        bg_color = BG if won else BG_DARK
        msg = "YOU WIN!" if won else "Game Over"
        msg_color = GOOD if won else BAD

        if won:
            if SOUND_WIN and not audio_muted: SOUND_WIN.play()
            confetti = [ConfettiParticle(random.randint(0, win_width), random.randint(-win_height, 0), win_width, win_height) for _ in range(150)]
        else:
            if SOUND_LOSE and not audio_muted: SOUND_LOSE.play()

        start_time = time.time()
        while time.time() - start_time < 5.0:
            end_frame = make_bg(win_height, win_width, bg_color)
            if won:
                center_panel_rect = (MARGIN, TOPBAR_H + MARGIN, win_width - 2 * MARGIN, win_height - TOPBAR_H - BOTTOMBAR_H - 2 * MARGIN)
                draw_panel(end_frame, center_panel_rect, PANEL, PANEL_BORDER, 2)
            
            put_center_text(end_frame, msg, (win_width // 2, win_height // 2 - 16), 2.0, msg_color, 4, cv2.FONT_HERSHEY_TRIPLEX)
            draw_panel(end_frame, bottombar_rect, PANEL, PANEL_BORDER, shadow=False)
            put_center_text(end_frame, f"Exiting in {5 - int(time.time() - start_time)}...", (win_width // 2, win_height - BOTTOMBAR_H // 2 + 8), 0.95, TEXT_SUB, 2)

            if won:
                for p in confetti: p.update(); p.draw(end_frame)
            
            cv2.imshow(WINDOW_NAME, end_frame)
            if cv2.waitKey(15) & 0xFF == 27: break
    
    pygame.mixer.quit()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_healthy_vs_junk_food_game()

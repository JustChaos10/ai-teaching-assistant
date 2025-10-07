def runner_finger_counting_game():
    import cv2
    import numpy as np
    import random
    import os
    import tkinter as tk
    import pygame
    import time
    try:
        import fingers_counting_trails
    except ImportError:
        print("Warning: fingers_counting_trails module not found. Finger detection may not work properly.")
        fingers_counting_trails = None


    # ---------- STYLE / CONSTANTS ----------
    MARGIN = 16
    TOPBAR_H = 60
    BOTTOMBAR_H = 80
    SHADOW_OFFSET = 8

    # Colors (RGB)
    BG = (248, 250, 255)
    BG_DARK = (40, 45, 60) # Dark background for lose screen
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

    WINDOW_NAME = "Finger Counting Game"
    POINTS_TO_WIN = 5
    MAX_TOTAL_WRONG = 3
    SCALE_FACTOR = 0.65  # Reduced window width to minimize wasted space

    # --- Create dummy directories and files for the script to run ---
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    if not os.path.exists("count_images"):
        os.makedirs("count_images")

    # Note: You should replace these with actual sound and image files
    SOUNDS_DIR = "sounds"
    SOUND_CORRECT_PATH = os.path.join(SOUNDS_DIR, "correct.wav")
    SOUND_WRONG_PATH = os.path.join(SOUNDS_DIR, "wrong.wav")
    SOUND_WIN_PATH = os.path.join(SOUNDS_DIR, "win.wav")
    SOUND_LOSE_PATH = os.path.join(SOUNDS_DIR, "lose.wav")
    SOUND_BG_PATH = os.path.join(SOUNDS_DIR, "bg_music_fingers.wav")

    for p in [SOUND_CORRECT_PATH, SOUND_WRONG_PATH, SOUND_WIN_PATH, SOUND_LOSE_PATH, SOUND_BG_PATH]:
        if not os.path.exists(p): open(p, 'a').close()


    COUNT_ITEMS = [
        {"name": "One", "count": 1, "image": os.path.join("count_images", "one.jpg")},
        {"name": "Two", "count": 2, "image": os.path.join("count_images", "two.jpg")},
        {"name": "Three", "count": 3, "image": os.path.join("count_images", "three.jpg")},
        {"name": "Four", "count": 4, "image": os.path.join("count_images", "four.jpg")},
        {"name": "Five", "count": 5, "image": os.path.join("count_images", "five.jpg")},
    ]

    for item in COUNT_ITEMS:
        if not os.path.exists(item["image"]):
            img = np.full((100, 100, 3), (200, 200, 200), dtype=np.uint8)
            cv2.putText(img, str(item["count"]), (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 3)
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
    win_width = int(screen_width * SCALE_FACTOR*0.75)
    win_height = int(screen_height * SCALE_FACTOR)

    # ---------- Confetti Class for Win Screen ----------
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

    # ---------- OpenCV UI helpers ----------
    def cv_color(rgb):
        return (rgb[2], rgb[1], rgb[0])

    def make_bg(h, w, rgb):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = np.array(cv_color(rgb), dtype=np.uint8)[None, None, :]
        return frame

    def draw_panel(img, rect, fill, border, border_th=2, shadow=True):
        x, y, w, h = rect
        if shadow:
            sx, sy = x + SHADOW_OFFSET, y + SHADOW_OFFSET
            cv2.rectangle(img, (sx, sy), (sx + w, sy + h), cv_color(PANEL_SHADOW), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(fill), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(border), border_th)

    def put_center_text(img, text, center_xy, font_scale, color, thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX):
        size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        x = int(center_xy[0] - size[0] / 2)
        y = int(center_xy[1] + size[1] / 2)
        cv2.putText(img, text, (x, y), font, font_scale, cv_color(color), thickness, cv2.LINE_AA)

    # ---------- Layout elements ----------
    topbar_rect = (12, 10, win_width - 24, TOPBAR_H - 16)
    content_rect = (MARGIN, TOPBAR_H + MARGIN, win_width - 2 * MARGIN, win_height - TOPBAR_H - BOTTOMBAR_H - 2 * MARGIN)
    bottombar_rect = (0, win_height - BOTTOMBAR_H, win_width, BOTTOMBAR_H)

    content_x, content_y, content_w, content_h = content_rect
    caption_h = int(max(80, 0.2 * content_h))
    image_panel_rect = (content_x + 16, content_y + 16, content_w - 32, content_h - caption_h - 24)
    caption_panel_rect = (content_x + 16, content_y + content_h - caption_h, content_w - 32, caption_h - 8)

    # ---------- Centered score board ----------
    SCORE_W = 580
    SCORE_H = 34
    topbar_x, _, topbar_w, _ = topbar_rect
    SCORE_X = topbar_x + (topbar_w - SCORE_W) // 2
    SCORE_Y = 14 + TOPBAR_H // 2 - SCORE_H // 2

    def draw_score_bar(img, score, points_to_win):
        cv2.rectangle(img, (SCORE_X, SCORE_Y), (SCORE_X + SCORE_W, SCORE_Y + SCORE_H), cv_color(PANEL_SHADOW), -1)
        fill_w = max(0, min(SCORE_W, int(SCORE_W * (score / max(1, points_to_win)))))
        if fill_w > 0:
            cv2.rectangle(img, (SCORE_X, SCORE_Y), (SCORE_X + fill_w, SCORE_Y + SCORE_H), cv_color(GOOD), -1)
        cv2.rectangle(img, (SCORE_X, SCORE_Y), (SCORE_X + SCORE_W, SCORE_Y + SCORE_H), cv_color(PANEL_BORDER), 3)
        label = f"Score: {score} / {points_to_win}"
        put_center_text(img, label, (SCORE_X + SCORE_W // 2, SCORE_Y + SCORE_H // 2 + 4), 0.95, TEXT, thickness=2)

    def draw_strikes_bottom(img, total_wrong, max_total_wrong):
        radius = max(18, int(win_height * 0.025))
        pad = max(26, int(win_width * 0.018))
        y = win_height - BOTTOMBAR_H // 2 + 6
        total_w = max_total_wrong * (2 * radius) + (max_total_wrong - 1) * pad
        x_start = (win_width - total_w) // 2 + radius
        for i in range(max_total_wrong):
            cx = x_start + i * (2 * radius + pad)
            cy = y
            cv2.circle(img, (cx, cy), radius, cv_color(GRAY), 3)
            if i < total_wrong:
                off = int(radius * 0.7)
                cv2.line(img, (cx - off, cy - off), (cx + off, cy + off), cv_color(BAD), 5)
                cv2.line(img, (cx + off, cy - off), (cx - off, cy + off), cv_color(BAD), 5)

    btn_h = 48
    btn_w = 150
    btn_y = win_height - BOTTOMBAR_H // 2 - btn_h // 2
    mute_btn_rect = (MARGIN + 16, btn_y, btn_w, btn_h)

    def draw_button(img, rect, label, hover=False):
        x, y, w, h = rect
        base_color = ACCENT if hover else PANEL
        txt_color = PANEL if hover else ACCENT_DARK
        cv2.rectangle(img, (x + 3, y + 3), (x + w + 3, y + h + 3), cv_color(PANEL_SHADOW), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(base_color), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(ACCENT_DARK), 2)
        put_center_text(img, label, (x + w // 2, y + h // 2 + 4), 0.9, txt_color, thickness=2)

    def point_in_rect(pt, rect):
        x, y = pt
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def draw_caption(img, text):
        x, y, w, h = caption_panel_rect
        draw_panel(img, (x, y, w, h), PANEL, PANEL_BORDER, 2, shadow=True)
        scale = max(1.0, w / 800)
        put_center_text(img, f"{text}", (x + w // 2, y + h // 2 + 8), scale, TEXT, thickness=4)

    def draw_image_in_panel(img, picture_bgr, fit_rect):
        x, y, w, h = fit_rect
        draw_panel(img, (x, y, w, h), PANEL, PANEL_BORDER, 2, shadow=True)
        if picture_bgr is None:
            put_center_text(img, "Image missing", (x + w // 2, y + h // 2), 1.0, TEXT)
            return
        ph, pw = picture_bgr.shape[:2]
        s = min(w / max(1, pw), h / max(1, ph))
        nw, nh = int(pw * s), int(ph * s)
        resized = cv2.resize(picture_bgr, (nw, nh), interpolation=cv2.INTER_AREA)
        ox = x + (w - nw) // 2
        oy = y + (h - nh) // 2
        img[oy:oy + nh, ox:ox + nw] = resized

    def draw_tick_or_cross_over_image(img, correct=True):
        x, y, w, h = image_panel_rect
        size = int(min(w, h) * 0.42)
        center_x, center_y = x + w // 2, y + h // 2
        thickness = max(8, int(size * 0.1))
        color = GOOD if correct else BAD

        if correct:
            pt1 = (center_x - size // 3, center_y)
            pt2 = (center_x - size // 8, center_y + size // 4)
            pt3 = (center_x + size // 2, center_y - size // 4)
            cv2.line(img, pt1, pt2, cv_color(color), thickness)
            cv2.line(img, pt2, pt3, cv_color(color), thickness)
        else:
            offset = size // 3
            cv2.line(img, (center_x - offset, center_y - offset), (center_x + offset, center_y + offset), cv_color(color), thickness)
            cv2.line(img, (center_x + offset, center_y - offset), (center_x - offset, center_y + offset), cv_color(color), thickness)

    # ---------- Mouse handling ----------
    mouse_pos = (0, 0)
    mouse_clicked = False

    def on_mouse(event, x, y, flags, userdata):
        nonlocal mouse_pos, mouse_clicked
        mouse_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            mouse_clicked = True

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    # ---------- Game state ----------
    score = 0
    total_wrong = 0
    random.shuffle(COUNT_ITEMS)
    count_queue = COUNT_ITEMS.copy()

    # ---------- Main loop ----------
    # ---------- Main loop ----------
    running = True
    while running:
        if score >= POINTS_TO_WIN or total_wrong >= MAX_TOTAL_WRONG:
            break

        if not count_queue:
            count_queue = COUNT_ITEMS.copy()
            random.shuffle(count_queue)

        item = count_queue.pop(0)
        count_name = item["name"]
        count_needed = item["count"]
        image_path = item["image"]

        picture = cv2.imread(image_path)
        if picture is None:
            print(f"Warning: Could not load image '{image_path}'. Skipping.")
            continue

        # --- Build the initial frame with a generic prompt ---
        frame = make_bg(win_height, win_width, BG)
        draw_score_bar(frame, score, POINTS_TO_WIN)
        draw_image_in_panel(frame, picture, image_panel_rect)
        draw_panel(frame, bottombar_rect, PANEL, PANEL_BORDER, 2, shadow=True)
        draw_strikes_bottom(frame, total_wrong, MAX_TOTAL_WRONG)

        hover_mute = point_in_rect(mouse_pos, mute_btn_rect)
        draw_button(frame, mute_btn_rect, "Unmute" if audio_muted else "Mute", hover=hover_mute)

        # CHANGE 1: Show a generic prompt before the user gives input
        draw_caption(frame, "Ready? Show your hand!")

        cv2.imshow(WINDOW_NAME, frame)

        # --- Handle non-gameplay actions like mute or exit ---
        key = cv2.waitKey(30) & 0xFF
        if key == 27:
            running = False
            continue

        if mouse_clicked:
            mouse_clicked = False 
            if hover_mute:
                audio_muted = not audio_muted
                set_music_paused(audio_muted)
                continue # Skip the rest of the loop to redraw the button instantly

        # --- Get user's finger count ---
        if fingers_counting_trails is not None:
            finger_count = fingers_counting_trails.get_finger_count_with_timer(2)
        else:
            print("Finger counting module not available, using random for demo")
            finger_count = random.randint(1, 5)  # Demo mode
        correct = (finger_count == count_needed)

        # --- Update score and play sound ---
        if correct:
            score += 1
            if SOUND_CORRECT and not audio_muted:
                try: SOUND_CORRECT.play()
                except Exception: pass
        else:
            total_wrong += 1
            if SOUND_WRONG and not audio_muted:
                try: SOUND_WRONG.play()
                except Exception: pass

        # --- Build the feedback frame, now revealing the answer ---
        feedback_frame = frame.copy()
        
        # CHANGE 2: Reveal the correct answer on the feedback screen
        draw_caption(feedback_frame, count_name)
        
        draw_tick_or_cross_over_image(feedback_frame, correct)
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
            if SOUND_WIN and not audio_muted:
                try: SOUND_WIN.play()
                except Exception: pass
            confetti = [ConfettiParticle(random.randint(0, win_width), random.randint(-win_height, 0), win_width, win_height) for _ in range(150)]
        else:
            if SOUND_LOSE and not audio_muted:
                try: SOUND_LOSE.play()
                except Exception: pass

        start_time = time.time()
        while time.time() - start_time < 5.0:
            end_frame = make_bg(win_height, win_width, bg_color)
            
            # FIX: Only draw the center panel on the win screen
            if won:
                center_panel_rect = (MARGIN, TOPBAR_H + MARGIN, win_width - 2 * MARGIN, win_height - TOPBAR_H - BOTTOMBAR_H - 2 * MARGIN)
                draw_panel(end_frame, center_panel_rect, PANEL, PANEL_BORDER, 2, shadow=True)
            
            put_center_text(end_frame, msg, (win_width // 2, win_height // 2 - 16), 2.0, msg_color, thickness=4, font=cv2.FONT_HERSHEY_TRIPLEX)
            
            draw_panel(end_frame, bottombar_rect, PANEL, PANEL_BORDER, 2, shadow=True)
            put_center_text(end_frame, f"Exiting in {5 - int(time.time() - start_time)}...", (win_width // 2, win_height - BOTTOMBAR_H // 2 + 8), 0.95, TEXT_SUB, thickness=2)

            if won:
                for p in confetti:
                    p.update()
                    p.draw(end_frame)

            cv2.imshow(WINDOW_NAME, end_frame)
            if cv2.waitKey(15) & 0xFF == 27:
                break
    
    pygame.mixer.quit()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    runner_finger_counting_game()

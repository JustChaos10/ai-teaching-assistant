import cv2
import numpy as np
import random
import os
import tkinter as tk
import pygame
import detector  # your color placard detection module

def run_healthy_vs_junk_food_game():
    """
    Sets up and runs the entire Healthy vs. Junk Food game.
    """
    # --- Game Configuration ---
    POINTS_TO_WIN = 5
    MAX_WRONGS = 3
    WINDOW_NAME = "Healthy vs. Junk Food Game"
    SCALE_FACTOR = 0.5

    pygame.mixer.init()
    SOUND_CORRECT = pygame.mixer.Sound(os.path.join("sounds", "correct.wav"))
    SOUND_WRONG = pygame.mixer.Sound(os.path.join("sounds", "wrong.wav"))
    SOUND_WIN = pygame.mixer.Sound(os.path.join("sounds", "win.wav"))

    FOOD_ITEMS = [
        {"name": "Apple", "type": "healthy", "image": os.path.join("images", "apple.jpg")},
        {"name": "Broccoli", "type": "healthy", "image": os.path.join("images", "broccoli.jpg")},
        {"name": "Carrot", "type": "healthy", "image": os.path.join("images", "carrot.jpg")},
        {"name": "Pizza", "type": "junk", "image": os.path.join("images", "pizza.jpg")},
        {"name": "Burger", "type": "junk", "image": os.path.join("images", "burger.jpg")},
        {"name": "Donut", "type": "junk", "image": os.path.join("images", "donut.jpg")},
    ]

    # --- Helper Functions (defined inside the main runner) ---
    def get_screen_dimensions():
        root = tk.Tk()
        root.withdraw()
        return root.winfo_screenwidth(), root.winfo_screenheight()

    def draw_score_bar(image, score, points_to_win):
        height, width, _ = image.shape
        bar_width = int(width * 0.6)
        bar_height = int(height * 0.05)
        x_start = int(width * 0.2)
        y_start = int(height * 0.05)
        cv2.rectangle(image, (x_start, y_start), (x_start + bar_width, y_start + bar_height), (50, 50, 50), -1)
        fill_width = int(bar_width * (score / points_to_win))
        cv2.rectangle(image, (x_start, y_start), (x_start + fill_width, y_start + bar_height), (0, 255, 0), -1)
        cv2.rectangle(image, (x_start, y_start), (x_start + bar_width, y_start + bar_height), (0, 0, 0), 2)
        text = f"Score: {score} / {points_to_win}"
        font_scale = bar_height / 30
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = x_start + (bar_width - text_size[0]) // 2
        text_y = y_start + (bar_height + text_size[1]) // 2
        cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

    def draw_strikes(image, wrongs, max_wrongs):
        height, width, _ = image.shape
        radius = int(height * 0.02)
        padding = int(width * 0.02)
        y_pos = int(height * 0.15)
        x_start = width - padding - radius
        for i in range(max_wrongs):
            center_x = x_start - i * (2 * radius + padding)
            center_y = y_pos
            cv2.circle(image, (center_x, center_y), radius, (100, 100, 100), 2)
            if i < wrongs:
                offset = int(radius * 0.7)
                thickness = 3
                color = (0, 0, 255) # Red
                cv2.line(image, (center_x - offset, center_y - offset), (center_x + offset, center_y + offset), color, thickness)
                cv2.line(image, (center_x + offset, center_y - offset), (center_x - offset, center_y + offset), color, thickness)

    def draw_food_name(image, food_name):
        height, width, _ = image.shape
        font_scale = width / 700
        thickness = 3
        text_size = cv2.getTextSize(food_name, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        text_width, text_height = text_size
        x = (width - text_width) // 2
        y = height - int(height * 0.07)
        padding_x, padding_y = 30, 16
        rect_x1 = x - padding_x
        rect_y1 = y - text_height - padding_y
        rect_x2 = x + text_width + padding_x
        rect_y2 = y + padding_y
        overlay = image.copy()
        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (255, 255, 255), -1)
        alpha = 0.92
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        cv2.putText(image, food_name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

    def display_tick_or_cross(image, correct=True):
        height, width, _ = image.shape
        size = int(min(width, height) * 0.50)
        center = (width // 2, int(height * 0.6))
        thickness = int(size * 0.1)
        color = (0, 255, 0) if correct else (0, 0, 255)
        if correct:
            pt1 = (center[0] - size // 4, center[1])
            pt2 = (center[0] - size // 10, center[1] + size // 4)
            pt3 = (center[0] + size // 3, center[1] - size // 5)
            cv2.line(image, pt1, pt2, color, thickness)
            cv2.line(image, pt2, pt3, color, thickness)
        else:
            offset = size // 3
            cv2.line(image, (center[0] - offset, center[1] - offset), (center[0] + offset, center[1] + offset), color, thickness)
            cv2.line(image, (center[0] + offset, center[1] - offset), (center[0] - offset, center[1] + offset), color, thickness)

    # --- Core Game Logic ---
    def main_game():
        screen_width, screen_height = get_screen_dimensions()
        win_width = int(screen_width * SCALE_FACTOR)
        win_height = int(screen_height * SCALE_FACTOR)
        
        score = 0
        wrongs = 0
        random.shuffle(FOOD_ITEMS)
        food_queue = FOOD_ITEMS.copy()

        while score < POINTS_TO_WIN and wrongs < MAX_WRONGS:
            if not food_queue:
                food_queue = FOOD_ITEMS.copy()
                random.shuffle(food_queue)
            
            item = food_queue.pop(0)
            item_name = item["name"]
            item_type = item["type"]
            image_path = item["image"]
            
            frame = cv2.imread(image_path)
            if frame is None:
                print(f"Warning: Could not load image '{image_path}'. Skipping.")
                continue
            
            frame = cv2.resize(frame, (win_width, win_height))
            draw_score_bar(frame, score, POINTS_TO_WIN)
            draw_strikes(frame, wrongs, MAX_WRONGS)
            draw_food_name(frame, item_name)
            
            cv2.imshow(WINDOW_NAME, frame)
            cv2.waitKey(1)
            
            print("\n-------------------------")
            print(f"Is '{item_name}' a healthy food?")
            print("Show your placard to the camera...")
            
            user_answer = detector.get_input()
            correct = False
            
            if user_answer == "yes" and item_type == "healthy":
                correct = True
            elif user_answer == "no" and item_type == "junk":
                correct = True
            elif user_answer is None:
                print("Input cancelled. Exiting game.")
                break
            
            if correct:
                score += 1
                SOUND_CORRECT.play()
            else:
                wrongs += 1
                SOUND_WRONG.play()
                
            display_tick_or_cross(frame, correct)
            cv2.imshow(WINDOW_NAME, frame)
            cv2.waitKey(1200)

        # --- End Screen ---
        end_screen = np.zeros((win_height, win_width, 3), dtype=np.uint8)
        font_scale_title = win_width / 400
        font_scale_subtitle = win_width / 800
        
        if score >= POINTS_TO_WIN:
            print("\nCongratulations! You reached the required score!")
            cv2.putText(end_screen, "YOU WIN!", (int(win_width * 0.24), int(win_height * 0.5)),
                        cv2.FONT_HERSHEY_TRIPLEX, font_scale_title, (50, 200, 50), 3)
            SOUND_WIN.play()
        else:
            cv2.putText(end_screen, "Game Over", (int(win_width * 0.18), int(win_height * 0.5)),
                        cv2.FONT_HERSHEY_TRIPLEX, font_scale_title, (200, 200, 200), 3)
                        
        cv2.putText(end_screen, "Press any key to exit", (int(win_width * 0.22), int(win_height * 0.7)),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale_subtitle, (255, 255, 255), 2)
        cv2.imshow(WINDOW_NAME, end_screen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # --- Start the game by calling the main_game function ---
    main_game()

# This block now calls the single encapsulating function to run the game.
if __name__ == "__main__":
    run_healthy_vs_junk_food_game()
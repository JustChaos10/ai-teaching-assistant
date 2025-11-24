import cv2
import numpy as np
import time
import tkinter as tk

# --- Configuration ---
MIN_AREA = 3000
HOLD_DURATION = 2.0
MAX_RUNTIME = 15.0 # Maximum time in seconds for the function to run

# --- HSV Color Ranges ---
LOWER_GREEN = np.array([40, 70, 80])
UPPER_GREEN = np.array([80, 255, 255])
LOWER_RED1 = np.array([0, 120, 100])
UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([170, 120, 100])
UPPER_RED2 = np.array([180, 255, 255])

def draw_progress_circle(frame, center, radius, progress, color):
    """
    Draws a circular pie-progress indicator on the frame.
    - progress: float from 0.0 to 1.0 (shows percentage filled)
    - color: (B, G, R) tuple for the filled color
    """
    # Draw the background circle (light gray)
    cv2.circle(frame, center, radius, (220, 220, 220), 2)
    if progress > 0:
        angle = int(progress * 360)
        overlay = frame.copy()
        # Filled colored arc (pie wedge)
        cv2.ellipse(overlay, center, (radius, radius), 0, -90, -90 + angle, color, -1)
        # Blend the overlay with frame for a smooth look
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

# --- MODIFICATION: Helper function to find the largest valid contour ---
def find_largest_contour(contours, min_area):
    """ Finds the largest contour in a list, provided it's larger than min_area. """
    if not contours:
        return None
    
    largest_c = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest_c) > min_area:
        return largest_c
        
    return None
# --- END MODIFICATION ---

import tkinter as tk

class ColorDetector:
    def __init__(self):
        self.detection_state = None
        self.start_time = None

    def process_frame(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        green_mask = cv2.inRange(hsv_frame, LOWER_GREEN, UPPER_GREEN)
        red_mask = cv2.inRange(hsv_frame, LOWER_RED1, UPPER_RED1) + \
                   cv2.inRange(hsv_frame, LOWER_RED2, UPPER_RED2)

        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        largest_green = find_largest_contour(green_contours, MIN_AREA)
        largest_red = find_largest_contour(red_contours, MIN_AREA)

        current_detection = None
        if largest_green is not None and largest_red is None:
            current_detection = 'green'
            highlight_color = (0, 255, 0)
            cv2.drawContours(frame, [largest_green], -1, highlight_color, 3)
        elif largest_red is not None and largest_green is None:
            current_detection = 'red'
            highlight_color = (0, 0, 255)
            cv2.drawContours(frame, [largest_red], -1, highlight_color, 3)

        if current_detection != self.detection_state:
            self.detection_state = current_detection
            self.start_time = time.time() if current_detection is not None else None

        if self.detection_state is not None and self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            progress = min(elapsed_time / HOLD_DURATION, 1.0)

            circle_center = (frame.shape[1] // 2, frame.shape[0] // 2)
            circle_radius = 80
            circle_color = (0, 255, 0) if self.detection_state == 'green' else (0, 0, 255)
            draw_progress_circle(frame, circle_center, circle_radius, progress, circle_color)

            if progress < 1.0:
                hold_text = "HOLD!"
                (text_w, text_h), _ = cv2.getTextSize(hold_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                cv2.putText(frame, hold_text, (circle_center[0] - text_w // 2, circle_center[1] + circle_radius + text_h + 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            if elapsed_time >= HOLD_DURATION:
                return "yes" if self.detection_state == 'green' else "no"
        
        return None

    def reset(self):
        self.detection_state = None
        self.start_time = None


# --- Example of how to call it (for testing purposes) ---
if __name__ == '__main__':
    print("This is a test run of the detector module.")
    print(f"Please show a green or red placard to the camera within {MAX_RUNTIME} seconds.")
    user_choice = get_input()
    if user_choice:
        print(f"\nThe function returned: '{user_choice}'")
    else:
        print("\nNo choice was made or the process was quit/timed out.")
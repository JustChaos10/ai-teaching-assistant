import cv2
import mediapipe as mp
import time
import numpy as np
import tkinter as tk

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Landmark IDs for the tips of the fingers
finger_tips_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

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


def count_fingers_with_status(hand_landmarks):
    """
    Counts the number of raised fingers from a given hand landmark list.
    Returns the total count and a list of booleans indicating the status of each finger.
    """
    count = 0
    finger_status = [False] * 5  # [Thumb, Index, Middle, Ring, Pinky]
    
    # Thumb: Check if its x-coordinate is to the left of the joint below it (for a right hand in a flipped view).
    if hand_landmarks.landmark[finger_tips_ids[0]].x < hand_landmarks.landmark[finger_tips_ids[0] - 1].x:
        count += 1
        finger_status[0] = True
    
    # Other four fingers: Check if the fingertip is above the joint two landmarks below it.
    for i, tip_id in enumerate(finger_tips_ids[1:], 1):
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            count += 1
            finger_status[i] = True
    
    return count, finger_status

def draw_finger_circles(frame, hand_landmarks, finger_status):
    """
    Draws circles on the tips of raised fingers.
    """
    height, width, _ = frame.shape
    
    for i, is_raised in enumerate(finger_status):
        if is_raised:
            # Get the normalized coordinates of the fingertip
            tip_landmark = hand_landmarks.landmark[finger_tips_ids[i]]
            # Convert to pixel coordinates
            tip_x = int(tip_landmark.x * width)
            tip_y = int(tip_landmark.y * height)
            
            # Draw a filled red circle with a white border
            cv2.circle(frame, (tip_x, tip_y), 15, (0, 255, 0), -1)
            cv2.circle(frame, (tip_x, tip_y), 15, (255, 255, 255), 2)

class FingerCounter:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.detected_fingers = None
        self.gesture_start_time = None

    def process_frame(self, frame, duration=2):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        final_count = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers, finger_status = count_fingers_with_status(hand_landmarks)
                draw_finger_circles(frame, hand_landmarks, finger_status)
                
                if self.detected_fingers != fingers:
                    self.detected_fingers = fingers
                    self.gesture_start_time = time.time()
                
                if self.gesture_start_time:
                    elapsed_time = time.time() - self.gesture_start_time
                    progress = min(elapsed_time / duration, 1.0)

                    circle_center = (frame.shape[1] // 2, frame.shape[0] // 2)
                    circle_radius = 80
                    circle_color = (0, 255, 0)
                    draw_progress_circle(frame, circle_center, circle_radius, progress, circle_color)

                    if progress < 1.0:
                        hold_text = "HOLD!"
                        (text_w, text_h), _ = cv2.getTextSize(hold_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                        cv2.putText(frame, hold_text, (circle_center[0] - text_w // 2, circle_center[1] + circle_radius + text_h + 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

                    if elapsed_time > duration:
                        final_count = self.detected_fingers
        else:
            self.gesture_start_time = None
            self.detected_fingers = None
            
        return final_count

    def reset(self):
        self.detected_fingers = None
        self.gesture_start_time = None



# Standalone test
if __name__ == "__main__":
    print("Starting finger count detection. The window will close after 10 seconds.")
    count = get_finger_count_with_timer(duration=2, max_runtime_seconds=10)
    
    if count is not None:
        print(f"Final counted fingers: {count}")
    else:
        print("No final count was determined.")

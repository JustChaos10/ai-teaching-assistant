import cv2
import mediapipe as mp
import time

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

def get_finger_count_with_timer(duration=2, max_runtime_seconds=10, stop_event=None):
    """
    Opens the camera, displays a countdown, and detects a stable finger count.
    """
    cap = cv2.VideoCapture(0)
    window_name = 'Show Your Hand!'
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    
    gesture_start_time = None
    detected_fingers = None
    final_count = None

    # Timer for the overall 10-second runtime
    overall_start_time = time.time()

    while True:
        elapsed_time = time.time() - overall_start_time
        remaining_time = max(0, max_runtime_seconds - elapsed_time)

        # Exit if 10 seconds have passed
        if remaining_time == 0:
            print(f"Timeout: Exiting after {max_runtime_seconds} seconds.")
            break

        # Handle threaded exit signals if applicable
        if stop_event and stop_event.is_set():
            break

        success, frame = cap.read()
        if not success:
            break
        
        # --- RESIZE AND FLIP THE FRAME ---
        # Flip the frame horizontally for a mirror view first
        frame = cv2.flip(frame, 1)
        # Then, resize the frame to half its original size
        height, width, _ = frame.shape
        frame = cv2.resize(frame, (width // 2, height // 2))

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers, finger_status = count_fingers_with_status(hand_landmarks)
                draw_finger_circles(frame, hand_landmarks, finger_status)
                
                # If the finger count changes, reset the gesture timer
                if detected_fingers != fingers:
                    detected_fingers = fingers
                    gesture_start_time = time.time()
                
                # If a gesture is held for the required duration, lock it in
                if gesture_start_time and (time.time() - gesture_start_time) > duration:
                    final_count = detected_fingers
                    break # Exit the inner for-loop
        else:
            # If no hand is detected, reset the gesture timer
            gesture_start_time = None
            detected_fingers = None
        
        # --- DISPLAY THE COUNTDOWN TIMER ---
        timer_text = f"{int(remaining_time)}"
        font_scale = 2.5
        thickness = 4
        outline_thickness = 7
        text_pos = (30, 80) # Position in the top-left corner
        
        # Draw white outline by drawing text with a thicker stroke
        cv2.putText(frame, timer_text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), outline_thickness, cv2.LINE_AA)
        # Draw the black text on top
        cv2.putText(frame, timer_text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)


        cv2.imshow(window_name, frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27: # ESC key
            final_count = None 
            break

        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            final_count = None
            break

        if final_count is not None:
            time.sleep(0.5) # Pause briefly to show the locked-in count
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    return final_count

# Standalone test
if __name__ == "__main__":
    print("Starting finger count detection. The window will close after 10 seconds.")
    count = get_finger_count_with_timer(duration=2, max_runtime_seconds=10)
    
    if count is not None:
        print(f"Final counted fingers: {count}")
    else:
        print("No final count was determined.")

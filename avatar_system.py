import cv2
import numpy as np
import os
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMovie, QPixmap, QPainter, QPen, QBrush
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
import math
import random

class AnimatedAvatar(QObject):
    """
    Enhanced animated avatar system for the teaching assistant.
    Creates a more cartoon-like character with moving mouth, eyes, and expressions.
    """
    
    animation_changed = pyqtSignal(QPixmap)
    
    def __init__(self, width=400, height=400):
        super().__init__()
        self.width = width
        self.height = height
        self.current_state = "idle"
        self.frame_count = 0
        
        # Animation parameters
        self.mouth_open = 0.0  # 0.0 to 1.0
        self.eye_blink = 0.0   # 0.0 to 1.0
        self.head_tilt = 0.0   # -0.5 to 0.5
        
        # Colors
        self.face_color = (255, 220, 177)  # Skin tone
        self.eye_color = (50, 50, 50)      # Dark gray
        self.mouth_color = (200, 50, 50)   # Red
        self.hair_color = (139, 69, 19)    # Brown
        
        # Timer for animations
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(100)  # 10 FPS
        
    def set_state(self, state):
        """Set the animation state: idle, listening, thinking, speaking"""
        self.current_state = state
        
    def update_animation(self):
        """Update animation frame"""
        self.frame_count += 1
        
        # Update animation parameters based on state
        if self.current_state == "idle":
            self.mouth_open = 0.1 + 0.05 * math.sin(self.frame_count * 0.1)
            self.eye_blink = 1.0 if (self.frame_count % 60) < 5 else 0.0
            self.head_tilt = 0.02 * math.sin(self.frame_count * 0.05)
            
        elif self.current_state == "listening":
            self.mouth_open = 0.2 + 0.1 * math.sin(self.frame_count * 0.3)
            self.eye_blink = 0.0  # Wide eyes when listening
            self.head_tilt = 0.05 * math.sin(self.frame_count * 0.1)
            
        elif self.current_state == "thinking":
            self.mouth_open = 0.1
            self.eye_blink = 0.3  # Squinting slightly
            self.head_tilt = 0.1 * math.sin(self.frame_count * 0.08)
            
        elif self.current_state == "speaking":
            # Animated mouth movement for speaking
            self.mouth_open = 0.3 + 0.4 * abs(math.sin(self.frame_count * 0.8))
            self.eye_blink = 1.0 if (self.frame_count % 40) < 3 else 0.0
            self.head_tilt = 0.03 * math.sin(self.frame_count * 0.2)
        
        # Generate the frame
        pixmap = self.generate_frame()
        self.animation_changed.emit(pixmap)
        
    def generate_frame(self):
        """Generate a single animation frame"""
        # Create blank canvas
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        canvas.fill(240)  # Light background
        
        # Calculate center and head position
        center_x, center_y = self.width // 2, self.height // 2
        head_offset_x = int(self.head_tilt * 20)
        head_offset_y = int(abs(self.head_tilt) * 10)
        
        # Draw head (circle)
        head_center = (center_x + head_offset_x, center_y - 30 + head_offset_y)
        head_radius = 80
        cv2.circle(canvas, head_center, head_radius, self.face_color, -1)
        cv2.circle(canvas, head_center, head_radius, (200, 200, 200), 2)
        
        # Draw hair
        hair_points = []
        for angle in range(0, 180, 20):
            rad = math.radians(angle)
            hair_x = head_center[0] + int((head_radius + 15) * math.cos(rad + math.pi))
            hair_y = head_center[1] + int((head_radius + 15) * math.sin(rad + math.pi))
            hair_points.append([hair_x, hair_y])
        
        if len(hair_points) > 2:
            hair_points = np.array(hair_points)
            cv2.fillPoly(canvas, [hair_points], self.hair_color)
        
        # Draw eyes
        eye_y = head_center[1] - 15
        left_eye_center = (head_center[0] - 25, eye_y)
        right_eye_center = (head_center[0] + 25, eye_y)
        
        # Eye whites
        eye_radius = 12
        cv2.circle(canvas, left_eye_center, eye_radius, (255, 255, 255), -1)
        cv2.circle(canvas, right_eye_center, eye_radius, (255, 255, 255), -1)
        
        # Eye pupils (affected by blinking)
        if self.eye_blink < 0.8:
            pupil_radius = int(6 * (1 - self.eye_blink))
            cv2.circle(canvas, left_eye_center, pupil_radius, self.eye_color, -1)
            cv2.circle(canvas, right_eye_center, pupil_radius, self.eye_color, -1)
        else:
            # Draw closed eyes (lines)
            cv2.line(canvas, (left_eye_center[0] - 10, left_eye_center[1]), 
                    (left_eye_center[0] + 10, left_eye_center[1]), self.eye_color, 3)
            cv2.line(canvas, (right_eye_center[0] - 10, right_eye_center[1]), 
                    (right_eye_center[0] + 10, right_eye_center[1]), self.eye_color, 3)
        
        # Draw eyebrows
        cv2.line(canvas, (left_eye_center[0] - 15, left_eye_center[1] - 15), 
                (left_eye_center[0] + 5, left_eye_center[1] - 20), self.hair_color, 4)
        cv2.line(canvas, (right_eye_center[0] - 5, right_eye_center[1] - 20), 
                (right_eye_center[0] + 15, right_eye_center[1] - 15), self.hair_color, 4)
        
        # Draw nose (small triangle)
        nose_tip = (head_center[0], head_center[1] + 5)
        nose_left = (head_center[0] - 5, head_center[1] + 15)
        nose_right = (head_center[0] + 5, head_center[1] + 15)
        nose_points = np.array([nose_tip, nose_left, nose_right])
        cv2.fillPoly(canvas, [nose_points], (220, 180, 140))
        
        # Draw mouth (affected by mouth_open parameter)
        mouth_center = (head_center[0], head_center[1] + 35)
        mouth_width = int(20 + 15 * self.mouth_open)
        mouth_height = int(5 + 15 * self.mouth_open)
        
        if self.mouth_open > 0.3:
            # Open mouth (oval)
            cv2.ellipse(canvas, mouth_center, (mouth_width, mouth_height), 0, 0, 360, (100, 50, 50), -1)
            # Teeth
            if self.mouth_open > 0.5:
                cv2.ellipse(canvas, (mouth_center[0], mouth_center[1] - mouth_height//3), 
                           (mouth_width-4, 3), 0, 0, 360, (255, 255, 255), -1)
        else:
            # Closed mouth (line with slight curve)
            cv2.ellipse(canvas, mouth_center, (mouth_width, 3), 0, 0, 360, self.mouth_color, -1)
        
        # Add some rosy cheeks
        left_cheek = (head_center[0] - 35, head_center[1] + 10)
        right_cheek = (head_center[0] + 35, head_center[1] + 10)
        cv2.circle(canvas, left_cheek, 8, (255, 200, 200), -1)
        cv2.circle(canvas, right_cheek, 8, (255, 200, 200), -1)
        
        # Convert to QPixmap
        height, width, channel = canvas.shape
        bytes_per_line = 3 * width
        
        # Convert BGR to RGB for Qt
        rgb_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        
        from PyQt6.QtGui import QImage
        q_image = QImage(rgb_canvas.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        return QPixmap.fromImage(q_image)

class TeachingAssistantUI(QLabel):
    """Enhanced UI widget for the teaching assistant with animated avatar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create animated avatar
        self.avatar = AnimatedAvatar(400, 400)
        self.avatar.animation_changed.connect(self.update_avatar)
        
        # Fallback to original animation system if avatar fails
        self.setup_fallback_animations()
        self.use_avatar = True
        
    def setup_fallback_animations(self):
        """Setup fallback animation system using GIFs"""
        try:
            self.listening_anim = QMovie("animations/listening.gif")
            self.thinking_anim = QMovie("animations/thinking.gif")
            self.speaking_anim = QMovie("animations/speaking.gif")
            self.idle_anim = QMovie("animations/idle.gif")
            
            # Check if animations loaded successfully
            if not all([self.listening_anim.isValid(), self.thinking_anim.isValid(), 
                       self.speaking_anim.isValid(), self.idle_anim.isValid()]):
                raise FileNotFoundError("Some animation files are invalid")
                
        except (FileNotFoundError, Exception) as e:
            print(f"Warning: Animation files not found: {e}")
            print("Using programmatic avatar instead")
            self.listening_anim = None
            self.thinking_anim = None
            self.speaking_anim = None
            self.idle_anim = None
    
    def update_avatar(self, pixmap):
        """Update the avatar display"""
        if self.use_avatar:
            self.setPixmap(pixmap)
    
    def set_state(self, state):
        """Set the avatar state"""
        if self.use_avatar:
            self.avatar.set_state(state)
        else:
            # Fallback to text or GIF animations
            if state == "idle":
                if self.idle_anim:
                    self.setMovie(self.idle_anim)
                    self.idle_anim.start()
                else:
                    self.setText("🤖 Ready to help!")
            elif state == "listening":
                if self.listening_anim:
                    self.setMovie(self.listening_anim)
                    self.listening_anim.start()
                else:
                    self.setText("👂 Listening...")
            elif state == "thinking":
                if self.thinking_anim:
                    self.setMovie(self.thinking_anim)
                    self.thinking_anim.start()
                else:
                    self.setText("🤔 Thinking...")
            elif state == "speaking":
                if self.speaking_anim:
                    self.setMovie(self.speaking_anim)
                    self.speaking_anim.start()
                else:
                    self.setText("🗣️ Speaking...")

# Test the avatar system
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Teaching Assistant Avatar Test")
    
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    # Create the teaching assistant UI
    assistant = TeachingAssistantUI()
    layout.addWidget(assistant)
    
    # Add buttons to test different states
    states = ["idle", "listening", "thinking", "speaking"]
    for state in states:
        btn = QPushButton(f"Set {state.title()}")
        btn.clicked.connect(lambda checked, s=state: assistant.set_state(s))
        layout.addWidget(btn)
    
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    window.show()
    sys.exit(app.exec())
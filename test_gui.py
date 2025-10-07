"""
Test GUI initialization without the backend worker
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

def test_gui():
    """Test basic GUI functionality"""
    print("[TEST] Testing GUI initialization...")

    app = QApplication(sys.argv)

    # Create a simple test window
    window = QWidget()
    window.setWindowTitle("Teaching Assistant - GUI Test")
    layout = QVBoxLayout()

    label = QLabel("GUI Test - If you see this window, PyQt6 is working!")
    layout.addWidget(label)

    button = QPushButton("Close Test")
    button.clicked.connect(window.close)
    layout.addWidget(button)

    window.setLayout(layout)
    window.show()

    print("[SUCCESS] GUI window created successfully!")
    print("[INFO] Close the window to complete the test...")

    # Run for a short time
    app.exec()

if __name__ == "__main__":
    try:
        test_gui()
        print("[SUCCESS] GUI test completed!")
    except Exception as e:
        print(f"[ERROR] GUI test failed: {e}")
        sys.exit(1)
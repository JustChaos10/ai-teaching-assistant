import sys
import time
import pyaudio
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import QThread, pyqtSignal, QObject, QUrl
from PyQt6.QtMultimedia import QSoundEffect

from chatbot_logic import ChatbotLogic
from avatar_system import TeachingAssistantUI

# Import the FREE speech services
sys.path.insert(0, "backend")
from backend.free_speech_services import FreeSTTService, SimpleVoiceActivityDetector

def list_audio_devices():
    """Helper function to print available audio input devices."""
    print("[AUDIO] Listing available audio input devices...")
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    for i in range(0, num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if (device_info.get('maxInputChannels')) > 0:
            print(f"   - Device index {i}: {device_info.get('name')}")
    p.terminate()
    print("--------------------------------------------------")


class BackendWorker(QObject):
    state_changed = pyqtSignal(str)
    tts_audio_ready = pyqtSignal(str)

    def __init__(self, chatbot_logic: ChatbotLogic):
        super().__init__()
        self.chatbot_logic = chatbot_logic
        self.is_running = True
        self.stt_service = None
        self.vad = None
        self.waiting_for_wake_word = True

    def run(self):
        """The main STT -> LLM -> TTS pipeline loop using online services."""
        print("Backend worker running...")
        list_audio_devices()

        try:
            print("[INFO] Setting up FREE STT Service...")

            # Initialize FREE STT service
            self.stt_service = FreeSTTService()
            self.stt_service.set_callbacks(
                on_transcription=self._on_transcription,
                on_recording_start=self._on_recording_start,
                on_recording_stop=self._on_recording_stop
            )

            # Initialize Simple Voice Activity Detector
            self.vad = SimpleVoiceActivityDetector(threshold=0.01, silence_duration=2.0)
            self.vad.set_callbacks(
                on_speech_start=self._on_speech_start,
                on_speech_end=self._on_speech_end
            )

            print("[SUCCESS] FREE STT Service initialized successfully")
            self.state_changed.emit("idle")

            # Start continuous speech recognition instead of VAD
            print("[INFO] Starting continuous speech recognition...")
            self.stt_service.start_continuous_listening()

            # Keep the worker running
            while self.is_running:
                time.sleep(0.1)  # Small sleep to prevent busy waiting

        except Exception as e:
            print(f"An error occurred in the backend worker: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()
            print("Backend worker stopped.")

    def _on_speech_start(self):
        """Callback when speech is detected by VAD."""
        if self.waiting_for_wake_word:
            print("[INFO] Speech detected, checking for wake word...")
            self.state_changed.emit("listening")
            self.stt_service.start_recording()
        else:
            print("[INFO] Speech detected, starting recording...")
            self.state_changed.emit("listening")
            self.stt_service.start_recording()

    def _on_speech_end(self):
        """Callback when speech ends."""
        print("[INFO] Speech ended, processing...")
        self.stt_service.stop_recording()

    def _on_recording_start(self):
        """Callback when STT recording starts."""
        print("[STT] Recording started")

    def _on_recording_stop(self):
        """Callback when STT recording stops."""
        print("[STT] Recording stopped, transcribing...")

    def _on_transcription(self, text: str):
        """Callback when transcription is ready."""
        if not text or not self.is_running:
            self.state_changed.emit("idle")
            return

        print(f"[STT] Transcribed: '{text}'")

        # Check for wake word if waiting
        if self.waiting_for_wake_word:
            if "jarvis" in text.lower() or "hey jarvis" in text.lower():
                print("[WAKE WORD] Detected! Ready for commands.")
                self.waiting_for_wake_word = False
                self.state_changed.emit("idle")
                return
            else:
                print(f"[WAKE WORD] Not detected in '{text}', still waiting for 'Hey Jarvis'...")
                self.state_changed.emit("idle")
                return

        # Process the command
        self._process_text(text.strip())

        # Reset to wake word detection after processing command
        print("[INFO] Command processed, resetting to wake word mode...")
        self.waiting_for_wake_word = True

    def _on_wakeword_detected(self):
        """Legacy callback for compatibility."""
        print("[INFO] Wake word detected!")
        self.state_changed.emit("listening")

    def _on_vad_start(self):
        """Legacy callback for compatibility."""
        print("[INFO] Speech detected, listening...")
        self.state_changed.emit("listening")

    def _process_text(self, text):
        """Processes transcribed text to generate and play a response."""
        if not text.strip() or len(text.strip()) < 3:
            self.state_changed.emit("idle")
            return

        print(f"Transcribed Text: {text}")

        self.state_changed.emit("thinking")
        response_text = self.chatbot_logic.get_response(text)
        print(f"RAG Response: {response_text}")

        output_path = self.chatbot_logic.generate_tts(response_text)

        if output_path:
            self.state_changed.emit("speaking")
            self.tts_audio_ready.emit(output_path)
        else:
            self.state_changed.emit("idle")

    def _cleanup(self):
        """Clean up audio resources."""
        try:
            if self.stt_service:
                self.stt_service.cleanup()
            if self.vad:
                self.vad.cleanup()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def stop(self):
        """Signals the run loop to exit and aborts blocking calls."""
        print("Signaling backend worker to stop...")
        self.is_running = False
        self._cleanup()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Humanoid Teaching Assistant")
        self.layout = QVBoxLayout()

        # --- ENHANCED ANIMATED AVATAR ---
        self.teaching_assistant = TeachingAssistantUI()
        self.layout.addWidget(self.teaching_assistant)
        
        # Keep the original label as fallback
        self.humanoid_label = QLabel("Press Start to Begin")
        self.humanoid_label.hide()  # Hidden by default, show only if avatar fails
        self.layout.addWidget(self.humanoid_label)
        
        # --- ANIMATION SETUP WITH ERROR HANDLING ---
        self.setup_animations()
        
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.setLayout(self.layout)

        # --- INITIALIZE CHATBOT LOGIC ---
        # This can take a while, so we do it once when the app starts
        self.chatbot_logic = ChatbotLogic()
        
        # --- ADD AUDIO PLAYER ---
        self.audio_player = QSoundEffect()
        
        # --- CONNECTIONS ---
        self.start_button.clicked.connect(self.start_backend)
        self.stop_button.clicked.connect(self.stop_backend)
        self.audio_player.playingChanged.connect(self._on_audio_finished)

    def setup_animations(self):
        """Setup animations with fallback handling."""
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
            print("Using text-based state indicators instead")
            
            # Create fallback text-based animations
            self.listening_anim = None
            self.thinking_anim = None
            self.speaking_anim = None
            self.idle_anim = None

    def start_backend(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.backend_thread = QThread()
        # Pass the initialized chatbot logic to the worker
        self.backend_worker = BackendWorker(self.chatbot_logic)
        self.backend_worker.moveToThread(self.backend_thread)

        # Connect signals
        self.backend_worker.state_changed.connect(self.update_humanoid_state)
        self.backend_worker.tts_audio_ready.connect(self.play_audio)
        self.backend_thread.started.connect(self.backend_worker.run)
        
        self.backend_thread.start()
        self.humanoid_label.setText("Initializing speech recognition... Please wait...")

    def stop_backend(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if hasattr(self, 'backend_thread') and self.backend_thread.isRunning():
            self.backend_worker.stop() # Gracefully stop the loop
            self.backend_thread.quit()
            self.backend_thread.wait()
        self.humanoid_label.setMovie(self.idle_anim) # Reset to idle
        if self.idle_anim:
            self.idle_anim.start()
        self.humanoid_label.setText("Session Ended.")

    def update_humanoid_state(self, state):
        print(f"UI changing to state: {state}")
        
        # Update the animated avatar
        try:
            self.teaching_assistant.set_state(state)
        except Exception as e:
            print(f"Avatar update failed: {e}")
            # Fallback to original system
            self.humanoid_label.show()
            self.teaching_assistant.hide()
            
            # Handle animations if available, otherwise use text
            if self.listening_anim and self.thinking_anim and self.speaking_anim and self.idle_anim:
                # Use animations
                if state == "idle":
                    self.humanoid_label.setMovie(self.idle_anim)
                    self.idle_anim.start()
                elif state == "listening":
                    self.humanoid_label.setMovie(self.listening_anim)
                    self.listening_anim.start()
                elif state == "thinking":
                    self.humanoid_label.setMovie(self.thinking_anim)
                    self.thinking_anim.start()
                elif state == "speaking":
                    self.humanoid_label.setMovie(self.speaking_anim)
                    self.speaking_anim.start()
            else:
                # Use text-based state indicators
                if state == "idle":
                    self.humanoid_label.setText("[READY] Say 'Hey Jarvis' to wake me up!")
                elif state == "listening":
                    self.humanoid_label.setText("[LISTENING] I can hear you, keep talking...")
                elif state == "thinking":
                    self.humanoid_label.setText("[THINKING] Processing your request...")
                elif state == "speaking":
                    self.humanoid_label.setText("[SPEAKING] Playing audio response...")
            
    def play_audio(self, path: str):
        """Slot to play the generated audio file."""
        if path:
            print(f"UI playing audio: {path}")
            url = QUrl.fromLocalFile(path)
            # By adding a unique query string, we force QSoundEffect to reload the file
            # and not use a cached version.
            url.setQuery(f"v={time.time()}")
            self.audio_player.setSource(url)
            self.audio_player.play()

    def _on_audio_finished(self):
        """Callback when audio playback state changes."""
        if not self.audio_player.isPlaying():
            print("Audio finished, returning to idle state.")
            self.update_humanoid_state("idle")

# The main execution block remains the same
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
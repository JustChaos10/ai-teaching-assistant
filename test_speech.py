"""
Test speech recognition functionality
"""

import sys
import time
sys.path.insert(0, "backend")

from backend.free_speech_services import FreeSTTService

def test_speech_recognition():
    """Test continuous speech recognition"""
    print("=" * 50)
    print("SPEECH RECOGNITION TEST")
    print("=" * 50)

    def on_transcription(text):
        print(f"[HEARD] {text}")
        if "jarvis" in text.lower():
            print("[WAKE WORD DETECTED!] Jarvis wake word found!")
        if "hello" in text.lower():
            print("[TEST PASSED] Hello detected!")

    def on_recording_start():
        print("[RECORDING] Started listening...")

    def on_recording_stop():
        print("[RECORDING] Stopped listening...")

    try:
        print("[INIT] Initializing speech recognition...")
        stt = FreeSTTService()

        print("[SETUP] Setting up callbacks...")
        stt.set_callbacks(
            on_transcription=on_transcription,
            on_recording_start=on_recording_start,
            on_recording_stop=on_recording_stop
        )

        print("[START] Starting continuous listening...")
        print("=" * 50)
        print("INSTRUCTIONS:")
        print("1. Say 'Hey Jarvis' to test wake word detection")
        print("2. Say 'Hello' to test basic recognition")
        print("3. Say anything else to test general recognition")
        print("4. The test will run for 30 seconds")
        print("=" * 50)

        stt.start_continuous_listening()

        # Run for 30 seconds
        for i in range(30):
            print(f"[TIME] {30-i} seconds remaining...")
            time.sleep(1)

        print("[STOP] Stopping speech recognition...")
        stt.cleanup()

        print("[COMPLETE] Speech recognition test completed!")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

if __name__ == "__main__":
    test_speech_recognition()
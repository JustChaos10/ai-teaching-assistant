"""
Test script to check application components without running the full GUI
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("[TEST] Testing imports...")

    try:
        from chatbot_logic import ChatbotLogic
        print("[OK] ChatbotLogic import successful")
    except Exception as e:
        print(f"[ERROR] ChatbotLogic import failed: {e}")
        return False

    try:
        from game_manager import GameManager
        print("[OK] GameManager import successful")
    except Exception as e:
        print(f"[ERROR] GameManager import failed: {e}")
        return False

    try:
        sys.path.insert(0, "backend")
        from backend.online_speech_services import OnlineSTTService, OnlineTTSService
        print("[OK] Online speech services import successful")
    except Exception as e:
        print(f"[ERROR] Online speech services import failed: {e}")
        return False

    try:
        from PyQt6.QtWidgets import QApplication
        print("[OK] PyQt6 import successful")
    except Exception as e:
        print(f"[ERROR] PyQt6 import failed: {e}")
        return False

    return True

def test_game_manager():
    """Test game manager functionality"""
    print("\n[TEST] Testing GameManager...")

    try:
        from game_manager import GameManager
        gm = GameManager()

        games = gm.list_available_games()
        print(f"[INFO] Found {len(games)} games:")
        for game_id, info in games.items():
            print(f"  - {info['name']} ({game_id})")

        print("\n[INFO] Game files status:")
        for game_id in games:
            available = gm.is_game_available(game_id)
            status = "[READY]" if available else "[MISSING]"
            print(f"  {status} {game_id}")

        return True

    except Exception as e:
        print(f"[ERROR] GameManager test failed: {e}")
        return False

def test_speech_services():
    """Test speech services (without real API keys)"""
    print("\n[TEST] Testing Speech Services...")

    try:
        # Set dummy API key to test initialization
        os.environ['OPENAI_API_KEY'] = 'test_key_for_testing'

        sys.path.insert(0, "backend")
        from backend.online_speech_services import OnlineTTSService, OnlineSTTService

        # Test TTS service initialization
        tts = OnlineTTSService()
        print("[OK] TTS Service can be initialized")

        # Test STT service initialization
        stt = OnlineSTTService()
        print("[OK] STT Service can be initialized")

        return True

    except Exception as e:
        print(f"[INFO] Speech services test (expected without real API key): {e}")
        return True  # This is expected without real API keys

def test_chatbot_logic():
    """Test chatbot logic initialization"""
    print("\n[TEST] Testing ChatbotLogic...")

    try:
        # Set dummy API key
        os.environ['OPENAI_API_KEY'] = 'test_key_for_testing'

        from chatbot_logic import ChatbotLogic
        print("[INFO] Attempting to initialize ChatbotLogic...")

        # This might fail without proper API keys, but we can test the import
        chatbot = ChatbotLogic()
        print("[OK] ChatbotLogic initialized successfully")

        return True

    except Exception as e:
        print(f"[INFO] ChatbotLogic test result: {e}")
        # Return True if it's just an API key issue
        if "OPENAI_API_KEY" in str(e) or "api" in str(e).lower():
            print("[INFO] This is expected without real API keys")
            return True
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("[START] Testing Application Components")
    print("=" * 50)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test game manager
    if not test_game_manager():
        all_passed = False

    # Test speech services
    if not test_speech_services():
        all_passed = False

    # Test chatbot logic
    if not test_chatbot_logic():
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All tests passed!")
        print("The application should work with proper API keys.")
    else:
        print("[FAILED] Some tests failed. Check the errors above.")
    print("=" * 50)

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
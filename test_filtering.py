"""
Test speech recognition filtering
"""

import sys
sys.path.insert(0, "backend")

from backend.free_speech_services import FreeSTTService

def test_text_filtering():
    """Test the text filtering functionality"""
    print("=" * 50)
    print("TESTING SPEECH RECOGNITION FILTERING")
    print("=" * 50)

    stt = FreeSTTService()

    # Test cases - what should be accepted vs rejected
    test_cases = [
        # Valid inputs (should be accepted)
        ("hey jarvis", True, "Wake word"),
        ("jarvis", True, "Wake word short"),
        ("let's play a game", True, "Game request"),
        ("launch finger game", True, "Game command"),
        ("start healthy game", True, "Game command"),
        ("show games", True, "Game command"),
        ("hello jarvis", True, "Greeting with wake word"),

        # Invalid inputs (should be rejected)
        ("uh", False, "Single noise word"),
        ("um", False, "Single noise word"),
        ("a", False, "Single article"),
        ("the", False, "Single article"),
        ("", False, "Empty string"),
        ("12345", False, "Numbers only"),
        ("what when where why how who and or but", False, "Only noise words"),
        ("a" * 150, False, "Too long gibberish"),
        ("123abc456def789", False, "Too many numbers"),
    ]

    passed = 0
    total = len(test_cases)

    for text, should_pass, description in test_cases:
        result = stt._is_valid_transcription(text)
        status = "PASS" if result == should_pass else "FAIL"
        expected = "ACCEPT" if should_pass else "REJECT"
        actual = "ACCEPTED" if result else "REJECTED"

        print(f"[{status}] '{text}' -> {actual} (expected {expected}) - {description}")

        if result == should_pass:
            passed += 1

    print("=" * 50)
    print(f"FILTERING TEST RESULTS: {passed}/{total} passed")
    print("=" * 50)

    if passed == total:
        print("[SUCCESS] All filtering tests passed!")
        return True
    else:
        print(f"[WARNING] {total - passed} tests failed")
        return False

if __name__ == "__main__":
    test_text_filtering()
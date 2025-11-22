#!/usr/bin/env python3
"""
Simple standalone test for Tamil detection logic
"""

def is_tamil_text(text: str) -> bool:
    """
    Detect if the text contains Tamil characters.
    Tamil Unicode range: U+0B80 to U+0BFF
    Returns True if more than 30% of characters are Tamil.
    """
    if not text:
        return False

    tamil_char_count = 0
    total_chars = 0

    for char in text:
        # Skip whitespace and common punctuation
        if char.isspace() or char in ".,!?;:":
            continue

        total_chars += 1
        # Check if character is in Tamil Unicode range
        if '\u0B80' <= char <= '\u0BFF':
            tamil_char_count += 1

    if total_chars == 0:
        return False

    # If more than 30% of non-whitespace characters are Tamil, consider it Tamil text
    tamil_percentage = tamil_char_count / total_chars
    return tamil_percentage > 0.3


def test_tamil_detection():
    """Test Tamil text detection"""
    print("=== Tamil Detection Test ===\n")

    # Test cases
    test_cases = [
        ("What is 2 + 2?", False, "English math question"),
        ("5 + 3 என்றால் என்ன?", True, "Tamil math question"),
        ("இரண்டு கூட்டல் மூன்று?", True, "Tamil addition question"),
        ("Hello, how are you?", False, "English greeting"),
        ("வணக்கம்", True, "Tamil greeting"),
        ("Tell me about trees", False, "English general question"),
        ("மரங்கள் பற்றி சொல்லுங்கள்", True, "Tamil general question"),
        ("மரம் பழங்களை பகிர்ந்து கொள்கிறது", True, "Tamil about trees sharing fruits"),
        ("123 + 456", False, "Numbers only"),
        ("The tree shares its fruits", False, "English about trees"),
    ]

    print("Testing Tamil detection:\n")
    all_passed = True

    for text, expected_tamil, description in test_cases:
        is_tamil = is_tamil_text(text)
        status = "✓ PASS" if is_tamil == expected_tamil else "✗ FAIL"

        if is_tamil != expected_tamil:
            all_passed = False

        # Calculate actual percentage for debugging
        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        total = sum(1 for c in text if not c.isspace() and c not in ".,!?;:")
        pct = (tamil_chars / total * 100) if total > 0 else 0

        print(f"{status} | {description}")
        print(f"  Text: '{text}'")
        print(f"  Tamil chars: {tamil_chars}/{total} ({pct:.1f}%)")
        print(f"  Expected Tamil: {expected_tamil}, Got: {is_tamil}")
        print()

    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nThe Tamil detection is working correctly!")
        print("When you ask Tamil questions, RAG will be bypassed and")
        print("the LLM will answer directly without irrelevant English context.")
    else:
        print("✗ SOME TESTS FAILED!")
    print("="*60)


if __name__ == "__main__":
    test_tamil_detection()

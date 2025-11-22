#!/usr/bin/env python3
"""
Quick test script to verify Tamil language detection is working
"""

import sys
sys.path.append('/home/user/ai-teaching-assistant')

from backend.rag_system import RAGSystem

def test_tamil_detection():
    """Test Tamil text detection"""
    print("=== Tamil Detection Test ===\n")

    # Initialize RAG system
    rag = RAGSystem()

    # Test cases
    test_cases = [
        ("What is 2 + 2?", False, "English math question"),
        ("5 + 3 என்றால் என்ன?", True, "Tamil math question"),
        ("இரண்டு கூட்டல் மூன்று?", True, "Tamil addition question"),
        ("Hello, how are you?", False, "English greeting"),
        ("வணக்கம்", True, "Tamil greeting"),
        ("Tell me about trees", False, "English general question"),
        ("மரங்கள் பற்றி சொல்லுங்கள்", True, "Tamil general question"),
        ("123 + 456", False, "Numbers only"),
    ]

    print("Testing Tamil detection:\n")
    all_passed = True

    for text, expected_tamil, description in test_cases:
        is_tamil = rag.is_tamil_text(text)
        status = "✓ PASS" if is_tamil == expected_tamil else "✗ FAIL"

        if is_tamil != expected_tamil:
            all_passed = False

        print(f"{status} | {description}")
        print(f"  Text: '{text}'")
        print(f"  Expected Tamil: {expected_tamil}, Got: {is_tamil}")
        print()

    print("\n=== RAG Usage Test ===\n")
    print("Testing should_use_rag() with Tamil questions:\n")

    rag_test_cases = [
        ("What is 2 + 2?", True, "English question should use RAG (if docs available)"),
        ("5 + 3 என்றால் என்ன?", False, "Tamil question should NOT use RAG"),
    ]

    for text, expected_rag, description in rag_test_cases:
        should_use = rag.should_use_rag(text)

        # For English questions, it depends on whether vector store exists
        # For Tamil, it should ALWAYS be False
        if rag.is_tamil_text(text):
            status = "✓ PASS" if not should_use else "✗ FAIL"
            if should_use:
                all_passed = False
            print(f"{status} | {description}")
            print(f"  Text: '{text}'")
            print(f"  Should use RAG: {should_use} (expected: False for Tamil)")
        else:
            print(f"INFO | {description}")
            print(f"  Text: '{text}'")
            print(f"  Should use RAG: {should_use} (depends on vector store)")
        print()

    print("\n" + "="*50)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
    else:
        print("✗ SOME TESTS FAILED!")
    print("="*50)

if __name__ == "__main__":
    test_tamil_detection()

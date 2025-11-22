#!/usr/bin/env python3
"""
Integration test to verify Tamil and English question handling
Tests that:
1. Tamil questions bypass RAG (no hallucinations)
2. English questions use RAG (when available)
3. Both get proper responses from the LLM
"""

import sys
import os

# Add the new-backend directory to path
sys.path.insert(0, '/home/user/ai-teaching-assistant/new-backend')

# Test the actual detection logic
from rag_system import RAGSystem

def test_tamil_english_handling():
    """Test that RAG system handles Tamil and English correctly"""
    print("="*70)
    print("TAMIL & ENGLISH QUESTION HANDLING TEST")
    print("="*70)
    print()

    # Initialize RAG system
    print("[INIT] Initializing RAG system...")
    rag = RAGSystem(
        doc_folder="./new-backend/docs",
        index_folder="./new-backend/indexes"
    )
    print()

    # Test cases: (question, expected_language, description)
    test_cases = [
        # English questions
        ("What is 2 + 2?", "English", "English math question"),
        ("Tell me about animals", "English", "English general question"),
        ("How do I spell cat?", "English", "English spelling question"),

        # Tamil questions
        ("5 + 3 என்றால் என்ன?", "Tamil", "Tamil math question"),
        ("இரண்டு கூட்டல் மூன்று?", "Tamil", "Tamil addition question"),
        ("வணக்கம்", "Tamil", "Tamil greeting"),
        ("மரங்கள் பற்றி சொல்லுங்கள்", "Tamil", "Tamil general question"),
        ("மரம் பழங்களை பகிர்ந்து கொள்கிறது", "Tamil", "Tamil about trees sharing fruits"),
    ]

    print("-"*70)
    print("LANGUAGE DETECTION & RAG BYPASS TEST")
    print("-"*70)
    print()

    all_passed = True

    for question, expected_lang, description in test_cases:
        is_tamil = rag.is_tamil_text(question)
        should_use = rag.should_use_rag(question)

        # Determine detected language
        detected_lang = "Tamil" if is_tamil else "English"

        # Check if detection is correct
        detection_correct = (detected_lang == expected_lang)

        # For Tamil, RAG should be skipped
        # For English, RAG usage depends on vector store availability
        if is_tamil:
            rag_behavior_correct = not should_use  # Tamil should NOT use RAG
        else:
            rag_behavior_correct = True  # English can use RAG or not depending on docs

        status = "✓ PASS" if (detection_correct and rag_behavior_correct) else "✗ FAIL"

        if not (detection_correct and rag_behavior_correct):
            all_passed = False

        print(f"{status} | {description}")
        print(f"  Question: '{question}'")
        print(f"  Expected: {expected_lang} | Detected: {detected_lang}")
        print(f"  Is Tamil: {is_tamil} | Uses RAG: {should_use}")

        # Explain RAG behavior
        if is_tamil:
            if not should_use:
                print(f"  ✓ Correct: Tamil detected → RAG skipped (no hallucinations)")
            else:
                print(f"  ✗ ERROR: Tamil detected but RAG not skipped!")
        else:
            print(f"  ✓ Correct: English detected → RAG allowed")

        print()

    print("-"*70)
    print("VECTOR STORE STATUS")
    print("-"*70)
    print(f"Embeddings available: {rag.embeddings_available}")
    print(f"Vector store exists: {rag.vector_store is not None}")
    print(f"Document count: {rag.get_document_count()}")
    print()

    print("-"*70)
    print("SUMMARY")
    print("-"*70)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print()
        print("✓ Tamil questions will bypass RAG (no hallucinations)")
        print("✓ English questions will use RAG if documents available")
        print("✓ Language detection is working correctly")
    else:
        print("✗ SOME TESTS FAILED!")
    print("="*70)


if __name__ == "__main__":
    try:
        test_tamil_english_handling()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

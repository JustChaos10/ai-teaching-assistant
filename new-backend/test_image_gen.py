"""
Quick test script for Pollinations.ai image generation
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

print("=" * 60)
print("Testing Pollinations.ai Image Generation (Free, No Auth)")
print("=" * 60)

print(f"\n✓ GROQ_API_KEY present: {bool(GROQ_API_KEY)}")
print("✓ Pollinations.ai: No API key required!")

if not GROQ_API_KEY:
    print("\n❌ Missing GROQ_API_KEY! Check your .env file")
    exit(1)

# Import and test
from image_generator import ImageGenerator

print("\n" + "=" * 60)
print("Initializing Image Generator...")
print("=" * 60)

try:
    generator = ImageGenerator(
        groq_api_key=GROQ_API_KEY,
        output_dir="static/generated_images"
    )
    print("✅ Image generator initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    exit(1)

# Test prompt analysis
print("\n" + "=" * 60)
print("Testing Groq Prompt Analysis...")
print("=" * 60)

test_content = """
Let's learn about addition with apples. 
If we have 2 apples and we get 3 more apples, how many apples do we have in total?
We start with 2 apples, then add 3 more. 2 + 3 = 5 apples!
"""

try:
    prompts = generator.analyze_teaching_content(test_content)
    print(f"✅ Generated {len(prompts)} image prompts:")
    for i, p in enumerate(prompts, 1):
        print(f"\n  {i}. {p.get('description', 'N/A')}")
        print(f"     Prompt: {p.get('prompt', 'N/A')[:80]}...")
except Exception as e:
    print(f"❌ Prompt analysis failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test image generation with first prompt
print("\n" + "=" * 60)
print("Testing Pollinations.ai Image Generation...")
print("=" * 60)

if prompts:
    test_prompt = prompts[0].get('prompt', 'A red apple on white background')
    print(f"\nGenerating image with prompt: {test_prompt[:100]}...")
    
    try:
        image_path = generator.generate_image_pollinations(test_prompt)
        
        if image_path:
            print(f"\n✅ SUCCESS! Image saved to: {image_path}")
            print(f"✅ File exists: {Path(image_path).exists()}")
            print(f"✅ File size: {Path(image_path).stat().st_size} bytes")
            print("\n🎉 Pollinations.ai is working perfectly!")
        else:
            print("\n❌ Image generation returned None")
            
    except Exception as e:
        print(f"\n❌ Image generation failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ No prompts to test with")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)

import os
import time
import json
from pathlib import Path
from groq import Groq
from huggingface_hub import InferenceClient

class ImageGenerator:
    """
    Image generation system that:
    1. Takes RAG output
    2. Uses Groq LLM to analyze and create image prompts with timing
    3. Generates images via Hugging Face FLUX Schnell model
    4. Saves images locally
    5. Returns image URLs with timing information
    """
    
    def __init__(self, groq_api_key, huggingface_api_key, output_dir="./static/generated_images"):
        self.groq_client = Groq(api_key=groq_api_key)
        self.hf_client = InferenceClient(api_key=huggingface_api_key)
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[Image Generator] Initialized with FLUX Schnell (Hugging Face)")
        print(f"[Image Generator] API Key present: {bool(huggingface_api_key)}")
        
    def analyze_teaching_content(self, ai_response):
        """
        Use Groq LLM to analyze the teaching content and generate well detailed image prompts with timing. these images are being used to teach the children so mush be helpful in understanding. typically tacking numbers.
        
        Args:
            ai_response (str): The answer from RAG system
            
        Returns:
            list: List of image prompt dictionaries with duration
        """
        
        prompt = f"""You are an educational image prompt generator for young students (grade 1-2).

Analyze this teaching content:

"{ai_response}"

Your task:
1. Count total words in the text: {len(ai_response.split())} words
2. Estimate total speaking time at 2.5 words/second: {len(ai_response.split()) / 2.5:.1f} seconds
3. Divide the explanation into segments where different images should show
4. For each segment, calculate:
   - Duration (in seconds) the image should display
   - Image prompt describing what to show

Example for "Let's count! We have 2 apples here. Now we add 3 oranges. Together we have 5 fruits total!" (20 words ≈ 8 seconds):

[
  {{
    "description": "2 apples",
    "prompt": "2 red apples on white background, simple illustration, child-friendly, educational style",
    "duration": 2.5
  }},
  {{
    "description": "3 oranges",
    "prompt": "3 orange fruits on white background, simple illustration, child-friendly, educational style",
    "duration": 2.5
  }},
  {{
    "description": "5 fruits total",
    "prompt": "2 apples and 3 oranges together, simple illustration, child-friendly, educational style",
    "duration": 3.0
  }}
]

Rules:
- Max 7 images
- Duration should be in seconds (decimal)
- Sum of all durations should approximately equal total speaking time
- Each image should cover a distinct concept/step
- Make sure durations align with how long each concept is discussed

Return ONLY valid JSON array with fields: description, prompt, duration
If no images needed, return []

Return ONLY valid JSON, no other text:"""

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates image prompts with timing for educational content. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            # Try to extract JSON if there's extra text
            if response_text.startswith('['):
                prompts = json.loads(response_text)
            else:
                # Try to find JSON array in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    prompts = json.loads(json_str)
                else:
                    prompts = []
            
            print(f"[Image Generator] Generated {len(prompts)} image prompts")
            return prompts
            
        except Exception as e:
            print(f"[Image Generator] Error analyzing content: {e}")
            return []
    
    def generate_image_huggingface(self, prompt):
        """
        Generate image using FLUX Schnell via Hugging Face Inference API.
        Fast, high-quality image generation.
        
        Args:
            prompt (str): Text prompt for image generation
            
        Returns:
            str: Path to saved image or None
        """
        try:
            print(f"[Image Generator] Calling FLUX Schnell with prompt: {prompt[:50]}...")
            
            # Generate image using Hugging Face
            image = self.hf_client.text_to_image(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell"
            )
            
            # Save image
            import uuid
            filename = f"edu_{uuid.uuid4().hex[:8]}.png"
            filepath = self.output_dir / filename
            
            image.save(str(filepath))
            
            print(f"[Image Generator] ✅ Image saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"[Image Generator] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_images_for_teaching(self, ai_response):
        """
        Complete pipeline: analyze content → generate prompts → create images with LLM-calculated timing.
        
        Args:
            ai_response (str): Teaching content from RAG system
            
        Returns:
            list: List of image paths with timing info
        """
        # Step 1: Analyze content and get prompts with LLM-calculated durations
        prompts = self.analyze_teaching_content(ai_response)
        
        if not prompts:
            print("[Image Generator] No images needed for this content")
            return []
        
        # Step 2: Calculate start times based on durations
        current_time = 0
        image_paths = []
        
        for idx, prompt_obj in enumerate(prompts):
            prompt = prompt_obj.get("prompt", "")
            description = prompt_obj.get("description", f"Step {idx + 1}")
            duration = prompt_obj.get("duration", 3.0)  # Default 3 seconds
            
            start_time = current_time
            end_time = start_time + duration
            
            print(f"[Image Generator] Image {idx + 1}: '{description}'")
            print(f"[Image Generator]   Time: {start_time:.1f}s → {end_time:.1f}s (duration: {duration:.1f}s)")
            
            image_path = self.generate_image_huggingface(prompt)
            
            if image_path:
                image_paths.append({
                    "path": image_path,
                    "description": description,
                    "prompt": prompt,
                    "step": idx + 1,
                    "start_time": round(start_time, 2),
                    "end_time": round(end_time, 2),
                    "duration": round(duration, 2)
                })
            
            # Move to next time slot
            current_time = end_time
        
        total_duration = current_time
        print(f"[Image Generator] Successfully generated {len(image_paths)}/{len(prompts)} images")
        print(f"[Image Generator] Total slideshow duration: {total_duration:.1f}s")
        return image_paths

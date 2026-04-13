
import asyncio
import os
import sys
import base64
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.services.dalle_service import generate_image_gemini
from dotenv import load_dotenv

load_dotenv()

# Set the correct model for image generation
os.environ["GEMINI_IMAGE_MODEL"] = "gemini-2.5-flash-image"

# Unified Theme: Glassmorphism 3D Isometric, soft studio lighting, vibrant gradient accents, clean dark background
THEME = "3D isometric render, glassmorphism style, translucent glass textures, vibrant neon accents, soft studio lighting, high-quality digital art, clean composition, minimalist aesthetic, 4k resolution."

FEATURES = [
    {
        "id": "onuitube",
        "prompt": f"A cinematic video play icon floating over a translucent glass tablet, pink and violet glowing edges, {THEME}",
        "filename": "feature_onuitube.png"
    },
    {
        "id": "onuibeats",
        "prompt": f"A stylish glowing musical note and a glass vinyl record, electric blue and purple neon lights, {THEME}",
        "filename": "feature_onuibeats.png"
    },
    {
        "id": "voicecall",
        "prompt": f"A sleek glass smartphone showing a friendly holographic AI face and sound wave ripples, orange and amber glow, {THEME}",
        "filename": "feature_voicecall.png"
    },
    {
        "id": "messenger",
        "prompt": f"Translucent glass chat bubbles with glowing teal icons and floating digital particles, mint green accents, {THEME}",
        "filename": "feature_messenger.png"
    },
    {
        "id": "roleplay",
        "prompt": f"A miniature isometric glass stage with two stylized floating character avatars, green and lime glowing aura, {THEME}",
        "filename": "feature_roleplay.png"
    },
    {
        "id": "textbook",
        "prompt": f"An open floating book made of frosted glass with digital data streams and an AI brain icon, indigo and deep blue glow, {THEME}",
        "filename": "feature_textbook.png"
    },
    {
        "id": "precision",
        "prompt": f"A high-tech glass circular target analyzing a 3D sound wave, magenta and hot pink neon highlights, {THEME}",
        "filename": "feature_precision.png"
    },
    {
        "id": "daily",
        "prompt": f"A glowing golden glass calendar card with a magical sparkle icon, soft yellow and sunburst orange accents, {THEME}",
        "filename": "feature_daily.png"
    },
    {
        "id": "reports",
        "prompt": f"A 3D bar chart made of crystalline glass with a rising arrow and a trophy, red and sunset orange glow, {THEME}",
        "filename": "feature_reports.png"
    }
]

async def generate_all():
    target_dir = Path("static/images/landing")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting image generation for {len(FEATURES)} features using {os.environ['GEMINI_IMAGE_MODEL']}...")
    
    for feature in FEATURES:
        print(f"Generating for {feature['id']}...")
        try:
            result = await generate_image_gemini(
                prompt=feature["prompt"],
                save_locally=False
            )
            
            if result["success"]:
                image_data = base64.b64decode(result["image_base64"])
                filepath = target_dir / feature["filename"]
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                print(f"  [SUCCESS] Saved to {filepath}")
            else:
                print(f"  [ERROR] Generation failed: {result.get('error')}")
                
        except Exception as e:
            print(f"  [EXCEPTION] {e}")
            
    print("Generation process completed.")

if __name__ == "__main__":
    asyncio.run(generate_all())

#!/usr/bin/env python3
"""
Connection Test Script - Verifies authentication for Gemini 2.5 Flash and Imagen 4 Fast.

This script tests that the Google Cloud service account credentials are properly
configured and can authenticate with both the Gemini API and Imagen API.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Set credentials path (resolve relative path to absolute)
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if creds_path and not os.path.isabs(creds_path):
    creds_path = str(Path(__file__).parent.parent / creds_path)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

def get_project_id():
    """Extract project ID from service account credentials."""
    creds_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_file and os.path.exists(creds_file):
        with open(creds_file) as f:
            return json.load(f).get("project_id")
    return None

def test_gemini_connection():
    """Test connection to Gemini 2.5 Flash."""
    print("\n" + "=" * 60)
    print("🧠 Testing Gemini 2.5 Flash Connection")
    print("=" * 60)
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        project_id = get_project_id()
        if not project_id:
            print("❌ FAILED: Could not extract project_id from credentials")
            return False
        
        print(f"   Project ID: {project_id}")
        print(f"   Model: gemini-2.5-flash")
        print(f"   Location: us-central1")
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location="us-central1")
        
        # Load the model
        model = GenerativeModel("gemini-2.5-flash")
        
        # Test with a simple prompt
        print("\n   📤 Sending test prompt...")
        response = model.generate_content("Say 'Connection successful!' in exactly 3 words.")
        
        print(f"   📥 Response: {response.text.strip()}")
        print("\n✅ Gemini 2.5 Flash: CONNECTION SUCCESSFUL")
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini 2.5 Flash: CONNECTION FAILED")
        print(f"   Error: {type(e).__name__}: {e}")
        return False

def test_imagen_connection():
    """Test connection to Imagen 4 Fast."""
    print("\n" + "=" * 60)
    print("🎨 Testing Imagen 4 Fast Connection")
    print("=" * 60)
    
    try:
        import vertexai
        from vertexai.preview.vision_models import ImageGenerationModel
        
        project_id = get_project_id()
        if not project_id:
            print("❌ FAILED: Could not extract project_id from credentials")
            return False
        
        print(f"   Project ID: {project_id}")
        print(f"   Model: imagen-4.0-fast-generate-001")
        print(f"   Location: us-central1")
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location="us-central1")
        
        # Load the Imagen model
        model = ImageGenerationModel.from_pretrained("imagen-4.0-fast-generate-001")
        
        print("\n   📤 Sending test generation request (1x1 pixel test)...")
        
        # Generate a minimal test image
        images = model.generate_images(
            prompt="A single red pixel on white background",
            number_of_images=1,
            aspect_ratio="1:1",
        )
        
        if images:
            # Count images by iterating
            image_count = sum(1 for _ in images.images) if hasattr(images, 'images') else 1
            print(f"   📥 Generated {image_count} image(s)")
            print("\n✅ Imagen 4 Fast: CONNECTION SUCCESSFUL")
            return True
        else:
            print("\n❌ Imagen 4 Fast: No images returned")
            return False
        
    except Exception as e:
        print(f"\n❌ Imagen 4 Fast: CONNECTION FAILED")
        print(f"   Error: {type(e).__name__}: {e}")
        return False

def main():
    """Run all connection tests."""
    print("\n" + "🔥" * 30)
    print("   GOOGLE CLOUD CONNECTION TEST")
    print("🔥" * 30)
    
    # Check credentials
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds:
        print("\n❌ GOOGLE_APPLICATION_CREDENTIALS not set!")
        return
    
    if not os.path.exists(creds):
        print(f"\n❌ Credentials file not found: {creds}")
        return
    
    print(f"\n📁 Credentials: {creds}")
    print(f"📍 Project ID: {get_project_id()}")
    
    # Run tests
    gemini_ok = test_gemini_connection()
    imagen_ok = test_imagen_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"   Gemini 2.5 Flash: {'✅ OK' if gemini_ok else '❌ FAILED'}")
    print(f"   Imagen 4 Fast:    {'✅ OK' if imagen_ok else '❌ FAILED'}")
    print("=" * 60)
    
    if gemini_ok and imagen_ok:
        print("\n🎉 All connection tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()

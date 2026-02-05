import asyncio
import os
import io
import requests
from PIL import Image
from ai_models.ocrflux_client import OCRFluxClient

# Mock Config class
class Config:
    def __init__(self):
        self.api_key = None
        self.local_url = None

async def test_connection():
    print("🚀 Testing OCRFlux Connection...")
    
    # Load env vars safely since we aren't in main app loop
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env.local")
    
    url = os.getenv("OCRFLUX_URL")
    print(f"🌐 URL: {url}")
    
    if not url:
        print("❌ Error: OCRFLUX_URL not found in .env.local")
        return

    client = OCRFluxClient(Config())
    
    # Create a tiny dummy image
    img = Image.new('RGB', (100, 30), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    print("📡 Checking available models...")
    # Clean URL (remove path)
    base_url = url.split("/v1/")[0]
    try:
        models_resp = requests.get(f"{base_url}/v1/models")
        print(f"   Models Status: {models_resp.status_code}")
        print(f"   Models List: {models_resp.text}")
    except Exception as e:
        print(f"   Failed to list models: {e}")

    print("📡 Sending test request...")
    result = await client._call_vision_api(img_bytes)
    
    if result:
        print("✅ SUCCESS! API Responded:")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Text Length: {len(result.get('text', ''))}")
        print(f"   Snippet: {result.get('text', '')[:50]}...")
    else:
        print("❌ FAILURE: API returned None or Error.")
        print("   This likely means the model file in Colab is corrupted (due to ^C).")
        print("   Solution: In Colab, run '!rm -rf /content/models/ocrflux.gguf' and re-run Cell 3.")

if __name__ == "__main__":
    asyncio.run(test_connection())

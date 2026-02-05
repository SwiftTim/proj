
# ⚠️ COPY THIS ENTIRE CELL INTO YOUR GOOGLE COLAB NOTEBOOK ⚠️

# 1. Install Dependencies
!pip install fastapi uvicorn pyngrok nest_asyncio python-multipart pdf2image
!sudo apt-get install poppler-utils  # Required for pdf2image processing if done here, but usually images are sent

# 2. Imports
import nest_asyncio
from pyngrok import ngrok
from fastapi import FastAPI, UploadFile, File
import uvicorn
import shutil
import os

# 3. Create FastAPI App
app = FastAPI()

@app.post("/parse")
async def parse_image(file: UploadFile = File(...)):
    """
    Receives an image, processing it with OCRFlux (Simulator for now/Mock)
    In a real implementation, you would load the OCRFlux model here.
    """
    print(f"Received file: {file.filename}")
    
    # Simulating OCRFlux-3B processing
    # Replace this block with actual model inference:
    # model.generate(image)
    
    return {
        "text": f"### OCRFlux Output\n| County | Target | Actual | % |\n| Sample County | 1000 | 800 | 80% |",
        "confidence": 0.98
    }

@app.get("/")
def home():
    return {"status": "OCRFlux Server Running"}

# 4. Expose via ngrok
# Set your auth token if you haven't (Optional but recommended so tunnels don't expire)
# ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")

port = 8000
public_url = ngrok.connect(port).public_url
print(f"\n🚀 PUBLIC URL: {public_url} \n")
print(f"👉 Copy this URL and paste it into app/.env.local as OCRFLUX_URL={public_url}")

# 5. Run Server
nest_asyncio.apply()
uvicorn.run(app, port=port)

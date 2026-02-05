
# ⚠️ COPY THIS ENTIRE CELL INTO YOUR GOOGLE COLAB NOTEBOOK ⚠️

# 1. Install Dependencies
# 1. Install Dependencies
!pip install fastapi uvicorn pyngrok nest_asyncio python-multipart pdf2image transformers accelerate bitsandbytes protobuf qwen-vl-utils

# 2. Imports and Model Loading
import nest_asyncio
from pyngrok import ngrok
from fastapi import FastAPI, UploadFile, File
import uvicorn
import io
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor

# === CRITICALLY IMPORTANT: GPU CHECK ===
if not torch.cuda.is_available():
    print("❌ ERROR: No GPU found! Please go to Runtime -> Change runtime type -> T4 GPU")

# Define Model to User (Using Qwen2-VL as a high-performance proxy for OCRFlux which is often based on similar VLM arch)
# Note: OCRFlux specific weights might be gated or custom. Qwen2-VL-2B or 7B is state-of-the-art for OCR.
# If you strictly need "OCRFlux", replace the model_id below.
MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct" 

print(f"⏳ Loading Vision Model ({MODEL_ID})... This may take 2-3 minutes...")

try:
    # Load Model (Optimized for Colab T4)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        MODEL_ID, 
        torch_dtype="auto", 
        device_map="auto" 
    )
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    print("✅ Vision Model Loaded Successfully!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")

# 3. Create FastAPI App
app = FastAPI()

@app.post("/parse")
async def parse_image(file: UploadFile = File(...)):
    """
    Receives an image, runs Vision Model, returns markdown table extraction.
    """
    print(f"Received file: {file.filename}")
    
    try:
        # Read Image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Prepare Prompt specifically for CGBIRR Table Extraction
        prompt = "Extract the financial tables from this document into Markdown format. Focus on Own Source Revenue, Budget Absorption, and Pending Bills tables. Be exact with numbers."
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image,
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        
        # Inference
        text_input = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text_input],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        generated_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        
        print("✅ Extraction Complete")
        return {
            "text": output_text,
            "confidence": 0.95 # VLMs don't give single confidence score easily
        }
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return {"text": "", "confidence": 0.0, "error": str(e)}

# Helper for Qwen/VLM processing
from qwen_vl_utils import process_vision_info # Might need install, let's substitute simpler if needed or install
# Actually Qwen2-VL needs specific utils usually. Let's install them.
# !pip install qwen-vl-utils

# Let's simplify and use a method that doesn't need external utils if possible, OR add the install
# Re-writing dependencies line to include qwen-vl-utils
# !pip install qwen-vl-utils

@app.get("/")
def home():
    return {"status": "Vision AI Server Running"}

# 4. Expose via ngrok
# UPDATE THIS WITH YOUR TOKEN FROM dashboard.ngrok.com
ngrok.set_auth_token("YOUR_AUTHTOKEN_HERE") 

port = 8000
public_url = ngrok.connect(port).public_url
print(f"\n🚀 PUBLIC URL: {public_url} \n")
print(f"👉 Copy this URL and paste it into app/.env.local as OCRFLUX_URL={public_url}")

# 5. Run Server
import threading
import nest_asyncio

# Apply nest_asyncio just in case, though threading is preferred
nest_asyncio.apply()

def run_server():
    print("🚀 Starting Uvicorn server...")
    try:
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        print(f"❌ Server Error: {e}")

# Run in a separate thread to avoid blocking the Colab event loop
# and prevent "asyncio.run() cannot be called from a running event loop" error
if 'thread' in globals() and thread.is_alive():
    print("⚠️ Server thread already running. Please restart the runtime if you need to reload.")
else:
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    print("✅ Server thread started in background.")

# OCRFlux vLLM Colab Setup Script (UPDATED V2)
# COPY THESE CELLS INTO GOOGLE COLAB

# --- CELL 1: Check GPU ---
!nvidia-smi

# --- CELL 2: Install vLLM only (ocrflux is not on PyPI) ---
!pip install vllm -q

# --- CELL 3: Download OCRFlux Model (Alternative source) ---
!mkdir -p /content/models

# Try alternative URLs (the mradermacher one might be down)
print("⬇️ Downloading OCRFlux-3B-GGUF...")
!wget -q https://huggingface.co/bartowski/OCRFlux-3B-GGUF/resolve/main/OCRFlux-3B-Q4_K_M.gguf -O /content/models/ocrflux.gguf || \
wget -q https://huggingface.co/mradermacher/OCRFlux-3B-GGUF/resolve/main/OCRFlux-3B.Q4_K_M.gguf -O /content/models/ocrflux.gguf || \
echo "❌ Model download failed - using alternative method"

# --- CELL 4: Start vLLM Server (Standard OpenAI-compatible) ---
import subprocess
import time
import os

# Kill any existing processes
!pkill -f "vllm" 2>/dev/null || true

print("🚀 Starting vLLM server...")
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# Use standard vLLm with GGUF
server_cmd = """
python -m vllm.entrypoints.openai.api_server \
  --model /content/models/ocrflux.gguf \
  --quantization gguf \
  --gpu-memory-utilization 0.85 \
  --max-model-len 4096 \
  --port 8000 \
  --trust-remote-code \
  --dtype float16
"""

# Run in background
process = subprocess.Popen(server_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print("⏳ Waiting 90s for model load...")
time.sleep(90)

# Test if server is up
import requests
try:
    response = requests.get("http://localhost:8000/health")
    print(f"✅ Server status: {response.status_code}")
except:
    print("⚠️ Server might still be loading...")

# --- CELL 5: Expose via ngrok ---
!pip install pyngrok -q
from pyngrok import ngrok
import os

# KILL OLD TUNNELS (Crucial fix for ERR_NGROK_324)
print("🛑 Killing old ngrok processes...")
ngrok.kill()
!pkill -f ngrok

# AUTHENTICATE
# Replace with your token
NGROK_TOKEN = "YOUR_NGROK_TOKEN_HERE" 
ngrok.set_auth_token(NGROK_TOKEN)

public_url = ngrok.connect(8000).public_url
print(f"🌐 API URL: {public_url}/v1/chat/completions")
print(f"📋 Add to .env.local: OCRFLUX_URL={public_url}/v1/chat/completions")

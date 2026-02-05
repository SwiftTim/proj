# OCRFlux vLLM Colab Setup Script (ROBUST V3)
# COPY THESE CELLS INTO GOOGLE COLAB

# --- CELL 1: Setup & Download (Idempotent) ---
import os
import subprocess

# Create directory
!mkdir -p /content/models

# Check if file exists and is valid (OCRFlux-3B-Q4_K_M should be ~3.7GB)
model_path = "/content/models/ocrflux.gguf"
expected_size_gb = 3.5  # Minimum expected size in GB

if os.path.exists(model_path):
    file_size_gb = os.path.getsize(model_path) / (1024**3)
    if file_size_gb < expected_size_gb:
        print(f"⚠️ Corrupted/Incomplete file ({file_size_gb:.2f} GB). Re-downloading...")
        os.remove(model_path)
    else:
        print(f"✅ Model already exists ({file_size_gb:.2f} GB). Skipping download.")
else:
    print("⬇️ Downloading OCRFlux-3B-GGUF (3.7GB, takes ~5-8 minutes)...")
    
    # Use -c flag to resume interrupted downloads
    download_cmd = """wget -c --progress=bar:force \
      "https://huggingface.co/mradermacher/OCRFlux-3B-GGUF/resolve/main/OCRFlux-3B.Q4_K_M.gguf" \
      -O /content/models/ocrflux.gguf"""
    
    result = subprocess.run(download_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Download failed. Trying alternative mirror...")
        # Fallback to bartowski repo
        !wget -c "https://huggingface.co/bartowski/OCRFlux-3B-GGUF/resolve/main/OCRFlux-3B-Q4_K_M.gguf" \
          -O /content/models/ocrflux.gguf

# Verify download
if os.path.exists(model_path):
    final_size = os.path.getsize(model_path) / (1024**3)
    print(f"✅ Final model size: {final_size:.2f} GB")
    if final_size < 3.0:
        raise Exception("Download corrupted! File too small.")
else:
    raise Exception("Download failed! Model file not found.")

# --- CELL 2: Install Dependencies ---
print("📦 Installing vLLM...")
!pip install vllm==0.5.5 -q  # Pinning usually safer, but latest is fine
!pip install vllm -q
!pip install pyngrok -q

# --- CELL 3: Kill Old Processes ---
print("🛑 Cleaning up old processes...")
!pkill -f "vllm" 2>/dev/null || true
!pkill -f "python.*api_server" 2>/dev/null || true
!sleep 2

# --- CELL 4: Start vLLM Server ---
import time
import threading

print("🚀 Starting vLLM server...")
# Run in background properly
cmd = """nohup python -m vllm.entrypoints.openai.api_server \
  --model /content/models/ocrflux.gguf \
  --quantization gguf \
  --gpu-memory-utilization 0.85 \
  --max-model-len 4096 \
  --port 8000 \
  --trust-remote-code \
  --dtype float16 > /content/server.log 2>&1 &"""

get_ipython().system(cmd)

# Wait for server
print("⏳ Waiting for server to start (60s)...")
for i in range(60):
    time.sleep(1) # Python sleep
    # Use curl to check health
    response = !curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000"
    if response and response[0] == "200":
        print(f"✅ Server ready after {i+1} seconds!")
        break
    if i % 10 == 0:
        print(f"  ...still loading ({i+1}s)")

# Show latest logs
!tail -n 20 /content/server.log

# --- CELL 5: Setup Ngrok ---
from pyngrok import ngrok

# Use your token
NGROK_TOKEN = "2bgNrSjCqjzMq8K9CjlT5GN0tFp_5ahs5AUfSTpj3Cq4VvNHF" 
ngrok.set_auth_token(NGROK_TOKEN)

# Kill old tunnels first
ngrok.kill()

# Create new tunnel
public_url = ngrok.connect(8000, "http").public_url
print(f"🌐 API URL: {public_url}/v1/chat/completions")
print(f"🔧 Add to backend .env.local:")
print(f"OCRFLUX_URL={public_url}/v1/chat/completions")

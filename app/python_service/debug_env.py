import os
from dotenv import load_dotenv
import sys

# Path to .env.local
env_path = os.path.join(os.path.dirname(__file__), "../.env.local")
print(f"DEBUG: Looking for .env.local at: {os.path.abspath(env_path)}")
print(f"DEBUG: File exists: {os.path.exists(env_path)}")

load_dotenv(dotenv_path=env_path)

print(f"DEBUG: DOCLING_COLAB_URL = {os.getenv('DOCLING_COLAB_URL')}")
print(f"DEBUG: OCRFLUX_URL = {os.getenv('OCRFLUX_URL')}")

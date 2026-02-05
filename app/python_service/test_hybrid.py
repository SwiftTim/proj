import os
from dotenv import load_dotenv
from hybrid_ai_analyzer import run_pipeline

# 1. Load config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(BASE_DIR, ".env.local")
print(f"DEBUG: BASE_DIR={BASE_DIR}")
print(f"DEBUG: env_path={env_path}")
load_dotenv(env_path)

print(f"DEBUG: DEEPSEEK_KEY_SET={'DEEPSEEK_API_KEY' in os.environ}")
print(f"DEBUG: GEMINI_KEY_SET={'GEMINI_API_KEY' in os.environ or 'GOOGLE_API_KEY' in os.environ}")
print(f"DEBUG: GROQ_KEY_SET={'GROQ_API_KEY' in os.environ}")

def test_api_connectivity():
    print("🧪 Checking API Connectivity...")
    ds_key = os.getenv("DEEPSEEK_API_KEY")
    gm_key = os.getenv("GEMINI_API_KEY")
    
    # 1. Test DeepSeek
    try:
        from openai import OpenAI
        client = OpenAI(api_key=ds_key, base_url="https://api.deepseek.com/v1")
        print("📡 Ping DeepSeek...")
        client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5
        )
        print("✅ DeepSeek: OK")
    except Exception as e:
        print(f"❌ DeepSeek: {e}")
        
    # 2. Test Groq
    try:
        gr_key = os.getenv("GROQ_API_KEY")
        client = OpenAI(api_key=gr_key, base_url="https://api.groq.com/openai/v1")
        print("📡 Ping Groq...")
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5
        )
        print("✅ Groq: OK")
    except Exception as e:
        print(f"❌ Groq: {e}")

    # 2. Test Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=gm_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("📡 Ping Gemini...")
        model.generate_content("hi")
        print("✅ Gemini: OK")
    except Exception as e:
        print(f"❌ Gemini: {e}")

def test_hybrid():
    print("🚀 Testing Hybrid Pipeline (Real PDF)...")
    
    # Path to a real PDF
    test_pdf_path = os.path.join(BASE_DIR, "public", "uploads", "CGBIRR August 2025.pdf")
    
    if not os.path.exists(test_pdf_path):
        print(f"❌ Test PDF not found at {test_pdf_path}")
        return

    # 2. Check keys
    ds_key = os.getenv("DEEPSEEK_API_KEY")
    gr_key = os.getenv("GROQ_API_KEY")
    gm_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not (ds_key or gr_key) or not gm_key:
        print("❌ MISSING KEYS: Please ensure (DEEPSEEK_API_KEY or GROQ_API_KEY) and GEMINI_API_KEY are in .env.local")
        return

    print(f"📄 Reading {test_pdf_path}...")
    with open(test_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    county = "Mombasa"
    print(f"🔍 Analyzing {county}...")
    
    result = run_pipeline(pdf_bytes, county, "What are the pending bills and own source revenue?")
    
    print("\n--- FINAL RESULT ---")
    import json
    print(json.dumps(result, indent=2))
    print("--------------------")

if __name__ == "__main__":
    test_api_connectivity()
    test_hybrid()

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("../../.env.local")
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))

try:
    models = client.models.list()
    print("Available Groq Models:")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print(f"Error: {e}")

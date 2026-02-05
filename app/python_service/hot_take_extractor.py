import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Optional
from db import get_db_connection

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env.local"))

class HotTakeExtractor:
    """
    Daily "Hot Take" Extraction Service - Unified Dashboard Edition
    
    Generates three primary insights for the dashboard:
    1. Hot Insights (Deep dive on trending topic)
    2. Daily Audit (Comparative OSR performance)
    3. Economic Ticker (Live news headlines)
    """
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("gemini")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or gemini not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    async def extract_daily_hot_takes(self) -> Dict:
        """
        Calls Gemini to perform the daily fiscal analysis.
        """
        prompt = """
        You are a Senior Public Finance Analyst for Kenya. Use the current date Feb 5, 2026.
        Your goal is to synthesize data for a high-level budget transparency dashboard.
        
        Provide three sections in your response:
        
        1. HOT INSIGHTS:
           Identify a major trending fiscal topic today (e.g., "The 5% PAYE Relief Proposal" or "Wage Bill Sustainability").
           - topic: Catchy name
           - description: 1-sentence summary
           - deep_dive: 3 detailed bullet points analyzing impact on counties.
           - keywords: 3 relevant tags.
           - priority: urgency (8-10).
        
        2. DAILY AUDIT (Comparative performance):
           Select TWO specific Kenyan counties with a notable gap in their OSR (Own Source Revenue) collection performance.
           - county_1: {name, budgeted, actual} (budgeted and actual MUST be numeric - integers or floats representing KES billions)
           - county_2: {name, budgeted, actual} (budgeted and actual MUST be numeric - integers or floats representing KES billions)
           - insight: Why this comparison is important today.
        
        3. ECONOMIC TICKER:
           Provide 3-4 short, punchy headlines (max 10 words each) about Kenya's economy today.
        
        Format the response as a clean JSON object:
        {
          "hot_insight": { "topic": "", "description": "", "deep_dive": [], "keywords": [], "priority": 9 },
          "daily_audit": { "county_1": {}, "county_2": {}, "insight": "" },
          "economic_ticker": ["Headline 1", "Headline 2", "..."]
        }
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start == -1 or end == 0:
                raise ValueError("Gemini response did not contain valid JSON")
                
            return json.loads(text[start:end])
        except Exception as e:
            print(f"❌ Gemini Extraction Error: {e}")
            raise

    async def save_to_database(self, data: Dict) -> bool:
        """
        Saves the structured morning sync data to the database.
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            today = datetime.now().date()
            
            cur.execute("""
                INSERT INTO trending_merits (
                    date, topic_name, description, keywords, priority_score, 
                    daily_audit, economic_ticker, raw_gemini_response
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO UPDATE SET
                    topic_name = EXCLUDED.topic_name,
                    description = EXCLUDED.description,
                    keywords = EXCLUDED.keywords,
                    priority_score = EXCLUDED.priority_score,
                    daily_audit = EXCLUDED.daily_audit,
                    economic_ticker = EXCLUDED.economic_ticker,
                    raw_gemini_response = EXCLUDED.raw_gemini_response
            """, (
                today,
                data.get('hot_insight', {}).get('topic', 'Daily Fiscal Update'),
                data.get('hot_insight', {}).get('description', ''),
                data.get('hot_insight', {}).get('keywords', []),
                data.get('hot_insight', {}).get('priority', 5),
                json.dumps(data.get('daily_audit', {})),
                json.dumps(data.get('economic_ticker', [])),
                json.dumps(data)
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Daily Sync saved for {today}")
            return True
        except Exception as e:
            print(f"❌ Database Save Error: {e}")
            return False

    async def run_daily_extraction(self) -> Dict:
        """
        Orchestrates the full morning sync process.
        """
        try:
            data = await self.extract_daily_hot_takes()
            if await self.save_to_database(data):
                return {"success": True, "data": data}
            return {"success": False, "error": "Database save failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import asyncio
    async def run_test():
        extractor = HotTakeExtractor()
        res = await extractor.run_daily_extraction()
        print(json.dumps(res, indent=2))
    asyncio.run(run_test())

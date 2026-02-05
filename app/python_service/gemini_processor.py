import os
import json
from ai_models.gemini_client import GeminiClient

class GeminiBudgetProcessor:
    def __init__(self):
        self.client = GeminiClient()

    async def process(self, pdf_path: str, county_name: str):
        """
        Orchestrates the Gemini-based extraction process.
        """
        try:
            # 1. Direct analysis via Gemini
            raw_data = await self.client.analyze_pdf(pdf_path, county_name)
            
            # 2. Map to interpreted structure for the frontend
            processed_result = {
                "status": "success",
                "method": "Google Gemini (Long Context)",
                "county": county_name,
                "interpreted_data": {
                    "county": county_name,
                    "summary_text": raw_data.get("executive_summary", "No summary provided."),
                    "key_metrics": {
                        "OSR Actual": raw_data.get("own_source_revenue_actual", 0),
                        "OSR Target": raw_data.get("own_source_revenue_target", 0),
                        "Total Revenue": raw_data.get("total_revenue", 0),
                        "Total Expenditure": raw_data.get("total_expenditure", 0),
                        "Development Exp": raw_data.get("development_expenditure", 0),
                        "Recurrent Exp": raw_data.get("recurrent_expenditure", 0),
                        "Personnel Emoluments": raw_data.get("personnel_emoluments", 0),
                        "Pending Bills": raw_data.get("pending_bills", 0)
                    },
                    "intelligence": {
                        "transparency_risk_score": (raw_data.get("fiscal_health_score", 5) * 10), # Scale 1-10 to 1-100
                        "risk_assessment_text": raw_data.get("risk_assessment", "Moderate"),
                        "executive_summary": raw_data.get("executive_summary", "")
                    },
                    "sectoral_allocations": {} # Gemini could fill this too if prompt updated
                },
                "raw_verified_data": {
                    "osr_actual": raw_data.get("own_source_revenue_actual"),
                    "osr_target": raw_data.get("own_source_revenue_target"),
                    "total_osr_actual": raw_data.get("own_source_revenue_actual"),
                    "source": "Google Gemini AI Synthesis (Full PDF Context)"
                }
            }
            
            return processed_result

        except Exception as e:
            print(f"❌ Gemini Processor Error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "method": "google_gemini_direct"
            }

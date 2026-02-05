import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env.local"))

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("gemini")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or gemini not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Use the latest Gemini 2.5 Flash as verified by the user
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def analyze_pdf(self, pdf_path, county_name):
        """
        Uploads a PDF to Gemini and extracts financial data.
        """
        print(f"🌟 Gemini Analysis: Processing {pdf_path} for {county_name}")
        
        try:
            # Upload the file
            sample_file = genai.upload_file(path=pdf_path, display_name=f"Budget_{county_name}")
            print(f"📤 Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

            # Wait for processing (though usually fast for small items, but good practice)
            # For Gemini 1.5, file processing is usually async
            while sample_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(2)
                sample_file = genai.get_file(sample_file.name)

            if sample_file.state.name == "FAILED":
                raise Exception(f"File processing failed: {sample_file.state.name}")

            prompt = f"""
            Extract the following financial information for {county_name} County from the attached Budget Implementation Review Report.
            
            Return ONLY a JSON object with the following structure:
            {{
                "county_name": "{county_name}",
                "total_budget": "number",
                "total_revenue": "number",
                "own_source_revenue_target": "number",
                "own_source_revenue_actual": "number",
                "total_expenditure": "number",
                "development_expenditure": "number",
                "recurrent_expenditure": "number",
                "personnel_emoluments": "number",
                "pending_bills": "number",
                "fiscal_health_score": "number between 1-10",
                "risk_assessment": "Low/Moderate/High",
                "executive_summary": "A concise professional summary of the county's fiscal performance."
            }}
            
            If a value is not found, use 0 for numbers and "N/A" for strings.
            Be extremely precise. Look for the specific section for {county_name} County.
            """

            response = self.model.generate_content([sample_file, prompt])
            
            # Clean up the file from Gemini's storage
            genai.delete_file(sample_file.name)
            
            # Extract JSON from response
            text = response.text
            # Basic cleaning if AI provides markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            
            # Standardize output to match application's expected format if necessary
            # For now, let's keep it clean as requested.
            
            return result

        except Exception as e:
            print(f"❌ Gemini Analysis Error: {str(e)}")
            raise e

if __name__ == "__main__":
    # Quick test if run directly
    import asyncio
    client = GeminiClient()
    # Mock path
    # asyncio.run(client.analyze_pdf("test.pdf", "Nairobi"))

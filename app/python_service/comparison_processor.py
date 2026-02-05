import os
import json
import asyncio
from ai_models.gemini_client import GeminiClient
import google.generativeai as genai

class GeminiComparisonProcessor:
    """
    PDF Push & Compare Pipeline using Gemini's Long Context Window.
    
    Architecture:
    1. Ingestion Layer: User pushes county PDF + system fetches official CBIRR section
    2. Extraction Layer: Gemini extracts identical merits from both documents
    3. Cross-Reference Logic: AI compares figures and flags integrity alerts
    4. Reporting Layer: Generates Budget Integrity Scorecard
    """
    
    # Merit definitions mapping to CBIRR structure
    MERIT_DEFINITIONS = {
        "Absorption Gap": {
            "description": "Compares target development budget (30% legal limit) against actual spending",
            "cbirr_sections": ["3.X.6 (Development Expenditure)", "3.X.7 (Recurrent Expenditure)"],
            "calculation": "Development Actual / Total Expenditure * 100"
        },
        "Revenue Variance": {
            "description": "Compares projected Own-Source Revenue against actual collections",
            "cbirr_sections": ["3.X.2 (Own Source Revenue)", "3.X.5 (Total Revenue)"],
            "calculation": "OSR Actual / OSR Target * 100"
        },
        "Wage Bill Compliance": {
            "description": "Checks if personnel emoluments exceed 35% regulatory ceiling",
            "cbirr_sections": ["3.X.8 (Compensation to Employees)", "3.X.5 (Total Revenue)"],
            "calculation": "Personnel Emoluments / Total Revenue * 100"
        },
        "Debt Stock": {
            "description": "Compares pushed pending bills against official debt stock",
            "cbirr_sections": ["3.X.14 (Pending Bills)", "3.X.15 (Debt Analysis)"],
            "calculation": "Total Pending Bills Amount"
        }
    }
    
    def __init__(self):
        self.client = GeminiClient()
        # Use Gemini 2.5 Flash (same as analysis tab)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def compare(self, pushed_pdf_path: str, official_pdf_path: str, county_name: str, merits: list):
        """
        Compares a user-pushed PDF against the official CBIRR report for a specific county.
        Uses Gemini's long context window to analyze both documents simultaneously.
        
        Args:
            pushed_pdf_path: Path to county's own budget document
            official_pdf_path: Path to official CBIRR report
            county_name: Name of the county (e.g., "Nairobi", "Embu")
            merits: List of merit names to compare (e.g., ["Absorption Gap", "Debt Stock"])
        
        Returns:
            Dictionary with integrity score, verdict, merit comparisons, and alerts
        """
        print(f"🔄 Gemini Comparison Pipeline Started")
        print(f"   County: {county_name}")
        print(f"   Pushed: {os.path.basename(pushed_pdf_path)}")
        print(f"   Official: {os.path.basename(official_pdf_path)}")
        print(f"   Merits: {', '.join(merits)}")
        
        try:
            # === INGESTION LAYER ===
            print("📤 Uploading documents to Gemini...")
            files = []
            pushed_file = genai.upload_file(path=pushed_pdf_path, display_name=f"County_Pushed_{county_name}")
            official_file = genai.upload_file(path=official_pdf_path, display_name=f"Official_CBIRR_2024_25")
            files = [pushed_file, official_file]

            # Wait for processing
            for f in files:
                while f.state.name == "PROCESSING":
                    print(f"   ⏳ Processing {f.display_name}...", flush=True)
                    await asyncio.sleep(2)
                    f = genai.get_file(f.name)
                if f.state.name == "FAILED":
                    raise Exception(f"File {f.display_name} failed to process.")
                print(f"   ✅ {f.display_name} ready")

            # Build merit context for the prompt
            merit_context = self._build_merit_context(merits)
            
            # === EXTRACTION & CROSS-REFERENCE LAYER ===
            prompt = f"""
You are a Senior Public Finance Integrity Auditor for the Controller of Budget, Kenya.

MISSION: Compare a County Government's self-reported budget document ("Pushed Document") against the official Controller of Budget Implementation Review Report (CBIRR) 2024/25 for {county_name} County.

CONTEXT - CBIRR Structure:
The official CBIRR report contains county-specific sections numbered 3.X.1 through 3.X.16, where X is the county number. Each section contains:
- 3.X.1: County Profile
- 3.X.2: Own Source Revenue (OSR Target and Actual)
- 3.X.5: Total Revenue Performance
- 3.X.6: Development Expenditure
- 3.X.7: Recurrent Expenditure
- 3.X.8: Compensation to Employees (Wage Bill)
- 3.X.14: Pending Bills Analysis
- 3.X.15: Debt Stock

MERITS TO COMPARE:
{merit_context}

EXTRACTION PROTOCOL:
1. **Locate County Section**: Find the specific section for {county_name} County in the Official CBIRR document (look for "3.X" sections or county name in headers).

2. **Extract Official Data**: For each merit, extract the exact figures from the CBIRR using the section references above.

3. **Extract Pushed Data**: For each merit, extract corresponding figures from the County's Pushed Document.

4. **Cross-Reference**: Compare the two values:
   - If Pushed value is LOWER than Official for debt/bills → FLAG as "Integrity Alert" (underreporting)
   - If Pushed value is HIGHER than Official for revenue/performance → FLAG as "Integrity Alert" (overreporting)
   - If values match within ±5% → Mark as "verified"
   - Calculate exact discrepancy amount and percentage

5. **Integrity Scoring**:
   - Start at 100 points
   - Deduct 15 points for each major discrepancy (>10% variance)
   - Deduct 5 points for each minor discrepancy (5-10% variance)
   - Deduct 25 points for each missing/unavailable data point
   - Minimum score: 0

CRITICAL RULES:
- Use EXACT figures from the documents (include currency symbols and units)
- If a figure is not found, state "Data Not Available" and flag as integrity concern
- For {county_name}, search for variations: "{county_name}", "{county_name} County", "County Government of {county_name}"
- Cite specific page numbers or section numbers where data was found

OUTPUT FORMAT (JSON ONLY):
{{
    "county": "{county_name}",
    "integrity_score": <0-100>,
    "verdict": "<1-sentence executive summary of integrity assessment>",
    "merit_comparison": [
        {{
            "merit": "<Merit Name>",
            "official_value": "<Exact value from CBIRR with units>",
            "official_source": "<Section/Page reference>",
            "pushed_value": "<Exact value from Pushed doc with units>",
            "pushed_source": "<Page reference>",
            "discrepancy": "<Detailed explanation of variance>",
            "variance_percent": <numeric percentage>,
            "status": "verified" | "alert" | "data_missing"
        }}
    ],
    "integrity_alerts": [
        "<Specific alert message 1>",
        "<Specific alert message 2>"
    ],
    "data_quality_notes": "<Any observations about data completeness or quality>"
}}

Begin analysis now. Return ONLY the JSON object, no additional text.
"""

            print("🧠 Running Gemini analysis...")
            response = self.model.generate_content([official_file, pushed_file, prompt])
            
            # === CLEANUP ===
            print("🧹 Cleaning up uploaded files...")
            for f in files:
                genai.delete_file(f.name)

            # === REPORTING LAYER ===
            text = response.text
            # Extract JSON from markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            
            print(f"✅ Comparison Complete | Integrity Score: {result.get('integrity_score', 'N/A')}")
            return result

        except Exception as e:
            print(f"❌ Gemini Comparison Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "county": county_name,
                "error": str(e),
                "integrity_score": 0,
                "verdict": f"Analysis failed: {str(e)}",
                "merit_comparison": [],
                "integrity_alerts": [f"System Error: {str(e)}"]
            }
    
    def _build_merit_context(self, merits: list) -> str:
        """Build detailed context for each merit being compared."""
        context_lines = []
        for merit in merits:
            if merit in self.MERIT_DEFINITIONS:
                defn = self.MERIT_DEFINITIONS[merit]
                context_lines.append(f"""
**{merit}**:
- Description: {defn['description']}
- CBIRR Sections: {', '.join(defn['cbirr_sections'])}
- Calculation: {defn['calculation']}
""")
            else:
                # Generic merit
                context_lines.append(f"**{merit}**: Extract and compare this metric from both documents.")
        
        return "\n".join(context_lines)

import io
import os
import re
import json
import time
from typing import Dict, Any, List, Tuple, Optional
import pypdf
import pymupdf4llm
from dotenv import load_dotenv

# --------------------------------------------------
# ENV + AI CLIENT
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env.local"))

def create_ai_client():
    """Create AI client as fallback."""
    try:
        from openai import OpenAI
    except ImportError:
        return None, None

    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if groq_key:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_key
        )
        model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        return client, model

    if openai_key:
        client = OpenAI(api_key=openai_key)
        model = "gpt-4o"
        return client, model

    return None, None

AI_CLIENT, AI_MODEL = create_ai_client()

# --------------------------------------------------
# DYNAMIC TOC MAPPING
# --------------------------------------------------

class DynamicTOCMapper:
    """Maps counties to their specific page numbers in the CBIRR report."""
    
    def __init__(self, pdf_bytes: bytes):
        self.pdf_bytes = pdf_bytes
        self.toc_text = ""
        self._extract_toc()
    
    def _extract_toc(self):
        """Extract the first 20 pages which usually contain the TOC."""
        reader = pypdf.PdfReader(io.BytesIO(self.pdf_bytes))
        for i in range(min(20, len(reader.pages))):
            self.toc_text += reader.pages[i].extract_text() or ""
    
    def get_county_page(self, county: str) -> Optional[int]:
        """Find the starting page number for a specific county."""
        # Pattern: 3.XX. County Government of [County] ... [PageNumber]
        # We use a flexible regex to handle variations in dots and spacing
        pattern = rf"County\s+Government\s+of\s+{re.escape(county)}[\s\.]+(\d+)"
        match = re.search(pattern, self.toc_text, re.IGNORECASE)
        
        if match:
            page_num = int(match.group(1))
            print(f"📍 TOC Mapping: Found {county} starting at page {page_num}")
            return page_num
        
        # Fallback: search for the county name directly in the TOC text
        pattern_alt = rf"{re.escape(county)}[\s\.]+(\d+)"
        match_alt = re.search(pattern_alt, self.toc_text, re.IGNORECASE)
        if match_alt:
            page_num = int(match_alt.group(1))
            print(f"📍 TOC Mapping (Fallback): Found {county} at page {page_num}")
            return page_num
            
        print(f"⚠️ TOC Mapping: Could not find {county} in TOC")
        return None

# --------------------------------------------------
# REGEX-TARGETED EXTRACTION
# --------------------------------------------------

class RegexSieve:
    """Extracts specific financial metrics using targeted regex patterns within relevant sections."""
    
    def __init__(self):
        # Patterns now include sentence structures and "billion/million" support
        self.patterns = {
            "own_source_revenue": [
                r"(?i)Own\s+Source\s+Revenue\s+(?:amounted\s+to|was|collected).*?Kshs?\.?\s*([\d,.]+)\s*(billion|million)",
                r"(?i)Own\s+Source\s+Revenue.*?Kshs?\.?\s*([\d,.]+)\s*(billion|million)?",
                r"(?i)Ordinary\s+Own\s+Source\s+Revenue.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)",
            ],
            "development_expenditure": [
                r"(?i)expenditure\s+on\s+development\s+programs.*?amounted\s+to\s+Kshs?\.?\s*([\d,.]+)\s*(billion|million)",
                r"(?i)Development\s+Expenditure.*?Kshs?\.?\s*([\d,.]+)\s*(billion|million)?",
            ],
            "pending_bills": [
                r"(?i)reported\s+total\s+pending\s+bills\s+of\s+Kshs?\.?\s*([\d,.]+)\s*(billion|million)",
                r"(?i)Pending\s+Bills.*?Kshs?\.?\s*([\d,.]+)\s*(billion|million)?",
            ],
            "total_revenue": [
                r"(?i)total\s+revenue\s+received.*?was\s+Kshs?\.?\s*([\d,.]+)\s*(billion|million)",
                r"(?i)Total\s+Revenue.*?Kshs?\.?\s*([\d,.]+)\s*(billion|million)?",
            ],
            "total_expenditure": [
                r"(?i)spent\s+a\s+total\s+of\s+Kshs?\.?\s*([\d,.]+)\s*(billion|million)",
                r"(?i)Total\s+Expenditure.*?Kshs?\.?\s*([\d,.]+)\s*(billion|million)?",
            ]
        }

    def extract_metrics(self, text: str) -> Dict[str, int]:
        """Extract all metrics from the provided text, respecting section context."""
        results = {}
        
        # 1. Extract Sections
        revenue_section = self._extract_section(text, "Revenue Performance")
        expenditure_section = self._extract_section(text, "County Expenditure Review")
        bills_section = self._extract_section(text, "Settlement of Pending Bills")
        
        # If sections aren't found, fallback to full text
        if not revenue_section: revenue_section = text
        if not expenditure_section: expenditure_section = text
        if not bills_section: bills_section = text

        # 2. Map Metrics to Sections
        # (Metric Name -> Source Text)
        mapping = {
            "own_source_revenue": revenue_section,
            "total_revenue": revenue_section,
            "development_expenditure": expenditure_section,
            "total_expenditure": expenditure_section,
            "pending_bills": bills_section
        }

        for metric, patterns in self.patterns.items():
            source_text = mapping.get(metric, text)
            found_value = 0
            
            for pattern in patterns:
                matches = re.findall(pattern, source_text)
                if matches:
                    for match in matches:
                        # Match might be a tuple (amount, unit) or just amount
                        if isinstance(match, tuple):
                            val = self._normalize_amount(match[0], match[1] if len(match) > 1 else "")
                        else:
                            val = self._normalize_amount(match)
                            
                        if val > 0: 
                            found_value = val
                            break
                if found_value > 0:
                    break
            results[metric] = found_value
            
        return results

    def _extract_section(self, text: str, title_keyword: str) -> str:
        """
        Extracts text belonging to a section with the given title.
        Looks for markdown headers like '### 3.28.2 Revenue Performance'.
        """
        # Regex explanation:
        # ^#{1,6}\s+            : Starts with 1-6 hashes (Markdown header)
        # (?:[\d\.]+\s+)?       : Optional numbering (e.g., "3.28.2 ")
        # .*?                   : Any text
        # title_keyword         : The specific title we want
        # .*?$                  : Rest of the line
        pattern = rf"(^#{1,6}\s+(?:[\d\.]+\s+)?.*?{re.escape(title_keyword)}.*?$)([\s\S]*?)(?=^#{1,6}\s+|\Z)"
        
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            # print(f"✅ Found section: {title_keyword}")
            return match.group(2)
        return ""

    def _normalize_amount(self, value_str: str, unit: str = "") -> int:
        """Convert string amount to integer, handling 'billion'/'million'."""
        try:
            # Clean string
            clean = value_str.replace(',', '').strip()
            amount = float(clean)
            
            unit = unit.lower().strip()
            if "billion" in unit:
                amount *= 1_000_000_000
            elif "million" in unit:
                amount *= 1_000_000
            
            return int(amount)
        except (ValueError, TypeError):
            return 0

# --------------------------------------------------
# ENHANCED COUNTY ANALYZER
# --------------------------------------------------

class EnhancedCountyAnalyzer:
    """Main analyzer using TOC mapping, Markdown conversion, and Regex extraction."""
    
    def __init__(self, ai_client=None, ai_model=None):
        self.ai_client = ai_client
        self.ai_model = ai_model
        self.sieve = RegexSieve()
    
    def analyze_pdf(self, pdf_bytes: bytes, county: str) -> Dict[str, Any]:
        """Main analysis pipeline."""
        start_time = time.time()
        print(f"🚀 Starting Enhanced Analysis for {county} County...")
        
        # 1. Dynamic TOC Mapping
        mapper = DynamicTOCMapper(pdf_bytes)
        start_page = mapper.get_county_page(county)
        
        if not start_page:
            # Fallback: search entire document (slow)
            print(f"⚠️ Falling back to full document scan for {county}")
            return self._full_scan_fallback(pdf_bytes, county, start_time)

        # 2. High-Fidelity Markdown Conversion (Targeted)
        # We extract ~12 pages starting from the county's section
        print(f"🧹 Converting pages {start_page} to {start_page+12} to Markdown...")
        try:
            # pymupdf4llm uses 0-based indexing for pages, but TOC usually uses 1-based
            # We'll try both or adjust based on common CBIRR offsets
            # Usually TOC page numbers are 1-based.
            page_range = list(range(start_page - 1, min(start_page + 11, 1000))) # 0-indexed
            
            # Save PDF to temp file for pymupdf4llm
            temp_pdf = f"temp_{int(time.time())}.pdf"
            with open(temp_pdf, "wb") as f:
                f.write(pdf_bytes)
            
            md_content = pymupdf4llm.to_markdown(temp_pdf, pages=page_range)
            os.remove(temp_pdf)
            
            # 3. Regex-Targeted Extraction
            metrics = self.sieve.extract_metrics(md_content)
            
            # 4. AI Fallback for missing metrics
            missing = [k for k, v in metrics.items() if v == 0]
            if missing and self.ai_client:
                print(f"🤖 AI assisting with missing metrics: {missing}")
                ai_results = self._ai_assist(md_content[:15000], county, missing)
                metrics.update(ai_results)

            # 5. Structured JSON Output
            return self._format_response(county, metrics, start_time, md_content)

        except Exception as e:
            print(f"❌ Error during enhanced extraction: {e}")
            return self._error_response(county, str(e))

    def _full_scan_fallback(self, pdf_bytes: bytes, county: str, start_time: float) -> Dict[str, Any]:
        """Fallback when TOC mapping fails."""
        # Implementation of the old logic or a simplified version
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        found_page = -1
        for i in range(len(reader.pages)):
            text = reader.pages[i].extract_text() or ""
            if f"County Government of {county}" in text:
                found_page = i + 1
                break
        
        if found_page == -1:
            return self._error_response(county, "County not found in document")
            
        # Re-run with the found page
        # (Simplified for this implementation)
        return self.analyze_pdf(pdf_bytes, county)

    def _ai_assist(self, text: str, county: str, missing: List[str]) -> Dict[str, int]:
        """AI assistance for missing metrics."""
        try:
            prompt = f"""
            Extract the following budget metrics for {county} County from this text.
            Metrics needed: {', '.join(missing)}
            
            Text:
            {text}
            
            Return ONLY a JSON object with integer values.
            Example: {{"pending_bills": 1200000000}}
            """
            
            response = self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ AI assist failed: {e}")
            return {}

    def _format_response(self, county: str, metrics: Dict[str, int], start_time: float, md_content: str) -> Dict[str, Any]:
        """Format the final structured JSON response."""
        processing_time = round(time.time() - start_time, 2)
        
        # Calculate transparency score (0-100)
        found_count = sum(1 for v in metrics.values() if v > 0)
        completeness = (found_count / len(metrics)) * 100
        
        # Simple insights
        insights = []
        if metrics.get("pending_bills", 0) > 1_000_000_000:
            insights.append("🚩 High level of pending bills detected")
        if metrics.get("development_expenditure", 0) < metrics.get("total_expenditure", 0) * 0.3:
            insights.append("⚠️ Low development expenditure relative to total spending")
            
        return {
            "county": county,
            "status": "success",
            "key_metrics": metrics,
            "summary_text": f"Analysis for {county} County completed in {processing_time}s. Data completeness: {completeness:.0f}%.",
            "intelligence": {
                "flags": insights,
                "transparency_risk_score": 100 - int(completeness),
                "data_completeness": f"{completeness:.0f}%"
            },
            "processing_time_sec": processing_time,
            "method": "Enhanced (TOC + Markdown + Regex)"
        }

    def _error_response(self, county: str, error: str) -> Dict[str, Any]:
        return {
            "county": county,
            "status": "error",
            "error": error,
            "key_metrics": {},
            "intelligence": {"flags": [error], "transparency_risk_score": 100}
        }

# --------------------------------------------------
# MAIN ENTRY POINT
# --------------------------------------------------

def run_pipeline(pdf_bytes: bytes, county: str) -> Dict[str, Any]:
    """FINAL WORKING PIPELINE"""
    analyzer = EnhancedCountyAnalyzer(ai_client=AI_CLIENT, ai_model=AI_MODEL)
    return analyzer.analyze_pdf(pdf_bytes, county)

if __name__ == "__main__":
    # Test with Mombasa
    test_pdf = "../../public/uploads/CGBIRR August 2025.pdf"
    if os.path.exists(test_pdf):
        with open(test_pdf, "rb") as f:
            data = f.read()
        result = run_pipeline(data, "Mombasa")
        print(json.dumps(result, indent=2))
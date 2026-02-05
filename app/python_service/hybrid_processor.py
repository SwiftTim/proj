from typing import Dict, Optional
from ai_models.ocrflux_client import OCRFluxClient, ExtractionResult
from ai_models.groq_client import GroqAnalyzer
from processors.table_parser import CGBIRRTableParser
from validators.data_validator import DataValidator
import os
import re
import json
from hybrid_ai_analyzer import extract_table_2_1_numbers, validate_county_data

class OCRFluxConfig:
    """
    Configuration for OCRFlux-3B Vision Model
    
    IMPORTANT: OCRFlux should be hosted on Google Colab for best performance
    
    Setup Instructions:
    1. Open Google Colab notebook with OCRFlux-3B-GGUF model
    2. Expose the API using ngrok or similar tunneling service
    3. Set OCRFLUX_URL environment variable to the public URL
       Example: OCRFLUX_URL=https://abc123.ngrok.io
    
    Fallback: If OCRFLUX_URL is not set, will use HuggingFace Inference API
              (slower due to cold starts, but doesn't require Colab setup)
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("HF_API_KEY")
        self.model = "OCRFlux-3B-Q4_K_M"
        # Primary: Google Colab instance URL (recommended for production)
        # Set this to your Colab ngrok URL for faster processing
        self.local_url = os.getenv("OCRFLUX_URL", "").strip() or None

class GroqConfig:
    def __init__(self, api_key=None, model="llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.max_tokens = 2000

class HybridBudgetProcessor:
    def __init__(self, ocrflux_config=None, groq_config=None):
        self.ocrflux = OCRFluxClient(ocrflux_config or OCRFluxConfig())
        self.groq = GroqAnalyzer(groq_config or GroqConfig())
        self.parser = CGBIRRTableParser()
        self.validator = DataValidator()
        
    async def process(self, pdf_path: str, county_name: str) -> Dict:
        """
        Execute two-stage pipeline with validation checkpoint
        """
        # STAGE 1: OCRFlux-3B Extraction
        print(f"🔍 Stage 1: OCRFlux extracting {county_name} from {pdf_path}...")
        
        # We target specific tables implicitly by reading the pages
        extraction_result = await self.ocrflux.extract(
            pdf_path=pdf_path,
            county_name=county_name,
            target_tables=["2.1", "2.5", "2.9", "2.2"]
        )
        
        if not extraction_result.markdown:
            print("❌ Stage 1 failed: No markdown extracted from OCRFlux")
            
        # --- NEW: Print Raw Discovery JSON ---
        print(f"📦 RAW DISCOVERY JSON (Metadata):")
        print(json.dumps({
            "county_name": county_name,
            "markdown_len": len(extraction_result.markdown),
            "confidence": extraction_result.confidence,
            "pages_processed": extraction_result.pages_processed
        }, indent=2))
        
        # Stage 1.5: Intelligent Parsing via Groq
        print(f"🧠 Stage 1.5: Intelligent Parsing via Groq...")
        
        # --- NEW: Raw PDF Extraction Match (For Transparency) ---
        print(f"\n📑 RAW PDF TABLE MATCH (Anchor: {county_name}):")
        print("-" * 50)
        found_raw = False
        for line in extraction_result.markdown.split('\n'):
            if county_name.lower() in line.lower() and ('|' in line or re.search(r'\d+\.\d+', line)):
                print(f"✅ Found Raw Row: {line.strip()}")
                found_raw = True
        if not found_raw:
            print(f"⚠️ No direct table row matching '{county_name}' found in markdown.")
        print("-" * 50 + "\n")

        structured_data = await self.groq.parse_markdown_tables(
            markdown=extraction_result.markdown,
            county_name=county_name
        )
        
        if not structured_data or not structured_data.get('revenue'):
             print("⚠️ Groq parsing failed or returned empty - falling back to Regex parser")
             structured_data = self.parser.parse(extraction_result.markdown, county_name)
             
        # --- NEW: Print Raw Structured JSON ---
        print(f"📦 RAW STRUCTURED JSON (Numerical Data):")
        print(json.dumps(structured_data, indent=2))
        
        # --- ENHANCEMENT: Derived Metrics Calculation ---
        # Ensure total_revenue is populated if components exist
        if structured_data.get('revenue'):
            rev = structured_data['revenue']
            
            # Fallback 1: Calculate Total Revenue
            if not rev.get('total_revenue'):
                osr = rev.get('own_source_revenue') or rev.get('osr_actual') or 0
                eq = rev.get('equitable_share') or 0
                if osr > 0 and eq > 0:
                    print(f"➕ Calculating Total Revenue from Components: {osr:,} + {eq:,}")
                    rev['total_revenue'] = osr + eq
            
            # Fallback 2: Calculate OSR Target (Total Rev - Equitable Share)
            if not rev.get('osr_target') or rev.get('osr_target') == 0:
                total = rev.get('total_revenue') or 0
                eq = rev.get('equitable_share') or 0
                if total > 0 and eq > 0 and total > eq:
                    calculated_target = total - eq
                    print(f"➕ Manual OSR Target Fallback (Total - Eq): {calculated_target:,}")
                    rev['osr_target'] = calculated_target
        
        
        # STAGE 2: Groq Analysis
        print(f"🧬 Stage 2: Insights & Fiscal Analysis for {county_name}...")
        
        # --- NEW: Raw PDF Extraction Match (For Transparency) ---
        raw_verified = extract_table_2_1_numbers(extraction_result.raw_text, county_name)
        print(f"📊 Raw Verified Data Extracted: {raw_verified}")
        
        # --- MERGE: Update structured_data with Verified Raw Data ---
        if raw_verified:
            print(f"🔄 Merging Verified Raw Data into Analysis...")
            if 'revenue' not in structured_data: structured_data['revenue'] = {}
            
            if 'osr_target' in raw_verified:
                structured_data['revenue']['osr_target'] = raw_verified['osr_target']
            if 'osr_actual' in raw_verified:
                structured_data['revenue']['osr_actual'] = raw_verified['osr_actual']
                structured_data['revenue']['own_source_revenue'] = raw_verified['osr_actual']
            
            # Recalculate OSR Performance
            if structured_data['revenue'].get('osr_target') and structured_data['revenue'].get('osr_actual'):
                try:
                    pct = (structured_data['revenue']['osr_actual'] / structured_data['revenue']['osr_target']) * 100
                    structured_data['revenue']['osr_performance_pct'] = round(pct, 1)
                except ZeroDivisionError:
                    pass

        analysis_result = await self.groq.analyze(
            structured_data=structured_data,
            county_name=county_name,
            context_snippets=extraction_result.markdown[:15000] 
        )
        
        # Construct Interpreted Data
        interpreted_data = {
            "county": county_name,
            "key_metrics": {
                "total_budget": structured_data.get('revenue', {}).get('total_budget', 0) or analysis_result.get('key_figures', {}).get('total_budget', 0),
                "total_revenue": structured_data.get('revenue', {}).get('total_revenue', 0),
                "total_expenditure": structured_data.get('expenditure', {}).get('total_expenditure', 0),
                "own_source_revenue": structured_data.get('revenue', {}).get('own_source_revenue', 0),
                "pending_bills": structured_data.get('debt', {}).get('pending_bills', 0),
                "osr_target": structured_data.get('revenue', {}).get('osr_target', 0)
            },
            "summary_text": analysis_result.get('executive_summary', ''),
            "intelligence": {
                **analysis_result.get('risk_assessment', {}),
                "verdict": analysis_result.get('risk_assessment', {}).get('verdict', 'Unknown'),
                "citizen_summary": analysis_result.get('citizen_summary', ''),
                "pillars": analysis_result.get('pillars', {}),
                "auditor_key_figures": analysis_result.get('key_figures', {})
            },
            "sectoral_allocations": structured_data.get('sectoral_allocations', {})
        }

        # --- VALIDATE: Apply Ground Truth Corrections ---
        interpreted_data = validate_county_data(interpreted_data, county_name)

        return {
            "interpreted_data": interpreted_data,
            "raw_verified_data": {
                "osr_target": f"Million {raw_verified.get('osr_target_raw', 'N/A')}",
                "osr_actual": f"Million {raw_verified.get('osr_actual_raw', 'N/A')}",
                "total_osr_target": f"Million {raw_verified.get('total_osr_target_raw', 'N/A')}",
                "total_osr_actual": f"Million {raw_verified.get('total_osr_actual_raw', 'N/A')}",
                "source": "Vision-Based Table Extraction (OCRFlux)"
            },
            "metadata": {
                "ocrflux_confidence": extraction_result.confidence,
                "processing_method": "hybrid_ocrflux_groq_v2",
                "raw_markdown": extraction_result.markdown
            }
        }

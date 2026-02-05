import io
import re
import os
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from decimal import Decimal
from collections import defaultdict, OrderedDict
import pdfplumber
from dotenv import load_dotenv
import statistics
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import warnings
import pypdf
warnings.filterwarnings('ignore')

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local"))

def create_ai_client():
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        print("⚠️ No GROQ_API_KEY found — AI features disabled.")
        return None, None
        
    if OpenAI is None:
        return None, None

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1", 
        api_key=groq_key
    )
    
    # Best for structured budget analysis
    model = "llama-3.3-70b-versatile"
    
    # Test the connection
    try:
        # client.models.list() is a simple way to test connectivity
        client.models.list()
        print(f"✅ Groq connected ({model})")
        return client, model
    except Exception as e:
        print(f"❌ Groq connection failed: {e}")
        return None, None

client, ai_model = create_ai_client()

# --- ALL 47 COUNTIES LIST ---
ALL_COUNTIES = [
    "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo Marakwet", "Embu", "Garissa", 
    "Homa Bay", "Isiolo", "Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi", 
    "Kirinyaga", "Kisii", "Kisumu", "Kitui", "Kwale", "Laikipia", "Lamu", 
    "Machakos", "Makueni", "Mandera", "Marsabit", "Meru", "Migori", "Mombasa", 
    "Murang'a", "Nairobi", "Nakuru", "Nandi", "Narok", "Nyamira", "Nyandarua", 
    "Nyeri", "Samburu", "Siaya", "Taita Taveta", "Tana River", "Tharaka Nithi", 
    "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
]

# --- County Name Normalization ---
COUNTY_NORMALIZATION = {
    "nairobi": "Nairobi", "nairobi city": "Nairobi", "nairobi city county": "Nairobi",
    "mombasa": "Mombasa", "kisumu": "Kisumu",
    "elgeyo marakwet": "Elgeyo Marakwet", "elgeyo": "Elgeyo Marakwet",
    "tharaka nithi": "Tharaka Nithi",
    "trans nzoia": "Trans Nzoia",
    "uasin gishu": "Uasin Gishu",
    "west pokot": "West Pokot",
    "tana river": "Tana River",
    "taita taveta": "Taita Taveta",
    "homabay": "Homa Bay", "homa bay": "Homa Bay",
    "muranga": "Murang'a",
    "tharakanithi": "Tharaka Nithi",
    "transnzoia": "Trans Nzoia",
    "uasingishu": "Uasin Gishu",
    "westpokot": "West Pokot",
    "tanariver": "Tana River",
    "taitataveta": "Taita Taveta"
}

def normalize_county_name(county_input: str) -> str:
    """Robust county name normalization."""
    if not county_input:
        return ""
    
    county_clean = county_input.lower().strip().replace("county", "").strip()
    
    if county_clean in COUNTY_NORMALIZATION:
        return COUNTY_NORMALIZATION[county_clean]
    
    # Try exact match
    for county in ALL_COUNTIES:
        if county.lower() == county_clean:
            return county
    
    # Partial match for multi-word counties
    for county in ALL_COUNTIES:
        county_words = county.lower().split()
        input_words = county_clean.split()
        # Check if first word matches (e.g., "elgeyo" matches "elgeyo marakwet")
        if input_words and county_words and input_words[0] == county_words[0]:
            return county
    
    return county_input.title()

# --- Enhanced Currency/Number Normalization ---
def normalize_currency(value: Any) -> int:
    """Handle Kshs, millions, billions, and various CGBIRR formats."""
    if value is None or value == "":
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    
    s = str(value).strip()
    
    # Extract number and multiplier separately
    # Patterns: "Kshs 4,880,829,952", "4.88 billion", "70 per cent", "70%"
    
    # Handle billions/millions with decimal
    billion_match = re.search(r'([\d\.]+)\s*billion', s, re.IGNORECASE)
    if billion_match:
        return int(float(billion_match.group(1)) * 1_000_000_000)
    
    million_match = re.search(r'([\d\.]+)\s*million', s, re.IGNORECASE)
    if million_match:
        return int(float(million_match.group(1)) * 1_000_000)
    
    # Remove all non-numeric except decimal point and minus
    # Keep digits, dots, commas
    s = re.sub(r'[^\d\.\-,]', '', s)
    
    # Handle accounting negatives (parentheses)
    if '(' in str(value) and ')' in str(value):
        s = '-' + s
    
    # Find the main number sequence
    numbers = re.findall(r'-?\d[\d,]*\.?\d*', s)
    if not numbers:
        return 0
    
    # Take the longest number (most significant)
    num_str = max(numbers, key=len).replace(',', '')
    
    try:
        return int(float(num_str))
    except:
        return 0

def normalize_percentage(value: Any) -> float:
    """Extract percentage from various formats."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    
    s = str(value).lower()
    # Match "70 per cent", "70%", "70.5%", etc.
    match = re.search(r'([\d\.]+)\s*(?:per cent|percent|%)', s)
    if match:
        return float(match.group(1))
    return 0.0

# --- Data Models ---
@dataclass
class RevenueData:
    osr_target: int = 0
    osr_actual: int = 0
    osr_performance_pct: float = 0.0  # Renamed for clarity
    fif_target: int = 0
    fif_actual: int = 0
    fif_performance_pct: float = 0.0
    equitable_share: int = 0
    total_conditional_grants: int = 0
    total_revenue: int = 0
    revenue_arrears: int = 0
    other_revenues: int = 0

@dataclass
class ExpenditureData:
    recurrent_exchequer: int = 0      # From CGBIRR Table 2.5
    recurrent_expenditure: int = 0
    dev_exchequer: int = 0            # Development budget/exchequer
    dev_expenditure: int = 0
    total_exchequer: int = 0
    total_expenditure: int = 0
    recurrent_absorption_pct: float = 0.0
    dev_absorption_pct: float = 0.0
    overall_absorption_pct: float = 0.0

@dataclass
class HealthFIFData:
    sha_approved: int = 0      # Table 2.2: SHA/SHIF Approved Claims
    sha_paid: int = 0          # Claims Paid
    sha_balance: int = 0       # Balance
    pending_debt: int = 0      # Pending Debt (Kshs.)
    payment_rate_pct: float = 0.0

@dataclass
class PendingBillsData:
    total_pending: int = 0
    under_one_year: int = 0
    one_to_two_years: int = 0
    two_to_three_years: int = 0
    over_three_years: int = 0
    
    def risk_flag(self) -> str:
        total = self.total_pending
        if total == 0:
            return "None"
        old_pct = (self.over_three_years / total) * 100 if total > 0 else 0
        if old_pct > 50:
            return "Critical"
        elif old_pct > 30:
            return "High"
        elif old_pct > 10:
            return "Moderate"
@dataclass
class CountyAnalysis:
    county_name: str
    financial_year: str = "2024/25"
    revenue: RevenueData = field(default_factory=RevenueData)
    expenditure: ExpenditureData = field(default_factory=ExpenditureData)
    pending_bills: PendingBillsData = field(default_factory=PendingBillsData)
    health_fif: HealthFIFData = field(default_factory=HealthFIFData)
    intelligence: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    key_metrics: Dict[str, str] = field(default_factory=dict)
    data_quality_score: float = 0.0  # How complete the data extraction was
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "county_name": self.county_name,
            "financial_year": self.financial_year,
            "revenue": self.revenue.__dict__,
            "expenditure": self.expenditure.__dict__,
            "pending_bills": {
                **self.pending_bills.__dict__,
                "ageing_risk": self.pending_bills.risk_flag()
            },
            "health_fif": self.health_fif.__dict__,
            "intelligence": self.intelligence,
            "key_metrics": self.key_metrics,
            "summary": self.summary,
            "data_quality_score": self.data_quality_score
        }

# --- AI Extraction Module ---
class AIBudgetExtractor:
    def __init__(self, client, model):
        self.client = client
        self.model = model
    
    def extract_county_data(self, pdf_bytes: bytes, county_name: str, pages_text: List[str], tables_cache: Dict[int, List]) -> Dict:
        """Stage 1: AI-Powered Data Extraction (Replaces Regex)"""
        # Find county-specific pages (usually 10-12 pages)
        start_page, end_page = self._find_county_page_range(pages_text, county_name)
        
        # If we can't find the county, we can't extract
        if start_page == -1:
            raise ValueError(f"Could not locate {county_name} in PDF")

        # Extract context
        raw_text = "\n".join(pages_text[start_page:end_page])
        
        # SPEED OPTIMIZATION: Crop PDF to just the relevant pages before opening with pdfplumber
        cropped_pdf_bytes = self._crop_pdf(pdf_bytes, start_page, end_page)
        
        # Extract tables from those pages as Markdown
        tables_md = ""
        with pdfplumber.open(io.BytesIO(cropped_pdf_bytes)) as pdf:
            for i in range(len(pdf.pages)):
                tables = pdf.pages[i].extract_tables()
                if tables:
                    for table in tables:
                        tables_md += self._table_to_markdown(table)

        # Build extraction prompt
        extraction_prompt = f"""
        You are the Data Extraction Module for the Kenya County Budget Transparency System.
        Extract structured financial data from the following CGBIRR document content for {county_name} County.
        
        Focus specifically on:
        - OSR Target vs Actual
        - Total Expenditure (Recurrent vs Development)
        - Pending Bills (Total and Ageing)
        - Revenue Arrears (Quantify the Kshs amount)
        - Health FIF (SHA Approved Claims, Paid, and Balance)
        
        Document Content Snippet:
        {raw_text[:12000]}
        
        Tables Found:
        {tables_md[:15000]}
        
        Extract and return ONLY this JSON structure:
        {{
            "county": "{county_name}",
            "fiscal_year": "2024/25",
            "revenue": {{
                "osr_target": <int or null>,
                "osr_actual": <int or null>,
                "equitable_share": <int or null>,
                "fif_target": <int or null>,
                "fif_actual": <int or null>,
                "total_revenue": <int or null>
            }},
            "expenditure": {{
                "recurrent_expenditure": <int or null>,
                "development_expenditure": <int or null>,
                "total_expenditure": <int or null>
            }},
            "debt": {{
                "pending_bills": <int or null>,
                "revenue_arrears": <int or null>,
                "pending_bills_ageing": {{
                    "under_one_year": <int or null>,
                    "one_to_two_years": <int or null>,
                    "two_to_three_years": <int or null>,
                    "over_three_years": <int or null>
                }}
            }},
            "health_fif": {{
                "sha_approved_claims": <int or null>,
                "claims_paid": <int or null>,
                "balance": <int or null>,
                "pending_debt": <int or null>
            }},
            "confidence_score": 0-100,
            "notes": "Any uncertainties or missing data"
        }}
        
        Rules:
        1. 🚨 **CRITICAL**: National Revenue Arrears are Kshs 13.75 Billion. **DO NOT** attribute this to {county_name}. Only extract arrears specifically labeled for this county.
        2. ONLY extract figures for {county_name} County. 
        3. Convert all amounts to integers (remove Kshs, commas, "million", "billion").
        4. If text says "4.88 Billion", return 4880000000. If it says "670 Million", return 670000000.
        5. DO NOT GUESS. If a value is missing, return null.
        6. DO NOT provide percentages (%) in your JSON.
        7. DO NOT concatenate numbers. 
        """
        
        # Call Groq/AI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise financial data extraction assistant. Return only valid JSON."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        extracted_data = json.loads(response.choices[0].message.content)
        print(f"DEBUG: Extracted data confidence: {extracted_data.get('confidence_score')}")
        
        # Stage 2: Immediately analyze the extracted data
        return self._analyze_extracted_data(extracted_data, raw_text)

    def _find_county_page_range(self, pages_text: List[str], county_name: str) -> Tuple[int, int]:
        """TOC-Aware search for county section."""
        # 1. Search for TOC entry to get the target page number
        toc_pattern = rf"3\.\d+\.\s+(?:County Government of )?{re.escape(county_name)}\s*\.*?\s*(\d+)"
        
        # Search in the first 20 pages (TOC area)
        toc_text = "\n".join(pages_text[:20])
        match = re.search(toc_pattern, toc_text, re.IGNORECASE)
        
        if match:
            target_page_num = int(match.group(1))
            # PDFs usually have some page offset, so search +/- 15 pages around the target
            start_search = max(20, target_page_num - 5) 
            end_search = min(len(pages_text), target_page_num + 30)
            
            header_pattern = rf"3\.\d+\.\s+(?:County Government of )?{re.escape(county_name)}"
            for i in range(start_search, end_search):
                if re.search(header_pattern, pages_text[i], re.IGNORECASE):
                    print(f"📍 Found {county_name} section start on page {i+1} (via TOC reference)")
                    return i, min(i + 15, len(pages_text))

        # 2. Fallback: Search all pages but skip TOC
        header_pattern = rf"3\.\d+\.\s+(?:County Government of )?{re.escape(county_name)}"
        for i in range(20, len(pages_text)):
            if re.search(header_pattern, pages_text[i], re.IGNORECASE):
                print(f"📍 Found {county_name} section start on page {i+1}")
                return i, min(i + 15, len(pages_text))
        
        return -1, -1

    def _table_to_markdown(self, table: List[List]) -> str:
        if not table: return ""
        md = ""
        for row in table:
            cells = [str(c).replace("\n", " ").strip() if c else "" for c in row]
            md += "| " + " | ".join(cells) + " |\n"
        md += "\n"
        return md

    def _crop_pdf(self, pdf_bytes: bytes, start_page: int, end_page: int) -> bytes:
        """Extracts specific pages from PDF to reduce size for table extraction."""
        print(f"✂️ Cropping PDF to pages {start_page+1}-{end_page}...")
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        writer = pypdf.PdfWriter()
        for i in range(start_page, min(end_page, len(reader.pages))):
            writer.add_page(reader.pages[i])
        
        out = io.BytesIO()
        writer.write(out)
        return out.getvalue()

    def _analyze_extracted_data(self, extracted_json: Dict, raw_context: str) -> Dict:
        """Stage 2: Analysis Using Extracted Figures"""
        
        # Internal Math Validation before analysis
        ext = extracted_json
        
        # Verify Revenue Shortfall
        rev = ext.get('revenue', {})
        target = rev.get('osr_target')
        actual = rev.get('osr_actual')
        if target and actual:
            shortfall = max(0, target - actual)
            ext['revenue']['calculated_shortfall'] = shortfall
            
        analysis_prompt = f"""
        Based on the VALIDATED extracted data for {extracted_json['county']} County.
        
        RULES:
        1. USE THE EXACT FIGURES PROVIDED. Do not hallucinate different numbers.
        2. QUANTIFY everything.
        3. If Arrears > 1 Billion for a single county, double check if you accidentally picked the national total (which is 13.75B). If the text says "County Government of {extracted_json['county']} has arrears of...", use that.
        
        Extracted Data:
        {json.dumps(extracted_json, indent=2)}
        
        Return ONLY a JSON object:
        {{
            "integrity_scores": {{ "transparency": 0-100, "compliance": 0-100, "overall": 0-100 }},
            "risk_level": "High|Moderate|Low",
            "risk_score": 0-100,
            "flags": ["list of specific issues"],
            "executive_summary": "Quantify OSR shortfall, total expenditure vs budget, pending bills, and specifically mention revenue arrears and Health FIF.",
            "recommendations": ["actionable items"]
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior financial auditor. Accuracy is life or death. Do not hallucinate."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        analysis_result = json.loads(response.choices[0].message.content)
        
        return {
            "extraction": extracted_json,
            "analysis": analysis_result,
            "processing_method": "AI Two-Stage (Llama 70B Verified)"
        }

# --- Core Analysis Engine ---
class CountyBudgetAnalyzer:
    """Optimized for CGBIRR August 2025 PDF structure."""
    
    def __init__(self, pdf_bytes: bytes, use_ai: bool = True):
        self.pdf_bytes = pdf_bytes
        self.full_text = ""
        self.pages_text = []
        self.tables_cache = {}
        self.health_fif_cache = None
        self.use_ai = use_ai and client is not None
        self.ai_extractor = AIBudgetExtractor(client, ai_model) if self.use_ai else None

    def _detect_pdf_type(self) -> str:
        """Detect if PDF is text-based or scanned."""
        with pdfplumber.open(io.BytesIO(self.pdf_bytes)) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            # If text is garbled or very short, likely scanned
            return "scanned" if len(text or "") < 100 else "text"
        
    def analyze_county(self, county_input: str) -> CountyAnalysis:
        """Main entry point for single county analysis."""
        county_name = normalize_county_name(county_input)
        
        if county_name not in ALL_COUNTIES:
            raise ValueError(f"County '{county_input}' not recognized. Did you mean one of: {self._suggest_counties(county_input)}?")
        
        # Lazy load PDF content if not already loaded
        if not self.full_text:
            self._load_pdf_content()

        if self.use_ai:
            print(f"🤖 Using Two-Stage AI pipeline for {county_name}...")
            try:
                ai_result = self.ai_extractor.extract_county_data(
                    self.pdf_bytes, 
                    county_name,
                    self.pages_text,
                    self.tables_cache
                )
                
                # Perform regex validation to prevent hallucinations
                ai_result = self._validate_with_regex(ai_result, county_name)
                
                return self._map_ai_result_to_analysis(ai_result, county_name)
            except Exception as e:
                print(f"⚠️ AI Pipeline failed: {e}. Falling back to Regex.")
                # Fallback to local regex if AI fails

        analysis = CountyAnalysis(county_name=county_name)
        
        # 1. Extract from Global Summary Tables (Table 2.1, 2.5, 2.9)
        self._extract_from_global_tables(analysis)
        
        # 2. Extract Health FIF from Table 2.2 (national summary)
        self._extract_health_fif(analysis)
        
        # 3. Extract from County-Specific Section (Chapter 3)
        self._extract_from_county_section(analysis)
        
        # 4. Cross-validate and calculate derived metrics
        self._calculate_derived_metrics(analysis)
        
        # 5. Generate intelligence and summary
        self._generate_intelligence(analysis)
        analysis.summary = self._generate_summary(analysis)
        analysis.key_metrics = self._prepare_key_metrics(analysis)
        
        # Calculate data quality score
        analysis.data_quality_score = self._calculate_data_quality(analysis)
        
        return analysis

    def _validate_with_regex(self, ai_result: Dict, county_name: str) -> Dict:
        """Cross-check AI extraction with regex heuristics to prevent hallucinations."""
        # Create a temp analysis object to run regex logic
        validation_analysis = CountyAnalysis(county_name=county_name)
        self._extract_from_global_tables(validation_analysis)
        
        # Compare OSR
        regex_osr = validation_analysis.revenue.osr_actual
        ai_osr = ai_result.get('extraction', {}).get('revenue', {}).get('osr_actual', 0) or 0
        
        if regex_osr > 0 and ai_osr > 0:
            variance = abs(regex_osr - ai_osr) / regex_osr
            if variance > 0.15: # > 15% difference
                print(f"⚠️ OSR Mismatch Detected: Regex={regex_osr}, AI={ai_osr}")
                ai_result['extraction']['revenue']['osr_actual'] = regex_osr # Prefer regex for hard figures
                ai_result['analysis']['flags'].append(f"🔍 Corrected OSR figure from {ai_osr:,} to {regex_osr:,} based on Table 2.1 cross-check")

        return ai_result

    def _map_ai_result_to_analysis(self, ai_result: Dict, county_name: str) -> CountyAnalysis:
        """Ground-Truth Hybrid: Regex for figures, AI for narrative intelligence."""
        ext = ai_result['extraction']
        ana = ai_result['analysis']
        
        # 1. ESTABLISH GROUND TRUTH FROM GLOBAL TABLES (Authority for figures)
        truth = CountyAnalysis(county_name=county_name)
        self._extract_from_global_tables(truth)
        self._extract_health_fif(truth)
        self._extract_from_county_section(truth)
        
        # 2. START WITH TRUTH
        analysis = truth
        
        # 3. MERGE AI DISCOVERY (If AI found something Regex missed, OR for narrative fields)
        # Revenue Arrears (AI is often better at finding this in the narrative)
        ai_arrears = self._ensure_int(ext.get('debt', {}).get('revenue_arrears'))
        if ai_arrears > 0 and (analysis.revenue.revenue_arrears == 0):
             # Filter out the 13.75B national total hallucination
             if not ("13.75" in str(ai_arrears) or "13745" in str(ai_arrears)):
                 analysis.revenue.revenue_arrears = ai_arrears

        # Health FIF details (AI better at SHA approved/paid details)
        hf = ext.get('health_fif', {})
        ai_sha_approved = self._ensure_int(hf.get('sha_approved_claims')) or self._ensure_int(hf.get('sha_approved'))
        ai_sha_paid = self._ensure_int(hf.get('claims_paid'))
        
        if ai_sha_approved > 0 and analysis.health_fif.sha_approved == 0:
            analysis.health_fif.sha_approved = ai_sha_approved
            analysis.health_fif.sha_paid = ai_sha_paid

        # 4. FINAL CALCULATIONS (Force Consistency)
        # Verify OSR Math
        if analysis.revenue.osr_target > 0:
            analysis.revenue.osr_performance_pct = round((analysis.revenue.osr_actual / analysis.revenue.osr_target) * 100, 1)

        # Absorption
        if analysis.expenditure.total_exchequer > 0:
            analysis.expenditure.overall_absorption_pct = min(round((analysis.expenditure.total_expenditure / analysis.expenditure.total_exchequer) * 100, 1), 100.0)
        if analysis.expenditure.dev_exchequer > 0:
            analysis.expenditure.dev_absorption_pct = min(round((analysis.expenditure.dev_expenditure / analysis.expenditure.dev_exchequer) * 100, 1), 100.0)
        
        if analysis.health_fif.sha_approved > 0:
             analysis.health_fif.payment_rate_pct = min(round((analysis.health_fif.sha_paid / analysis.health_fif.sha_approved) * 100, 1), 100.0)

        # 5. ATTACH AI INTELLIGENCE
        analysis.summary = ana.get('executive_summary', "")
        analysis.intelligence = {
            "risk_score": ana.get('risk_score', 0),
            "risk_level": ana.get('risk_level', "Unknown"),
            "flags": ana.get('flags', []),
            "integrity_scores": ana.get('integrity_scores', {}),
            "recommendations": ana.get('recommendations', [])
        }
        
        # Identify discrepancies between Ground Truth and AI Extraction as flags
        if abs(analysis.revenue.osr_actual - self._ensure_int(ext.get('revenue', {}).get('osr_actual', 0))) > 1_000_000:
             analysis.intelligence["flags"].append(f"🔍 Adjusted AI OSR figure to match official Table 2.1 Ground Truth")

        analysis.data_quality_score = self._calculate_data_quality(analysis)
        analysis.key_metrics = self._prepare_key_metrics(analysis)
        
        return analysis

    def _ensure_int(self, val: Any) -> int:
        """Robust conversion to int, handling strings, nulls, and scientific notation."""
        if val is None or val == "":
            return 0
        try:
            if isinstance(val, str):
                # Remove common non-numeric chars
                val = val.replace(',', '').replace('Kshs', '').replace('Ksh', '').strip()
                # Handle millions/billions in string
                if 'b' in val.lower(): return int(float(val.lower().replace('b', '')) * 1e9)
                if 'm' in val.lower(): return int(float(val.lower().replace('m', '')) * 1e6)
            return int(float(val))
        except:
            return 0
    
    def _load_pdf_content(self):
        """Fast text extraction with pypdf + selective table extraction with pdfplumber."""
        print("📖 Loading PDF content (Fast Mode)...")
        
        # 1. Fast text extraction for all pages
        reader = pypdf.PdfReader(io.BytesIO(self.pdf_bytes))
        for page in reader.pages:
            self.pages_text.append(page.extract_text() or "")
        
        # 2. Selective table extraction for global tables (first 20 pages usually suffice)
        with pdfplumber.open(io.BytesIO(self.pdf_bytes)) as pdf:
            max_table_pages = min(20, len(pdf.pages))
            for i in range(max_table_pages):
                tables = pdf.pages[i].extract_tables()
                if tables:
                    self.tables_cache[i] = tables
        
        self.full_text = "\n".join(self.pages_text)
        print(f"✅ Loaded {len(self.pages_text)} pages text & tables from first 20 pages")
    
    def _extract_from_global_tables(self, analysis: CountyAnalysis):
        """Extract from Table 2.1 (OSR), 2.5 (Absorption), 2.9 (Pending Bills)."""
        county = analysis.county_name
        
        # --- Table 2.1: Own Source Revenue Performance ---
        # Pattern: County Name* | Target | Actual | Shortfall | Perf %
        # Mombasa* 6,935.16 4,884.50 2,050.66 70.4
        t21_pattern = rf"{re.escape(county)}\*?\s+([\d\.,]+)\s+([\d\.,]+)\s+[\d\.,]*\s+([\d\.]+)"
        t21_match = re.search(t21_pattern, self.full_text, re.IGNORECASE)
        if t21_match:
            target = normalize_currency(t21_match.group(1))
            actual = normalize_currency(t21_match.group(2))
            
            if target > 1_000_000_000:  # Likely OSR
                analysis.revenue.osr_target = target
                analysis.revenue.osr_actual = actual
            else:  # Likely FIF
                analysis.revenue.fif_target = target
                analysis.revenue.fif_actual = actual
        
        # --- Table 2.5: Budget Allocations and Absorption ---
        # County | Rec Exch | Dev Exch | Total Exch | Rec Exp | Dev Exp | Total Exp | Dev Abs % | Overall Abs %
        # Mombasa 11,213.63 6,366.52 17,580.15 8,913.39 4,001.21 12,914.60 62.8 73.5
        t25_pattern = rf"{re.escape(county)}\*?\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.]+)\s+([\d\.]+)"
        t25_match = re.search(t25_pattern, self.full_text, re.IGNORECASE)
        if t25_match:
            analysis.expenditure.recurrent_exchequer = normalize_currency(t25_match.group(1))
            analysis.expenditure.dev_exchequer = normalize_currency(t25_match.group(2))
            analysis.expenditure.total_exchequer = normalize_currency(t25_match.group(3))
            analysis.expenditure.recurrent_expenditure = normalize_currency(t25_match.group(4))
            analysis.expenditure.dev_expenditure = normalize_currency(t25_match.group(5))
            analysis.expenditure.total_expenditure = normalize_currency(t25_match.group(6))
            analysis.expenditure.dev_absorption_pct = float(t25_match.group(7))
            analysis.expenditure.overall_absorption_pct = float(t25_match.group(8))
        
        # --- Table 2.9: Pending Bills ---
        # Columns: County | Recurrent | Development | Total | <1yr | 1-2yr | 2-3yr | >3yr
        t29_pattern = rf"{re.escape(county)}\*?\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)?\s*([\d\.,]+)?\s*([\d\.,]+)?\s*([\d\.,]+)?"
        t29_match = re.search(t29_pattern, self.full_text, re.IGNORECASE)
        if t29_match:
            analysis.pending_bills.total_pending = normalize_currency(t29_match.group(3))
            if t29_match.group(7):
                analysis.pending_bills.over_three_years = normalize_currency(t29_match.group(7))
    
    def _extract_health_fif(self, analysis: CountyAnalysis):
        """Extract from Table 2.2 (National Health FIF Summary)."""
        if self.health_fif_cache:
            fif_data = self.health_fif_cache.get(analysis.county_name, {})
            if fif_data:
                analysis.health_fif = HealthFIFData(**fif_data)
            return
        
        # Find Table 2.2
        # Pattern: County | SHA Approved | Claims Paid | Balance | Pending Debt
        t22_start = self.full_text.find("Table 2.2")
        t22_end = self.full_text.find("Table 2.3") if "Table 2.3" in self.full_text else len(self.full_text)
        t22_text = self.full_text[t22_start:t22_end]
        
        fif_dict = {}
        # Match each county in the table
        for county in ALL_COUNTIES:
            # Handle special characters in county names
            county_escaped = re.escape(county)
            pattern = rf"{county_escaped}\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)"
            match = re.search(pattern, t22_text, re.IGNORECASE)
            if match:
                approved = normalize_currency(match.group(1))
                paid = normalize_currency(match.group(2))
                balance = normalize_currency(match.group(3))
                pending = normalize_currency(match.group(4))
                
                fif_dict[county] = {
                    'sha_approved': approved,
                    'sha_paid': paid,
                    'sha_balance': balance,
                    'pending_debt': pending,
                    'payment_rate_pct': round((paid/approved)*100, 1) if approved > 0 else 0.0
                }
        
        self.health_fif_cache = fif_dict
        
        if analysis.county_name in fif_dict:
            data = fif_dict[analysis.county_name]
            analysis.health_fif = HealthFIFData(**data)
    
    def _extract_from_county_section(self, analysis: CountyAnalysis):
        """Extract detailed narrative from Chapter 3 county sections."""
        county = analysis.county_name
        
        # Find the county section: "3.X. County Government of [Name]"
        section_pattern = rf"3\.\d+\.\s+County Government of {re.escape(county)}.*?(?=3\.\d+\.\s+County Government of |\Z)"
        section_match = re.search(section_pattern, self.full_text, re.IGNORECASE | re.DOTALL)
        
        if not section_match:
            return
        
        section_text = section_match.group(0)
        
        # Extract Revenue Arrears (often mentioned in narrative)
        arrears_pattern = rf"{re.escape(county)}.*?revenue arrears.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?"
        arrears_match = re.search(arrears_pattern, section_text, re.IGNORECASE)
        if arrears_match:
            analysis.revenue.revenue_arrears = normalize_currency(arrears_match.group(1))
        
        # Extract Equitable Share mention
        eq_pattern = rf"equitable share.*?Kshs\.?\s*([\d\.,]+)"
        eq_match = re.search(eq_pattern, section_text, re.IGNORECASE)
        if eq_match and not analysis.revenue.equitable_share:
            analysis.revenue.equitable_share = normalize_currency(eq_match.group(1))
        
        # Extract conditional grants total
        cg_pattern = rf"conditional grants.*?total.*?Kshs\.?\s*([\d\.,]+)|total.*?conditional grants.*?Kshs\.?\s*([\d\.,]+)"
        cg_match = re.search(cg_pattern, section_text, re.IGNORECASE)
        if cg_match:
            val = cg_match.group(1) or cg_match.group(2)
            analysis.revenue.total_conditional_grants = normalize_currency(val)
        
        # Extract development expenditure from narrative if missing
        if not analysis.expenditure.dev_expenditure:
            dev_exp_pattern = rf"development expenditure.*?Kshs\.?\s*([\d\.,]+)"
            dev_match = re.search(dev_exp_pattern, section_text, re.IGNORECASE)
            if dev_match:
                analysis.expenditure.dev_expenditure = normalize_currency(dev_match.group(1))
    
    def _calculate_derived_metrics(self, analysis: CountyAnalysis):
        """Calculate totals and validate consistency."""
        rev = analysis.revenue
        exp = analysis.expenditure
        
        # Calculate total revenue
        if not rev.total_revenue:
            rev.total_revenue = rev.osr_actual + rev.equitable_share + rev.total_conditional_grants
        
        # Calculate total exchequer if not set
        if not exp.total_exchequer and (exp.recurrent_exchequer or exp.dev_exchequer):
            exp.total_exchequer = exp.recurrent_exchequer + exp.dev_exchequer
        
        # Calculate total expenditure if not set
        if not exp.total_expenditure and (exp.recurrent_expenditure or exp.dev_expenditure):
            exp.total_expenditure = exp.recurrent_expenditure + exp.dev_expenditure
        
        # Calculate absorption rates if missing
        if not exp.recurrent_absorption_pct and exp.recurrent_exchequer > 0:
            exp.recurrent_absorption_pct = (exp.recurrent_expenditure / exp.recurrent_exchequer) * 100
        
        if not exp.dev_absorption_pct and exp.dev_exchequer > 0:
            exp.dev_absorption_pct = (exp.dev_expenditure / exp.dev_exchequer) * 100
        
        if not exp.overall_absorption_pct and exp.total_exchequer > 0:
            exp.overall_absorption_pct = (exp.total_expenditure / exp.total_exchequer) * 100
    
    def _generate_intelligence(self, analysis: CountyAnalysis):
        """Generate fiscal intelligence and red flags."""
        intelligence = {
            "risk_score": 0,
            "risk_level": "Low",
            "flags": [],
            "strengths": [],
            "recommendations": []
        }
        
        score = 0
        
        # OSR Risk
        if analysis.revenue.osr_performance_pct < 50:
            score += 25
            intelligence["flags"].append(f"🔴 Critical OSR performance ({analysis.revenue.osr_performance_pct:.0f}%)")
        elif analysis.revenue.osr_performance_pct < 70:
            score += 15
            intelligence["flags"].append(f"🟡 Low OSR performance ({analysis.revenue.osr_performance_pct:.0f}%)")
        elif analysis.revenue.osr_performance_pct >= 100:
            intelligence["strengths"].append(f"✅ Excellent OSR performance ({analysis.revenue.osr_performance_pct:.0f}%)")
        
        # Development Absorption Risk
        if analysis.expenditure.dev_absorption_pct < 30:
            score += 30
            intelligence["flags"].append(f"🔴 Critical dev absorption ({analysis.expenditure.dev_absorption_pct:.0f}%)")
        elif analysis.expenditure.dev_absorption_pct < 60:
            score += 15
            intelligence["flags"].append(f"🟡 Low dev absorption ({analysis.expenditure.dev_absorption_pct:.0f}%)")
        elif analysis.expenditure.dev_absorption_pct >= 80:
            intelligence["strengths"].append(f"✅ Strong dev absorption ({analysis.expenditure.dev_absorption_pct:.0f}%)")
        
        # Pending Bills Risk (relative to budget)
        if analysis.expenditure.total_exchequer > 0:
            bills_ratio = analysis.pending_bills.total_pending / analysis.expenditure.total_exchequer
            if bills_ratio > 0.4:
                score += 25
                intelligence["flags"].append(f"🔴 High pending bills ({bills_ratio:.1%} of budget)")
            elif bills_ratio > 0.2:
                score += 10
                intelligence["flags"].append(f"🟡 Moderate pending bills ({bills_ratio:.1%} of budget)")
        
        # Health FIF Risk
        if analysis.health_fif.payment_rate_pct < 50 and analysis.health_fif.sha_approved > 0:
            intelligence["flags"].append(f"⚠️ Low SHA payment rate ({analysis.health_fif.payment_rate_pct:.0f}%)")
        
        # Revenue Arrears
        if analysis.revenue.revenue_arrears > 1_000_000_000:
            intelligence["flags"].append(f"⚠️ High revenue arrears (Ksh {analysis.revenue.revenue_arrears/1_000_000_000:.1f}B)")
        
        # Set risk level
        intelligence["risk_score"] = min(score, 100)
        if score >= 60:
            intelligence["risk_level"] = "🔴 High"
        elif score >= 30:
            intelligence["risk_level"] = "🟡 Moderate"
        else:
            intelligence["risk_level"] = "🟢 Low"
        
        # Recommendations
        if analysis.revenue.osr_performance_pct < 70:
            intelligence["recommendations"].append("Review revenue mobilization strategies")
        if analysis.expenditure.dev_absorption_pct < 60:
            intelligence["recommendations"].append("Accelerate development project implementation")
        if analysis.pending_bills.total_pending > 0:
            intelligence["recommendations"].append("Prioritize settlement of pending bills")
        if analysis.health_fif.payment_rate_pct < 80:
            intelligence["recommendations"].append("Improve SHA claims processing efficiency")
        
        analysis.intelligence = intelligence
    
    def _generate_summary(self, analysis: CountyAnalysis) -> str:
        """Generate formatted summary."""
        r = analysis.revenue
        e = analysis.expenditure
        pb = analysis.pending_bills
        hf = analysis.health_fif
        intel = analysis.intelligence
        
        def fmt(val):
            if val >= 1_000_000_000:
                return f"Ksh {val/1_000_000_000:.2f}B"
            elif val >= 1_000_000:
                return f"Ksh {val/1_000_000:.0f}M"
            return f"Ksh {val:,}"
        
        summary = f"""# 🏛️ {analysis.county_name} County Budget Analysis (FY {analysis.financial_year})

**Risk Assessment**: {intel['risk_level']} ({intel['risk_score']}/100)

## 💰 Revenue
- **OSR**: {fmt(r.osr_actual)} / {fmt(r.osr_target)} ({r.osr_performance_pct:.0f}%)
- **Equitable Share**: {fmt(r.equitable_share)}
- **Total Revenue**: {fmt(r.total_revenue)}
- **Revenue Arrears**: {fmt(r.revenue_arrears)}

## 📈 Expenditure
- **Total Expenditure**: {fmt(e.total_expenditure)} / {fmt(e.total_exchequer)} ({e.overall_absorption_pct:.0f}%)
- **Development**: {fmt(e.dev_expenditure)} ({e.dev_absorption_pct:.0f}% absorbed)
- **Recurrent**: {fmt(e.recurrent_expenditure)}

## 🚨 Liabilities
- **Pending Bills**: {fmt(pb.total_pending)} (Risk: {pb.risk_flag()})
- **SHA Claims**: {fmt(hf.sha_approved)} approved, {fmt(hf.sha_paid)} paid ({hf.payment_rate_pct:.0f}%)"""
        
        if intel['flags']:
            summary += "\n\n## ⚠️ Red Flags\n" + "\n".join(f"- {f}" for f in intel['flags'])
        if intel['strengths']:
            summary += "\n\n## ✅ Strengths\n" + "\n".join(f"- {s}" for s in intel['strengths'])
        if intel['recommendations']:
            summary += "\n\n## 💡 Recommendations\n" + "\n".join(f"- {r}" for r in intel['recommendations'])
        
        return summary
    
    def _prepare_key_metrics(self, analysis: CountyAnalysis) -> Dict[str, str]:
        """Prepare display metrics."""
        def fmt(val):
            if val >= 1_000_000_000:
                return f"{val/1_000_000_000:.2f}B"
            elif val >= 1_000_000:
                return f"{val/1_000_000:.0f}M"
            return f"{val:,}"
        
        return {
            "County": analysis.county_name,
            "OSR Perf": f"{analysis.revenue.osr_performance_pct:.0f}%",
            "Total Exp": fmt(analysis.expenditure.total_expenditure),
            "Absorption": f"{analysis.expenditure.overall_absorption_pct:.0f}%",
            "Dev Abs": f"{analysis.expenditure.dev_absorption_pct:.0f}%",
            "Pending": fmt(analysis.pending_bills.total_pending),
            "Risk Score": f"{analysis.intelligence.get('risk_score', 0)}/100",
            "Data Quality": f"{analysis.data_quality_score:.0f}%"
        }
    
    def _calculate_data_quality(self, analysis: CountyAnalysis) -> float:
        """Calculate completeness of data extraction."""
        fields = [
            analysis.revenue.osr_actual > 0,
            analysis.revenue.equitable_share > 0,
            analysis.expenditure.total_expenditure > 0,
            analysis.expenditure.dev_absorption_pct > 0,
            analysis.pending_bills.total_pending > 0,
            analysis.health_fif.sha_approved > 0
        ]
        return (sum(fields) / len(fields)) * 100
    
    def _suggest_counties(self, input_str: str) -> List[str]:
        """Suggest closest county matches."""
        input_lower = input_str.lower()
        suggestions = []
        for county in ALL_COUNTIES:
            if input_lower in county.lower() or county.lower() in input_lower:
                suggestions.append(county)
            elif input_lower[:3] == county.lower()[:3]:
                suggestions.append(county)
        return suggestions[:3]

# --- Public API Functions ---
def analyze_county_budget(pdf_path: str, county_name: str) -> Dict[str, Any]:
    """
    Analyze a single county from CGBIRR PDF.
    
    Args:
        pdf_path: Path to CGBIRR PDF file
        county_name: Name of county (e.g., "Mombasa", "Nairobi")
    
    Returns:
        Dictionary with complete analysis
    """
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        analyzer = CountyBudgetAnalyzer(pdf_bytes)
        analysis = analyzer.analyze_county(county_name)
        
        return {
            "success": True,
            "data": analysis.to_dict(),
            "summary": analysis.summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Try county names like: Mombasa, Nairobi, Kisumu, Kiambu, Nakuru"
        }

def analyze_all_counties(pdf_path: str) -> Dict[str, Any]:
    """Analyze all 47 counties and return comparative data."""
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    analyzer = CountyBudgetAnalyzer(pdf_bytes)
    results = {}
    
    print(f"🔍 Analyzing all 47 counties...")
    for i, county in enumerate(ALL_COUNTIES, 1):
        try:
            analysis = analyzer.analyze_county(county)
            results[county] = {
                "success": True,
                "risk_score": analysis.intelligence.get('risk_score', 0),
                "osr_perf": analysis.revenue.osr_performance_pct,
                "dev_abs": analysis.expenditure.dev_absorption_pct,
                "pending_bills": analysis.pending_bills.total_pending,
                "data_quality": analysis.data_quality_score
            }
            print(f"  {i:2d}. {county:<20} Risk: {analysis.intelligence.get('risk_score', 0):2d}/100 | Data: {analysis.data_quality_score:.0f}%")
        except Exception as e:
            results[county] = {"success": False, "error": str(e)}
            print(f"  {i:2d}. {county:<20} ❌ Failed")
    
    return {
        "total": len(ALL_COUNTIES),
        "successful": sum(1 for r in results.values() if r.get('success')),
        "results": results,
        "top_risky": sorted(
            [(c, r['risk_score']) for c, r in results.items() if r.get('success')],
            key=lambda x: x[1],
            reverse=True
        )[:5]
    }

def run_pipeline(pdf_bytes: bytes, county: str) -> Dict[str, Any]:
    """Compatibility interface for FastAPI main.py."""
    analyzer = CountyBudgetAnalyzer(pdf_bytes)
    try:
        analysis = analyzer.analyze_county(county)
        data = analysis.to_dict()
        
        # Map fields to match what the frontend (analysis-module.tsx) expects
        # 1. summary_text
        data["summary_text"] = data["summary"]
        
        # 2. transparency_risk_score (from intelligence.risk_score)
        if "intelligence" in data and "risk_score" in data["intelligence"]:
            data["intelligence"]["transparency_risk_score"] = data["intelligence"]["risk_score"]
            data["intelligence"]["flags"] = data["intelligence"].get("flags", [])
        
        # 3. Method tag
        data["method"] = "Local (AI-Enhanced)" if analyzer.use_ai else "Local (Precision Regex)"
        data["status"] = "success"
        data["county"] = analysis.county_name # Frontend expects 'county'
        
        return data
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "county": county,
            "key_metrics": {}
        }

# --- Example Usage ---
if __name__ == "__main__":
    # Example: Analyze Mombasa specifically
    result = analyze_county_budget("CGBIRR August 2025.pdf", "Mombasa")
    
    if result['success']:
        print("\n" + "="*60)
        print(result['summary'])
        print("="*60)
        
        # Show key metrics
        metrics = result['data']['key_metrics']
        print("\n📊 Key Metrics:")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
    else:
        print(f"❌ Error: {result['error']}")
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
from dataclasses import dataclass
from enum import Enum

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local"))

def create_ai_client():
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if OpenAI is None:
        print("⚠️ OpenAI library not installed — skipping AI summarization.")
        return None, None

    if groq_key:
        print("🤖 Using Groq API for summarization.")
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_key)
        model = "meta-llama/llama-4-maverick-17b-128e-instruct"
    elif openai_key:
        print("🤖 Using OpenAI API for summarization.")
        client = OpenAI(api_key=openai_key)
        model = "gpt-3.5-turbo"
    else:
        print("⚠️ No API key found — skipping AI summarization.")
        return None, None

    return client, model

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
    # Handle special cases, abbreviations, variations
    "nairobi": "Nairobi",
    "nairobi city": "Nairobi",
    "nairobi city county": "Nairobi",
    "mombasa": "Mombasa",
    "kisumu": "Kisumu",
    "elgeyo marakwet": "Elgeyo Marakwet",
    "tharaka nithi": "Tharaka Nithi",
    "trans nzoia": "Trans Nzoia",
    "uasin gishu": "Uasin Gishu",
    "west pokot": "West Pokot",
    "tana river": "Tana River",
    "taita taveta": "Taita Taveta",
    "homabay": "Homa Bay",
    "muranga": "Murang'a",
    "nyeri": "Nyeri",
    "kisii": "Kisii",
    "kakamega": "Kakamega",
    "kiambu": "Kiambu",
    "kilifi": "Kilifi",
    "kirinyaga": "Kirinyaga",
    "kitui": "Kitui",
    "kwale": "Kwale",
    "laikipia": "Laikipia",
    "lamu": "Lamu",
    "machakos": "Machakos",
    "makueni": "Makueni",
    "mandera": "Mandera",
    "marsabit": "Marsabit",
    "meru": "Meru",
    "migori": "Migori",
    "nakuru": "Nakuru",
    "nandi": "Nandi",
    "narok": "Narok",
    "nyamira": "Nyamira",
    "nyandarua": "Nyandarua",
    "samburu": "Samburu",
    "siaya": "Siaya",
    "turkana": "Turkana",
    "vihiga": "Vihiga",
    "wajir": "Wajir"
}

def normalize_county_name(county_input: str) -> str:
    """Normalize county name input to standard format."""
    if not county_input:
        return ""
    
    county_lower = county_input.lower().strip()
    
    # Check normalization dictionary first
    if county_lower in COUNTY_NORMALIZATION:
        return COUNTY_NORMALIZATION[county_lower]
    
    # Try exact match with all counties
    for county in ALL_COUNTIES:
        if county.lower() == county_lower:
            return county
    
    # Try partial match
    for county in ALL_COUNTIES:
        if county_lower in county.lower() or county.lower() in county_lower:
            return county
    
    # Try removing "county" suffix
    county_clean = re.sub(r'\s+county$', '', county_lower, flags=re.IGNORECASE)
    for county in ALL_COUNTIES:
        if county.lower() == county_clean:
            return county
    
    # Return original with title case if all else fails
    return county_input.title()

# --- Enhanced Currency Normalization ---
num_re = re.compile(r"[-+]?\d{1,3}(?:[,\d{3}])*?(?:\.\d+)?")

def normalize_currency(value: Any) -> int:
    """Enhanced currency normalization supporting multiple formats."""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str):
        return 0
    
    s = str(value).strip()
    if s == "":
        return 0
    
    # Remove currency labels
    s = s.replace("Kshs", "").replace("KSh", "").replace("Ksh", "").replace("KSH", "")
    s = s.replace("KShs", "").replace("kshs", "").replace("KES", "").replace("Kshs.", "")
    
    # Handle billion/million notation
    if "billion" in s.lower() or "bil" in s.lower() or "b" in s.lower():
        multiplier = 1000000000
        # Extract number
        num_match = re.search(r'[\d\.,]+', s)
        if num_match:
            try:
                num = float(num_match.group().replace(',', ''))
                return int(num * multiplier)
            except:
                pass
    
    if "million" in s.lower() or "mil" in s.lower() or "m" in s.lower():
        multiplier = 1000000
        num_match = re.search(r'[\d\.,]+', s)
        if num_match:
            try:
                num = float(num_match.group().replace(',', ''))
                return int(num * multiplier)
            except:
                pass
    
    # Handle accounting format (parentheses = negative)
    s = s.replace("(", "-").replace(")", "")
    
    # Remove non-numeric except comma, dot, minus
    s = re.sub(r"[^\d\-,.\s]", "", s)
    
    # Find all number-like patterns
    matches = re.findall(r"-?\d[\d,]*\.?\d*", s)
    if not matches:
        return 0
    
    # Take the longest match (most likely the actual number)
    m = max(matches, key=len)
    m = m.replace(",", "")
    
    try:
        if "." in m:
            val = Decimal(m)
            return int(round(val))
        return int(m)
    except (ValueError, Exception):
        return 0

def find_first_number_in_text(text: str) -> Optional[int]:
    """Extract first number from text."""
    m = num_re.search(text or "")
    return int(m.group(0).replace(",", "")) if m else None

# --- Data Models ---
@dataclass
class RevenueData:
    """Revenue information for a county."""
    osr_target: int = 0
    osr_actual: int = 0
    fif_target: int = 0
    fif_actual: int = 0
    equitable_share: int = 0
    conditional_grants: int = 0
    total_revenue: int = 0
    performance_percent: float = 0.0
    revenue_arrears: int = 0

@dataclass
class ExpenditureData:
    """Expenditure information for a county."""
    recurrent_budget: int = 0
    recurrent_expenditure: int = 0
    development_budget: int = 0
    development_expenditure: int = 0
    total_budget: int = 0
    total_expenditure: int = 0
    absorption_rate_percent: float = 0.0
    dev_absorption_percent: float = 0.0
    overall_absorption_percent: float = 0.0

@dataclass
class DebtData:
    """Debt and liabilities information."""
    pending_bills: int = 0
    revenue_arrears: int = 0
    pending_bills_ageing: Dict[str, int] = None
    
    def __post_init__(self):
        if self.pending_bills_ageing is None:
            self.pending_bills_ageing = {
                "under_one_year": 0,
                "one_to_two_years": 0,
                "two_to_three_years": 0,
                "over_three_years": 0
            }

@dataclass
class CountyAnalysis:
    """Complete analysis for a county."""
    county_name: str
    financial_year: str = "2024/25"
    revenue: RevenueData = None
    expenditure: ExpenditureData = None
    debt: DebtData = None
    intelligence: Dict[str, Any] = None
    summary: str = ""
    key_metrics: Dict[str, str] = None
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.revenue is None:
            self.revenue = RevenueData()
        if self.expenditure is None:
            self.expenditure = ExpenditureData()
        if self.debt is None:
            self.debt = DebtData()
        if self.intelligence is None:
            self.intelligence = {}
        if self.key_metrics is None:
            self.key_metrics = {}
        if self.raw_data is None:
            self.raw_data = {}

# --- Main Analysis Engine ---
class CountyBudgetAnalyzer:
    """Dynamic analyzer for all 47 counties."""
    
    def __init__(self, pdf_bytes: bytes):
        self.pdf_bytes = pdf_bytes
        self.full_text = ""
        self.pages = []
        self.county_sections = {}
        self.global_tables = {}
        self._cache = {}
        
    def analyze_county(self, county_input: str) -> CountyAnalysis:
        """Analyze a specific county."""
        # Normalize county name
        county_name = normalize_county_name(county_input)
        
        if county_name not in ALL_COUNTIES:
            # Try to find closest match
            closest = self._find_closest_county(county_input)
            if closest:
                county_name = closest
                print(f"⚠️ Using '{county_name}' instead of '{county_input}'")
            else:
                raise ValueError(f"County '{county_input}' not found. Available counties: {', '.join(ALL_COUNTIES)}")
        
        print(f"🔍 Analyzing {county_name} County...")
        
        # Initialize analysis object
        analysis = CountyAnalysis(county_name=county_name)
        
        # Extract full text if not already done
        if not self.full_text:
            self._extract_full_text()
        
        # Find county section
        section = self._find_county_section(county_name)
        
        if section:
            print(f"✅ Found detailed section for {county_name}")
            self._extract_from_section(section, analysis)
        else:
            print(f"⚠️ No detailed section found, using global tables")
        
        # Extract from global tables (Table 2.1, 2.5, 2.9)
        self._extract_from_global_tables(analysis)
        
        # Extract from summary tables
        self._extract_from_summary_tables(analysis)
        
        # Calculate derived metrics
        self._calculate_derived_metrics(analysis)
        
        # Generate intelligence
        self._generate_intelligence(analysis)
        
        # Generate summary
        analysis.summary = self._generate_summary(analysis)
        
        # Prepare key metrics
        analysis.key_metrics = self._prepare_key_metrics(analysis)
        
        return analysis
    
    def analyze_multiple_counties(self, counties: List[str]) -> Dict[str, CountyAnalysis]:
        """Analyze multiple counties."""
        results = {}
        
        for county in counties:
            try:
                analysis = self.analyze_county(county)
                results[county] = analysis
            except Exception as e:
                print(f"❌ Error analyzing {county}: {str(e)}")
                results[county] = None
        
        return results
    
    def analyze_all_counties(self) -> Dict[str, CountyAnalysis]:
        """Analyze all 47 counties."""
        return self.analyze_multiple_counties(ALL_COUNTIES)
    
    def _extract_full_text(self):
        """Extract all text from PDF."""
        print("📖 Extracting text from PDF...")
        with pdfplumber.open(io.BytesIO(self.pdf_bytes)) as pdf:
            self.pages = list(pdf.pages)
            for i, page in enumerate(self.pages):
                text = page.extract_text()
                self.full_text += f"\n--- Page {i+1} ---\n{text}"
        
        # Pre-process for faster searching
        self._preprocess_text()
    
    def _preprocess_text(self):
        """Pre-process text for faster searching."""
        # Find all county sections
        county_section_pattern = r"3\.\d+\.\s+County Government of (.*?)\s*\n"
        sections = re.split(county_section_pattern, self.full_text)
        
        if len(sections) > 1:
            # First element is text before first county
            for i in range(1, len(sections), 2):
                if i < len(sections):
                    county_name = sections[i].strip()
                    section_text = sections[i+1] if i+1 < len(sections) else ""
                    
                    # Normalize county name
                    normalized = normalize_county_name(county_name)
                    if normalized in ALL_COUNTIES:
                        self.county_sections[normalized] = section_text
    
    def _find_county_section(self, county_name: str) -> Optional[str]:
        """Find section for a specific county."""
        # Check cache first
        if county_name in self.county_sections:
            return self.county_sections[county_name]
        
        # Try alternative patterns
        patterns = [
            rf"3\.\d+\.\s+County Government of {re.escape(county_name)}.*?(?=3\.\d+\.\s+County Government of|\Z)",
            rf"Table.*?{re.escape(county_name)}.*County.*?(?=Table\s+\d+\.|\Z)",
            rf"{re.escape(county_name)} County.*?(?=\n\d+\.\s+|\Z)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        
        return None
    
    def _find_closest_county(self, county_input: str) -> Optional[str]:
        """Find closest matching county name."""
        input_lower = county_input.lower()
        
        # Try simple contains
        for county in ALL_COUNTIES:
            if input_lower in county.lower() or county.lower() in input_lower:
                return county
        
        # Try fuzzy matching on first word
        input_first = input_lower.split()[0] if ' ' in input_lower else input_lower
        for county in ALL_COUNTIES:
            county_first = county.lower().split()[0]
            if county_first.startswith(input_first) or input_first.startswith(county_first):
                return county
        
        return None
    
    def _extract_from_section(self, section_text: str, analysis: CountyAnalysis):
        """Extract data from county-specific section."""
        # Revenue patterns
        revenue_patterns = {
            "osr_target": r"Ordinary OSR Target.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "osr_actual": r"Ordinary OSR Actual.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "fif_target": r"FIF.*?Target.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "fif_actual": r"FIF.*?Actual.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "total_osr": r"Total OSR.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "equitable_share": r"equitable share.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "conditional_grants": r"conditional.*?grant.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "revenue_performance": r"performance.*?(\d+) per cent",
            "revenue_arrears": r"revenue.*?arrears.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?"
        }
        
        for key, pattern in revenue_patterns.items():
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            if matches:
                if "per cent" in key:
                    setattr(analysis.revenue, "performance_percent", float(matches[0]))
                else:
                    value = normalize_currency(matches[0])
                    if "arrears" in key:
                        analysis.debt.revenue_arrears = value
                    elif "osr_target" == key:
                        analysis.revenue.osr_target = value
                    elif "osr_actual" == key:
                        analysis.revenue.osr_actual = value
                    elif "fif_target" == key:
                        analysis.revenue.fif_target = value
                    elif "fif_actual" == key:
                        analysis.revenue.fif_actual = value
                    elif "equitable_share" == key:
                        analysis.revenue.equitable_share = value
                    elif "conditional_grants" == key:
                        analysis.revenue.conditional_grants = value
        
        # Expenditure patterns
        exp_patterns = {
            "recurrent_budget": r"Recurrent.*?budget.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "recurrent_expenditure": r"Recurrent.*?expenditure.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "development_budget": r"Development.*?budget.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "development_expenditure": r"Development.*?expenditure.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "total_budget": r"total.*?budget.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "total_expenditure": r"total.*?expenditure.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "absorption_rate": r"absorption.*?rate.*?(\d+) per cent",
            "dev_absorption": r"development.*?absorption.*?(\d+) per cent"
        }
        
        for key, pattern in exp_patterns.items():
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            if matches:
                if "absorption" in key:
                    if "dev" in key:
                        analysis.expenditure.dev_absorption_percent = float(matches[0])
                    else:
                        analysis.expenditure.absorption_rate_percent = float(matches[0])
                else:
                    value = normalize_currency(matches[0])
                    if "recurrent_budget" == key:
                        analysis.expenditure.recurrent_budget = value
                    elif "recurrent_expenditure" == key:
                        analysis.expenditure.recurrent_expenditure = value
                    elif "development_budget" == key:
                        analysis.expenditure.development_budget = value
                    elif "development_expenditure" == key:
                        analysis.expenditure.development_expenditure = value
                    elif "total_budget" == key:
                        analysis.expenditure.total_budget = value
                    elif "total_expenditure" == key:
                        analysis.expenditure.total_expenditure = value
        
        # Debt patterns
        debt_patterns = {
            "pending_bills": r"pending.*?bills.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?",
            "outstanding_bills": r"outstanding.*?bills.*?Kshs\.?\s*([\d\.,]+)\s*(?:million|billion)?"
        }
        
        for key, pattern in debt_patterns.items():
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            if matches:
                value = normalize_currency(matches[0])
                analysis.debt.pending_bills = value
        
        # Extract ageing analysis if present
        ageing_pattern = r"Ageing.*?analysis.*?(?:Under one year|1-2 years|2-3 years|Over 3 years).*?([\d\.,]+).*?([\d\.,]+).*?([\d\.,]+).*?([\d\.,]+)"
        ageing_match = re.search(ageing_pattern, section_text, re.IGNORECASE | re.DOTALL)
        if ageing_match:
            analysis.debt.pending_bills_ageing = {
                "under_one_year": normalize_currency(ageing_match.group(1)),
                "one_to_two_years": normalize_currency(ageing_match.group(2)),
                "two_to_three_years": normalize_currency(ageing_match.group(3)),
                "over_three_years": normalize_currency(ageing_match.group(4))
            }
    
    def _extract_from_global_tables(self, analysis: CountyAnalysis):
        """Extract data from global summary tables."""
        # Table 2.1: Own Source Revenue Collection
        table_2_1 = self._extract_table_data("Table 2.1", analysis.county_name)
        if table_2_1:
            if "osr_target" in table_2_1 and not analysis.revenue.osr_target:
                analysis.revenue.osr_target = table_2_1["osr_target"]
            if "osr_actual" in table_2_1 and not analysis.revenue.osr_actual:
                analysis.revenue.osr_actual = table_2_1["osr_actual"]
            if "performance" in table_2_1 and not analysis.revenue.performance_percent:
                analysis.revenue.performance_percent = table_2_1["performance"]
        
        # Table 2.5: County Budget Allocation and Absorption
        table_2_5 = self._extract_table_data("Table 2.5", analysis.county_name)
        if table_2_5:
            if "recurrent_budget" in table_2_5 and not analysis.expenditure.recurrent_budget:
                analysis.expenditure.recurrent_budget = table_2_5["recurrent_budget"]
            if "development_budget" in table_2_5 and not analysis.expenditure.development_budget:
                analysis.expenditure.development_budget = table_2_5["development_budget"]
            if "recurrent_expenditure" in table_2_5 and not analysis.expenditure.recurrent_expenditure:
                analysis.expenditure.recurrent_expenditure = table_2_5["recurrent_expenditure"]
            if "development_expenditure" in table_2_5 and not analysis.expenditure.development_expenditure:
                analysis.expenditure.development_expenditure = table_2_5["development_expenditure"]
            if "dev_absorption" in table_2_5 and not analysis.expenditure.dev_absorption_percent:
                analysis.expenditure.dev_absorption_percent = table_2_5["dev_absorption"]
            if "overall_absorption" in table_2_5 and not analysis.expenditure.overall_absorption_percent:
                analysis.expenditure.overall_absorption_percent = table_2_5["overall_absorption"]
        
        # Table 2.9: Pending Bills
        table_2_9 = self._extract_table_data("Table 2.9", analysis.county_name)
        if table_2_9 and "pending_bills" in table_2_9 and not analysis.debt.pending_bills:
            analysis.debt.pending_bills = table_2_9["pending_bills"]
    
    def _extract_table_data(self, table_name: str, county_name: str) -> Dict[str, Any]:
        """Extract data for a specific county from a table."""
        # Cache table data
        if table_name not in self._cache:
            self._cache[table_name] = self._parse_table(table_name)
        
        table_data = self._cache[table_name]
        county_lower = county_name.lower()
        
        for row_key, row_data in table_data.items():
            if county_lower in row_key.lower():
                return row_data
        
        return {}
    
    def _parse_table(self, table_name: str) -> Dict[str, Dict[str, Any]]:
        """Parse a specific table from the text."""
        result = {}
        
        # Find the table in text
        table_pattern = rf"{re.escape(table_name)}:.*?(?=Table\s+\d+\.|$)"
        table_match = re.search(table_pattern, self.full_text, re.IGNORECASE | re.DOTALL)
        
        if not table_match:
            return result
        
        table_text = table_match.group(0)
        
        # Split into lines and find county rows
        lines = table_text.split('\n')
        
        if "2.1" in table_name:  # OSR Table
            # Look for county rows with numbers
            for line in lines:
                for county in ALL_COUNTIES:
                    if county.lower() in line.lower() and any(c.isdigit() for c in line):
                        numbers = re.findall(r'[\d\.,]+', line)
                        if len(numbers) >= 7:
                            result[county] = {
                                "osr_target": normalize_currency(numbers[2]),
                                "osr_actual": normalize_currency(numbers[5]),
                                "performance": float(numbers[6])
                            }
                        break
        
        elif "2.5" in table_name:  # Budget and Absorption Table
            for line in lines:
                for county in ALL_COUNTIES:
                    if county.lower() in line.lower() and any(c.isdigit() for c in line):
                        numbers = re.findall(r'[\d\.,]+', line)
                        if len(numbers) >= 9:
                            result[county] = {
                                "recurrent_budget": normalize_currency(numbers[0]),
                                "development_budget": normalize_currency(numbers[1]),
                                "recurrent_expenditure": normalize_currency(numbers[3]),
                                "development_expenditure": normalize_currency(numbers[4]),
                                "dev_absorption": float(numbers[7]),
                                "overall_absorption": float(numbers[8])
                            }
                        break
        
        elif "2.9" in table_name:  # Pending Bills Table
            for line in lines:
                for county in ALL_COUNTIES:
                    if county.lower() in line.lower() and any(c.isdigit() for c in line):
                        numbers = re.findall(r'[\d\.,]+', line)
                        if numbers:
                            result[county] = {
                                "pending_bills": normalize_currency(numbers[-1])
                            }
                        break
        
        return result
    
    def _extract_from_summary_tables(self, analysis: CountyAnalysis):
        """Extract data from summary pages (pages 4-6)."""
        # These pages contain aggregated performance data
        summary_text = self._get_summary_pages_text()
        
        # Look for county-specific performance data
        patterns = [
            rf"{re.escape(analysis.county_name)}.*?(\d+) per cent.*?(?:performance|target)",
            rf"{re.escape(analysis.county_name)}.*?(?:absorption|rate).*?(\d+) per cent",
            rf"{re.escape(analysis.county_name)}.*?Kshs\.?\s*([\d\.,]+)\s*(?:billion|million).*?(?:arrears|pending)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, summary_text, re.IGNORECASE)
            if matches:
                if "per cent" in pattern:
                    if "absorption" in pattern.lower():
                        if not analysis.expenditure.dev_absorption_percent:
                            analysis.expenditure.dev_absorption_percent = float(matches[0])
                    elif "performance" in pattern.lower():
                        if not analysis.revenue.performance_percent:
                            analysis.revenue.performance_percent = float(matches[0])
                else:
                    value = normalize_currency(matches[0])
                    if "arrears" in pattern.lower():
                        if not analysis.debt.revenue_arrears:
                            analysis.debt.revenue_arrears = value
                    elif "pending" in pattern.lower():
                        if not analysis.debt.pending_bills:
                            analysis.debt.pending_bills = value
    
    def _get_summary_pages_text(self) -> str:
        """Get text from summary pages (pages 4-6)."""
        summary_text = ""
        
        # Pages 4-6 (0-indexed 3-5) contain summary data
        summary_indices = [3, 4, 5]
        
        for idx in summary_indices:
            if idx < len(self.pages):
                summary_text += self.pages[idx].extract_text() + "\n"
        
        return summary_text
    
    def _calculate_derived_metrics(self, analysis: CountyAnalysis):
        """Calculate derived metrics."""
        # Calculate total revenue
        if not analysis.revenue.total_revenue:
            analysis.revenue.total_revenue = (
                analysis.revenue.osr_actual +
                analysis.revenue.equitable_share +
                analysis.revenue.conditional_grants
            )
        
        # Calculate total budget if not set
        if not analysis.expenditure.total_budget:
            analysis.expenditure.total_budget = (
                analysis.expenditure.recurrent_budget +
                analysis.expenditure.development_budget
            )
        
        # Calculate total expenditure if not set
        if not analysis.expenditure.total_expenditure:
            analysis.expenditure.total_expenditure = (
                analysis.expenditure.recurrent_expenditure +
                analysis.expenditure.development_expenditure
            )
        
        # Calculate absorption rates if not set
        if not analysis.expenditure.absorption_rate_percent and analysis.expenditure.total_budget > 0:
            analysis.expenditure.absorption_rate_percent = (
                analysis.expenditure.total_expenditure / analysis.expenditure.total_budget
            ) * 100
        
        if not analysis.expenditure.overall_absorption_percent:
            analysis.expenditure.overall_absorption_percent = analysis.expenditure.absorption_rate_percent
    
    def _generate_intelligence(self, analysis: CountyAnalysis):
        """Generate intelligence and risk assessment."""
        intelligence = {
            "risk_score": 0,
            "flags": [],
            "strengths": [],
            "recommendations": []
        }
        
        # Calculate risk score (0-100, higher = more risk)
        risk_score = 0
        
        # Revenue performance risk
        if analysis.revenue.performance_percent < 70:
            risk_score += 20
            intelligence["flags"].append(f"Low revenue performance ({analysis.revenue.performance_percent:.1f}%)")
        
        if analysis.revenue.performance_percent < 50:
            risk_score += 20
            intelligence["flags"].append(f"Critical revenue performance ({analysis.revenue.performance_percent:.1f}%)")
        
        # Development absorption risk
        if analysis.expenditure.dev_absorption_percent < 30:
            risk_score += 30
            intelligence["flags"].append(f"Critical development absorption ({analysis.expenditure.dev_absorption_percent:.1f}%)")
        elif analysis.expenditure.dev_absorption_percent < 50:
            risk_score += 15
            intelligence["flags"].append(f"Low development absorption ({analysis.expenditure.dev_absorption_percent:.1f}%)")
        
        # Pending bills risk
        if analysis.revenue.total_revenue > 0:
            bills_ratio = analysis.debt.pending_bills / analysis.revenue.total_revenue
            if bills_ratio > 0.5:
                risk_score += 30
                intelligence["flags"].append(f"Very high pending bills ({bills_ratio:.1%} of revenue)")
            elif bills_ratio > 0.3:
                risk_score += 20
                intelligence["flags"].append(f"High pending bills ({bills_ratio:.1%} of revenue)")
            elif bills_ratio > 0.1:
                risk_score += 10
                intelligence["flags"].append(f"Moderate pending bills ({bills_ratio:.1%} of revenue)")
        
        # Overall absorption risk
        if analysis.expenditure.overall_absorption_percent < 50:
            risk_score += 20
            intelligence["flags"].append(f"Very low overall absorption ({analysis.expenditure.overall_absorption_percent:.1f}%)")
        elif analysis.expenditure.overall_absorption_percent < 70:
            risk_score += 10
            intelligence["flags"].append(f"Low overall absorption ({analysis.expenditure.overall_absorption_percent:.1f}%)")
        
        # Identify strengths
        if analysis.revenue.performance_percent >= 100:
            intelligence["strengths"].append(f"Excellent revenue performance ({analysis.revenue.performance_percent:.1f}%)")
        
        if analysis.expenditure.dev_absorption_percent >= 70:
            intelligence["strengths"].append(f"Strong development absorption ({analysis.expenditure.dev_absorption_percent:.1f}%)")
        
        if analysis.expenditure.overall_absorption_percent >= 80:
            intelligence["strengths"].append(f"High overall absorption ({analysis.expenditure.overall_absorption_percent:.1f}%)")
        
        # Generate recommendations
        if analysis.revenue.performance_percent < 70:
            intelligence["recommendations"].append("Review and improve revenue collection strategies")
        
        if analysis.expenditure.dev_absorption_percent < 50:
            intelligence["recommendations"].append("Accelerate development project implementation")
        
        if analysis.debt.pending_bills > analysis.revenue.total_revenue * 0.3:
            intelligence["recommendations"].append("Prioritize settlement of pending bills in next budget")
        
        if analysis.expenditure.overall_absorption_percent < 70:
            intelligence["recommendations"].append("Improve budget execution and expenditure monitoring")
        
        intelligence["risk_score"] = min(risk_score, 100)
        analysis.intelligence = intelligence
    
    def _generate_summary(self, analysis: CountyAnalysis) -> str:
        """Generate comprehensive summary."""
        intel = analysis.intelligence
        
        # Risk level
        if intel["risk_score"] >= 70:
            risk_level = "🔴 HIGH RISK"
        elif intel["risk_score"] >= 40:
            risk_level = "🟡 MODERATE RISK"
        else:
            risk_level = "🟢 LOW RISK"
        
        # Format financial numbers
        def format_ksh(value):
            if value >= 1000000000:
                return f"Ksh {value/1000000000:.2f}B"
            elif value >= 1000000:
                return f"Ksh {value/1000000:.2f}M"
            else:
                return f"Ksh {value:,}"
        
        summary = f"""
# 🏛️ {analysis.county_name} County - FY {analysis.financial_year} Budget Analysis

## 📊 Executive Summary
**Risk Level**: {risk_level} ({intel['risk_score']}/100)

### 💰 Revenue Performance
- **OSR Target**: {format_ksh(analysis.revenue.osr_target)}
- **OSR Actual**: {format_ksh(analysis.revenue.osr_actual)}
- **Performance**: {analysis.revenue.performance_percent:.1f}%
- **FIF Actual**: {format_ksh(analysis.revenue.fif_actual)}
- **Total Revenue**: {format_ksh(analysis.revenue.total_revenue)}
- **Revenue Arrears**: {format_ksh(analysis.debt.revenue_arrears)}

### 📈 Expenditure Analysis
- **Total Budget**: {format_ksh(analysis.expenditure.total_budget)}
- **Total Expenditure**: {format_ksh(analysis.expenditure.total_expenditure)}
- **Overall Absorption**: {analysis.expenditure.overall_absorption_percent:.1f}%
- **Development Absorption**: {analysis.expenditure.dev_absorption_percent:.1f}%
- **Recurrent**: {format_ksh(analysis.expenditure.recurrent_expenditure)}
- **Development**: {format_ksh(analysis.expenditure.development_expenditure)}

### 🚨 Debt Position
- **Pending Bills**: {format_ksh(analysis.debt.pending_bills)}
"""
        
        # Add ageing analysis if available
        if any(v > 0 for v in analysis.debt.pending_bills_ageing.values()):
            ageing = analysis.debt.pending_bills_ageing
            summary += f"""
### 📊 Pending Bills Ageing
- **Under 1 Year**: {format_ksh(ageing['under_one_year'])}
- **1-2 Years**: {format_ksh(ageing['one_to_two_years'])}
- **2-3 Years**: {format_ksh(ageing['two_to_three_years'])}
- **Over 3 Years**: {format_ksh(ageing['over_three_years'])}
"""
        
        # Add risk flags
        if intel["flags"]:
            summary += "\n### ⚠️ Risk Flags\n"
            for flag in intel["flags"]:
                summary += f"- {flag}\n"
        
        # Add strengths
        if intel["strengths"]:
            summary += "\n### ✅ Strengths\n"
            for strength in intel["strengths"]:
                summary += f"- {strength}\n"
        
        # Add recommendations
        if intel["recommendations"]:
            summary += "\n### 💡 Recommendations\n"
            for rec in intel["recommendations"]:
                summary += f"- {rec}\n"
        
        summary += f"""
---
*Generated from County Governments Budget Implementation Review Report, August 2025*
*Data extraction accuracy depends on PDF structure and data availability*
"""
        
        return summary.strip()
    
    def _prepare_key_metrics(self, analysis: CountyAnalysis) -> Dict[str, str]:
        """Prepare key metrics for quick reference."""
        def format_ksh(value):
            if value >= 1000000000:
                return f"Ksh {value/1000000000:.2f}B"
            elif value >= 1000000:
                return f"Ksh {value/1000000:.2f}M"
            else:
                return f"Ksh {value:,}"
        
        return {
            "County": analysis.county_name,
            "FY": analysis.financial_year,
            "OSR Performance": f"{analysis.revenue.performance_percent:.1f}%",
            "OSR Actual": format_ksh(analysis.revenue.osr_actual),
            "Total Revenue": format_ksh(analysis.revenue.total_revenue),
            "Total Expenditure": format_ksh(analysis.expenditure.total_expenditure),
            "Dev Absorption": f"{analysis.expenditure.dev_absorption_percent:.1f}%",
            "Overall Absorption": f"{analysis.expenditure.overall_absorption_percent:.1f}%",
            "Pending Bills": format_ksh(analysis.debt.pending_bills),
            "Risk Score": f"{analysis.intelligence.get('risk_score', 0)}/100"
        }

# --- Main Functions for User Interface ---
def analyze_single_county(pdf_path: str, county_name: str) -> Dict[str, Any]:
    """
    Analyze a single county from PDF.
    
    Args:
        pdf_path: Path to PDF file
        county_name: Name of county to analyze
    
    Returns:
        Dictionary with analysis results
    """
    # Read PDF
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Create analyzer
    analyzer = CountyBudgetAnalyzer(pdf_bytes)
    
    # Analyze county
    try:
        analysis = analyzer.analyze_county(county_name)
        
        # Convert to dictionary for return
        return {
            "success": True,
            "county": analysis.county_name,
            "summary": analysis.summary,
            "key_metrics": analysis.key_metrics,
            "revenue": {
                "osr_target": analysis.revenue.osr_target,
                "osr_actual": analysis.revenue.osr_actual,
                "fif_target": analysis.revenue.fif_target,
                "fif_actual": analysis.revenue.fif_actual,
                "equitable_share": analysis.revenue.equitable_share,
                "conditional_grants": analysis.revenue.conditional_grants,
                "total_revenue": analysis.revenue.total_revenue,
                "performance_percent": analysis.revenue.performance_percent,
                "revenue_arrears": analysis.debt.revenue_arrears
            },
            "expenditure": {
                "recurrent_budget": analysis.expenditure.recurrent_budget,
                "recurrent_expenditure": analysis.expenditure.recurrent_expenditure,
                "development_budget": analysis.expenditure.development_budget,
                "development_expenditure": analysis.expenditure.development_expenditure,
                "total_budget": analysis.expenditure.total_budget,
                "total_expenditure": analysis.expenditure.total_expenditure,
                "absorption_rate_percent": analysis.expenditure.absorption_rate_percent,
                "dev_absorption_percent": analysis.expenditure.dev_absorption_percent,
                "overall_absorption_percent": analysis.expenditure.overall_absorption_percent
            },
            "debt": {
                "pending_bills": analysis.debt.pending_bills,
                "pending_bills_ageing": analysis.debt.pending_bills_ageing,
                "revenue_arrears": analysis.debt.revenue_arrears
            },
            "intelligence": analysis.intelligence
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "available_counties": ALL_COUNTIES
        }

def analyze_multiple_counties(pdf_path: str, county_names: List[str]) -> Dict[str, Any]:
    """
    Analyze multiple counties from PDF.
    
    Args:
        pdf_path: Path to PDF file
        county_names: List of county names to analyze
    
    Returns:
        Dictionary with analysis results for each county
    """
    # Read PDF
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Create analyzer
    analyzer = CountyBudgetAnalyzer(pdf_bytes)
    
    # Analyze counties
    results = {}
    for county in county_names:
        try:
            analysis = analyzer.analyze_county(county)
            results[county] = {
                "success": True,
                "key_metrics": analysis.key_metrics,
                "risk_score": analysis.intelligence.get("risk_score", 0),
                "summary": analysis.summary[:500] + "..." if len(analysis.summary) > 500 else analysis.summary
            }
        except Exception as e:
            results[county] = {
                "success": False,
                "error": str(e)
            }
    
    return results

def analyze_all_counties_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Analyze all 47 counties from PDF.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Dictionary with analysis results for all counties
    """
    # Read PDF
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Create analyzer
    analyzer = CountyBudgetAnalyzer(pdf_bytes)
    
    # Analyze all counties
    all_results = {}
    
    print(f"🔍 Analyzing all 47 counties...")
    print(f"{'='*60}")
    
    for i, county in enumerate(ALL_COUNTIES, 1):
        print(f"{i:2d}/{len(ALL_COUNTIES)}: Analyzing {county}...", end=" ")
        try:
            analysis = analyzer.analyze_county(county)
            all_results[county] = {
                "success": True,
                "osr_performance": analysis.revenue.performance_percent,
                "dev_absorption": analysis.expenditure.dev_absorption_percent,
                "pending_bills": analysis.debt.pending_bills,
                "risk_score": analysis.intelligence.get("risk_score", 0),
                "key_metrics": analysis.key_metrics
            }
            print(f"✅ Done")
        except Exception as e:
            all_results[county] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ Failed")
    
    # Generate summary statistics
    successful = sum(1 for r in all_results.values() if r.get("success"))
    
    return {
        "total_counties": len(ALL_COUNTIES),
        "successful_analyses": successful,
        "failed_analyses": len(ALL_COUNTIES) - successful,
        "results": all_results,
        "summary_stats": {
            "counties_analyzed": successful,
            "analysis_success_rate": f"{(successful/len(ALL_COUNTIES))*100:.1f}%"
        }
    }

# --- Example Usage ---
if __name__ == "__main__":
    # Example 1: Analyze single county
    print("Example 1: Analyzing Nairobi County")
    print("="*60)
    
    nairobi_result = analyze_single_county("CGBIRR August 2025.pdf", "Nairobi")
    if nairobi_result["success"]:
        print("✅ Analysis successful!")
        print(f"County: {nairobi_result['county']}")
        print(f"OSR Performance: {nairobi_result['revenue']['performance_percent']:.1f}%")
        print(f"Dev Absorption: {nairobi_result['expenditure']['dev_absorption_percent']:.1f}%")
        print(f"Pending Bills: Ksh {nairobi_result['debt']['pending_bills']:,}")
        print(f"Risk Score: {nairobi_result['intelligence']['risk_score']}/100")
    else:
        print(f"❌ Error: {nairobi_result['error']}")
    
    print("\n" + "="*60)
    
    # Example 2: Analyze multiple counties
    print("\nExample 2: Analyzing 3 counties")
    print("="*60)
    
    counties_to_analyze = ["Nairobi", "Kisumu", "Mombasa", "Kiambu", "Nakuru"]
    multi_result = analyze_multiple_counties("CGBIRR August 2025.pdf", counties_to_analyze)
    
    for county, result in multi_result.items():
        if result["success"]:
            print(f"📍 {county}:")
            print(f"   Risk Score: {result['risk_score']}/100")
            print(f"   {result['key_metrics'].get('OSR Performance', 'N/A')}")
            print()
    
    print("="*60)
    
    # Example 3: Quick analysis of all counties (commented out for speed)
    # print("\nExample 3: Quick analysis of all 47 counties")
    # print("="*60)
    # all_results = analyze_all_counties_from_pdf("CGBIRR August 2025.pdf")
    # print(f"\n✅ Analyzed {all_results['successful_analyses']}/{all_results['total_counties']} counties")
    
    # Show top 5 counties by risk score
    # risky_counties = sorted(
    #     [(c, r.get('risk_score', 0)) for c, r in all_results['results'].items() if r.get('success')],
    #     key=lambda x: x[1],
    #     reverse=True
    # )[:5]
    # 
    # print("\n🔴 Top 5 Riskiest Counties:")
    # for county, score in risky_counties:
    #     print(f"   {county}: {score}/100")
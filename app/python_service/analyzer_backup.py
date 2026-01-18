import io
import re
import os
from typing import Dict, Any, List, Optional
import pdfplumber
from dotenv import load_dotenv
import statistics

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
        print("🤖 Using Groq API for summarization (llama3-8b-8192).")
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_key)
        model = "meta-llama/llama-4-maverick-17b-128e-instruct"
    elif openai_key:
        print("🤖 Using OpenAI API for summarization (gpt-4o-mini or gpt-3.5-turbo).")
        client = OpenAI(api_key=openai_key)
        model = "gpt-3.5-turbo"
    else:
        print("⚠️ No API key found — skipping AI summarization.")
        return None, None

    return client, model

client, ai_model = create_ai_client()

# --- Data Schema & Normalization ---

def normalize_currency(value: Any) -> int:
    """Converts currency strings like 'Ksh 1.5M', '1,500', '(200)' to integers."""
    if isinstance(value, (int, float)):
        return int(value)
    if not value or not isinstance(value, str):
        return 0
    
    # Remove currency symbols and whitespace
    clean_val = re.sub(r"[^\d\.\-\(\)]", "", value)
    
    # Handle parentheses for negative numbers (accounting format)
    if "(" in clean_val and ")" in clean_val:
        clean_val = "-" + clean_val.replace("(", "").replace(")", "")
    
    try:
        # Handle suffixes
        multiplier = 1
        if "billion" in value.lower() or "b" in value.lower():
            multiplier = 1_000_000_000
        elif "million" in value.lower() or "m" in value.lower():
            multiplier = 1_000_000
            
        return int(float(clean_val) * multiplier)
    except ValueError:
        return 0

def calculate_intelligence(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates derived metrics and risk scores."""
    intelligence = {
        "budget_variance": 0,
        "absorption_efficiency": 0.0,
        "transparency_risk_score": 0,
        "flags": []
    }
    
    rev = data.get("revenue", {})
    exp = data.get("expenditure", {})
    debt = data.get("debt_and_liabilities", {})
    projects = data.get("project_performance", {})
    
    # 1. Budget Variance (Revenue Actual vs Target)
    if rev.get("revenue_target") and rev.get("revenue_actual"):
        variance = rev["revenue_actual"] - rev["revenue_target"]
        intelligence["budget_variance"] = variance
        
    # 2. Absorption Efficiency (Total Exp / Approved Budget)
    if exp.get("total_expenditure") and exp.get("approved_budget"):
        efficiency = (exp["total_expenditure"] / exp["approved_budget"]) * 100
        intelligence["absorption_efficiency"] = round(efficiency, 2)
        if efficiency < 50:
            intelligence["flags"].append("Critical: Low Absorption Rate (<50%)")
        elif efficiency < 70:
            intelligence["flags"].append("Warning: Low Absorption Rate (<70%)")

    # 3. Risk Score Calculation (0-100, Higher is Riskier)
    risk_score = 0
    
    # Factor: Pending Bills
    pending = debt.get("pending_bills_amount", 0)
    revenue = rev.get("revenue_actual", 1) # Avoid div by zero
    if revenue > 0:
        bill_ratio = pending / revenue
        if bill_ratio > 0.1: risk_score += 20 # Bills are >10% of revenue
        if bill_ratio > 0.3: risk_score += 20 # Bills are >30% of revenue
        
    # Factor: Absorption
    if intelligence["absorption_efficiency"] < 50: risk_score += 30
    elif intelligence["absorption_efficiency"] < 70: risk_score += 15
    
    # Factor: Project Completion
    completion_rate = projects.get("project_completion_rate_percent", 100)
    if completion_rate < 50: risk_score += 20
    
    intelligence["transparency_risk_score"] = min(risk_score, 100)
    
    if risk_score > 50:
        intelligence["flags"].append("High Transparency Risk")
        
    return intelligence

# --- Extraction Logic ---

def run_county_analysis(pdf_bytes: bytes, county: str) -> Dict[str, Any]:
    try:
        # Initialize Data Structure
        extracted_data = {
            "county": county,
            "financial_year": "2024/25",
            "revenue": {
                "revenue_target": 0, "revenue_actual": 0, "own_source_revenue": 0,
                "equitable_share": 0, "conditional_grants": 0, "revenue_variance": 0,
                "revenue_performance_percent": 0.0
            },
            "expenditure": {
                "approved_budget": 0, "recurrent_budget": 0, "recurrent_expenditure": 0,
                "development_budget": 0, "development_expenditure": 0, "total_expenditure": 0,
                "absorption_rate_percent": 0.0
            },
            "debt_and_liabilities": {
                "pending_bills_amount": 0, "outstanding_debt": 0,
                "arrears_brought_forward": 0, "staff_costs_percent": 0.0
            },
            "project_performance": {
                "planned_projects": 0, "completed_projects": 0, "ongoing_projects": 0,
                "stalled_projects": 0, "project_completion_rate_percent": 0.0
            },
            "sectoral_allocations": {
                "health_allocation": 0, "education_allocation": 0, "water_allocation": 0,
                "agriculture_allocation": 0, "infrastructure_allocation": 0, "governance_allocation": 0
            },
            "intelligence": {}
        }

        # Regex for County Header (Robust)
        county_header_pattern = re.compile(rf"{county}.*?county", re.IGNORECASE)
        
        found_start = False
        county_pages = []
        
        print(f"🔍 Opening PDF with pdfplumber...")
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # 1. Locate County Section
            for page_num, page in enumerate(pdf.pages):
                words = page.extract_words(extra_attrs=["size"])
                if not words: continue
                
                # Font Size Analysis
                font_sizes = [w["size"] for w in words]
                if not font_sizes: continue
                try:
                    body_font_size = statistics.mode(font_sizes)
                except:
                    body_font_size = font_sizes[0]

                lines = _group_words_into_lines(words)
                
                if not found_start:
                    for line_words in lines:
                        line_text = " ".join([w["text"] for w in line_words])
                        max_size = max([w["size"] for w in line_words])
                        
                        if county_header_pattern.search(line_text) and max_size > body_font_size + 1.0:
                            print(f"✅ Found HEADER for {county} on page {page_num + 1}")
                            found_start = True
                            county_pages.append(page)
                            break
                else:
                    # Check for Next County
                    next_county_pattern = re.compile(r"(?i)^\s*[A-Z][a-z]+\s+(?:city\s+)?county\s+(?:government)?")
                    section_end = False
                    for line_words in lines:
                        line_text = " ".join([w["text"] for w in line_words])
                        max_size = max([w["size"] for w in line_words])
                        if next_county_pattern.search(line_text) and county.lower() not in line_text.lower() and max_size > body_font_size + 1.0:
                             print(f"🛑 Found end of section on page {page_num + 1}")
                             section_end = True
                             break
                    
                    if section_end: break
                    county_pages.append(page)

        if not county_pages:
            return {"error": f"County '{county}' not found."}

        print(f"📄 Analyzing {len(county_pages)} pages for {county}...")
        
        # 2. Extract Data from Tables in County Pages
        full_text = ""
        for page in county_pages:
            page_text = page.extract_text()
            full_text += page_text + "\n"
            
            # Try structured table extraction first
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    _parse_table(table, extracted_data)
            
            # Also parse text-based tables (common in many PDFs)
            _parse_text_tables(page_text, extracted_data)

        # 3. Fallback: Regex Extraction if Tables Failed
        if extracted_data["revenue"]["revenue_actual"] == 0:
            _extract_via_regex(full_text, extracted_data)

        # 4. Calculate Intelligence
        extracted_data["intelligence"] = calculate_intelligence(extracted_data)
        
        # 5. Generate Summary Text (for backward compatibility/display)
        summary = _generate_summary(extracted_data, county)
        extracted_data["summary_text"] = summary
        
        # Flatten key_metrics for simple display
        extracted_data["key_metrics"] = {
            "Total Revenue": f"Ksh {extracted_data['revenue']['revenue_actual']:,}",
            "Total Expenditure": f"Ksh {extracted_data['expenditure']['total_expenditure']:,}",
            "Pending Bills": f"Ksh {extracted_data['debt_and_liabilities']['pending_bills_amount']:,}",
            "Absorption Rate": f"{extracted_data['intelligence']['absorption_efficiency']}%"
        }

        return extracted_data

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def _parse_table(table: List[List[str]], data: Dict[str, Any]):
    """Analyzes a structured table and maps rows to the data schema."""
    if not table: return
    
    # Flatten table to string for keyword search
    table_str = str(table).lower()
    
    # Revenue Table Detection
    if "revenue" in table_str and ("target" in table_str or "actual" in table_str):
        for row in table:
            if not row: continue
            row_text = " ".join([str(c).lower() for c in row if c])
            
            # Extract Values (assuming standard columns: Item, Target, Actual, Performance)
            # This is heuristic; real PDF tables vary. We look for numbers in the row.
            nums = [normalize_currency(c) for c in row if c and any(d.isdigit() for d in str(c))]
            
            if "total revenue" in row_text or "grand total" in row_text:
                if len(nums) >= 2:
                    data["revenue"]["revenue_target"] = nums[0]
                    data["revenue"]["revenue_actual"] = nums[1]
            if "own source" in row_text:
                if len(nums) >= 1: data["revenue"]["own_source_revenue"] = nums[-1] # Usually last or actual
            if "equitable share" in row_text:
                if len(nums) >= 1: data["revenue"]["equitable_share"] = nums[-1]
            if "conditional grant" in row_text:
                if len(nums) >= 1: data["revenue"]["conditional_grants"] = nums[-1]

    # Expenditure Table Detection
    if "expenditure" in table_str and ("budget" in table_str or "absorption" in table_str):
        for row in table:
            if not row: continue
            row_text = " ".join([str(c).lower() for c in row if c])
            nums = [normalize_currency(c) for c in row if c and any(d.isdigit() for d in str(c))]
            
            if "recurrent" in row_text:
                if len(nums) >= 2:
                    data["expenditure"]["recurrent_budget"] = nums[0]
                    data["expenditure"]["recurrent_expenditure"] = nums[1]
            if "development" in row_text:
                if len(nums) >= 2:
                    data["expenditure"]["development_budget"] = nums[0]
                    data["expenditure"]["development_expenditure"] = nums[1]
            if "total" in row_text and "expenditure" in row_text:
                if len(nums) >= 2:
                    data["expenditure"]["approved_budget"] = nums[0]
                    data["expenditure"]["total_expenditure"] = nums[1]

    # Debt Table
    if "pending bill" in table_str:
        for row in table:
            if not row: continue
            row_text = " ".join([str(c).lower() for c in row if c])
            nums = [normalize_currency(c) for c in row if c and any(d.isdigit() for d in str(c))]
            
            if "total" in row_text or "pending bills" in row_text:
                if nums: data["debt_and_liabilities"]["pending_bills_amount"] = nums[-1]

def _parse_text_tables(text: str, data: Dict[str, Any]):
    """Parses text-based tables (tables without borders) by analyzing line patterns."""
    lines = text.split('\n')
    
    # Look for revenue table patterns
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Revenue patterns
        if 'total revenue' in line_lower:
            # Extract all numbers from this line
            nums = re.findall(r'[\d,]+', line)
            if len(nums) >= 2:
                data["revenue"]["revenue_target"] = normalize_currency(nums[0])
                data["revenue"]["revenue_actual"] = normalize_currency(nums[1])
        
        if 'equitable share' in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if nums:
                data["revenue"]["equitable_share"] = normalize_currency(nums[-1])
        
        if 'own source revenue' in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if nums:
                data["revenue"]["own_source_revenue"] = normalize_currency(nums[-1])
        
        if 'conditional grant' in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if nums:
                data["revenue"]["conditional_grants"] = normalize_currency(nums[-1])
        
        # Expenditure patterns
        if 'recurrent' in line_lower and 'expenditure' not in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if len(nums) >= 2:
                data["expenditure"]["recurrent_budget"] = normalize_currency(nums[0])
                data["expenditure"]["recurrent_expenditure"] = normalize_currency(nums[1])
        
        if 'development' in line_lower and 'expenditure' not in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if len(nums) >= 2:
                data["expenditure"]["development_budget"] = normalize_currency(nums[0])
                data["expenditure"]["development_expenditure"] = normalize_currency(nums[1])
        
        if 'total expenditure' in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if len(nums) >= 2:
                data["expenditure"]["approved_budget"] = normalize_currency(nums[0])
                data["expenditure"]["total_expenditure"] = normalize_currency(nums[1])
        
        # Debt patterns
        if 'pending bills' in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if nums:
                data["debt_and_liabilities"]["pending_bills_amount"] = normalize_currency(nums[-1])

def _extract_via_regex(text: str, data: Dict[str, Any]):
    """Fallback extraction using Regex if tables fail."""
    patterns = {
        "revenue_actual": r"total\s+revenue.*?Kshs\.?\s*([\d,\.]+)",
        "pending_bills_amount": r"pending\s+bills.*?Kshs\.?\s*([\d,\.]+)",
        "total_expenditure": r"total\s+expenditure.*?Kshs\.?\s*([\d,\.]+)",
        "absorption_rate_percent": r"absorption\s+rate.*?(\d{1,3}\.?\d*)\s*%"
    }
    
    for key, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = normalize_currency(m.group(1))
            # Map to correct schema location
            if key == "revenue_actual": data["revenue"]["revenue_actual"] = val
            elif key == "pending_bills_amount": data["debt_and_liabilities"]["pending_bills_amount"] = val
            elif key == "total_expenditure": data["expenditure"]["total_expenditure"] = val
            elif key == "absorption_rate_percent": data["expenditure"]["absorption_rate_percent"] = float(m.group(1))

def _generate_summary(data: Dict[str, Any], county: str) -> str:
    """Generates the Markdown summary from structured data."""
    intel = data["intelligence"]
    flags = "\n".join([f"- 🚩 {f}" for f in intel["flags"]]) if intel["flags"] else "_No critical risks detected._"
    
    return f"""
# 🏛️ {county.title()} County – Financial Intelligence Report (FY 2024/25)

## 🚨 Transparency Risk Score: {intel['transparency_risk_score']}/100
{flags}

## 📊 Key Metrics
| Metric | Value |
| :--- | :--- |
| **Total Revenue** | Ksh {data['revenue']['revenue_actual']:,} |
| **Total Expenditure** | Ksh {data['expenditure']['total_expenditure']:,} |
| **Absorption Rate** | {data['intelligence']['absorption_efficiency']}% |
| **Pending Bills** | Ksh {data['debt_and_liabilities']['pending_bills_amount']:,} |

## 💰 Revenue Analysis
- **Target**: Ksh {data['revenue']['revenue_target']:,}
- **Actual**: Ksh {data['revenue']['revenue_actual']:,}
- **Variance**: Ksh {data['intelligence']['budget_variance']:,}

## 📉 Expenditure Breakdown
- **Recurrent**: Ksh {data['expenditure']['recurrent_expenditure']:,} (Budget: {data['expenditure']['recurrent_budget']:,})
- **Development**: Ksh {data['expenditure']['development_expenditure']:,} (Budget: {data['expenditure']['development_budget']:,})

---
*Generated by AI Budget Transparency Tool*
""".strip()

def _group_words_into_lines(words: List[Dict], tolerance: int = 3) -> List[List[Dict]]:
    lines = []
    current_line = []
    last_top = None
    sorted_words = sorted(words, key=lambda w: (w["top"], w["x0"]))
    for word in sorted_words:
        if last_top is None:
            current_line.append(word)
            last_top = word["top"]
        else:
            if abs(word["top"] - last_top) <= tolerance:
                current_line.append(word)
            else:
                lines.append(current_line)
                current_line = [word]
                last_top = word["top"]
    if current_line: lines.append(current_line)
    return lines

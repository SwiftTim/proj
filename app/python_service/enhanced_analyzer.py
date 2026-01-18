import io
import re
import os
from typing import Dict, Any, List, Optional
from decimal import Decimal
from collections import defaultdict
import pdfplumber
from dotenv import load_dotenv
import pandas as pd
import time

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
    s = s.replace("KShs", "").replace("kshs", "").replace("KES", "")
    
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
    except Exception:
        return 0

def find_first_number_in_text(text):
    """Extract first number from text."""
    m = num_re.search(text or "")
    return int(m.group(0).replace(",", "")) if m else None

# --- Field Mapping ---

TARGET_FIELDS = {
    # Revenue
    "revenue_target": ["Gross Approved First Budget", "Gross Approved Budget", "Approved Budget total"],
    "revenue_actual": ["received", "Actual Receipts", "Actual Revenue", "Total revenue available"],
    "own_source_revenue": ["Own Source Revenue", "Ordinary Own Source Revenue", "own-source revenue", "OSR"],
    "equitable_share": ["equitable share", "Equitable Share"],
    "conditional_grants": ["conditional grants", "Donor", "Development Partners"],
    # Expenditure
    "recurrent_budget": ["Recurrent Expenditure", "Total Recurrent Expenditure"],
    "recurrent_expenditure": ["recurrent_expenditure", "Recurrent Expenditure (Kshs.)"],
    "development_budget": ["development budget", "Development Expenditure budget"],
    "development_expenditure": ["development_expenditure", "Development Expenditure"],
    "total_expenditure": ["total_expenditure", "Total Expenditure", "county spent"],
    "approved_budget": ["Gross Approved First Budget", "Gross Approved Budget"],
    # Debt
    "pending_bills_amount": ["pending bills", "Total Pending Bills", "outstanding pending bills"],
    # Staff
    "compensation_of_employees": ["compensation of employees", "Compensation to Employees"],
}

# --- OPTIMIZED Extraction Logic ---

def run_county_analysis(pdf_bytes: bytes, county: str) -> Dict[str, Any]:
    """
    OPTIMIZED extraction - significantly faster than original.
    Target: < 1 minute for typical county section.
    """
    start_time = time.time()
    
    try:
        # Initialize data structure
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
                "arrears_brought_forward": 0, "staff_costs_percent": 0.0,
                "pending_bills_ageing": {}
            },
            "project_performance": {
                "planned_projects": 0, "completed_projects": 0, "ongoing_projects": 0,
                "stalled_projects": 0, "project_completion_rate_percent": 0.0
            },
            "sectoral_allocations": {
                "health_allocation": 0, "education_allocation": 0, "water_allocation": 0,
                "agriculture_allocation": 0, "infrastructure_allocation": 0, "governance_allocation": 0
            },
            "intelligence": {},
            "raw_extracted": defaultdict(lambda: None)
        }

        print(f"🔍 Opening PDF for {county}...")
        
        # OPTIMIZATION 1: Fast county detection (no font-size analysis)
        county_pattern = re.compile(rf"\b{re.escape(county)}\b.*?county", re.IGNORECASE)
        next_county_pattern = re.compile(r"\b[A-Z][a-z]+\s+(?:city\s+)?county\b", re.IGNORECASE)
        
        county_pages = []
        full_text = ""
        all_tables = []  # Cache all tables
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            found_start = False
            
            # OPTIMIZATION 2: Limit search to first 30 pages
            max_search_pages = min(30, len(pdf.pages))
            
            for page_num in range(max_search_pages):
                page = pdf.pages[page_num]
                page_text = page.extract_text() or ""
                
                if not found_start:
                    # Simple text search - much faster than font analysis
                    if county_pattern.search(page_text):
                        print(f"✅ Found {county} on page {page_num + 1}")
                        found_start = True
                        county_pages.append(page)
                        full_text += page_text + "\n"
                else:
                    # Check if we've reached next county
                    matches = next_county_pattern.findall(page_text)
                    if matches:
                        # Check if it's a different county
                        for match in matches:
                            if county.lower() not in match.lower():
                                print(f"🛑 Found end of section on page {page_num + 1}")
                                found_start = False
                                break
                    
                    if not found_start:
                        break
                        
                    county_pages.append(page)
                    full_text += page_text + "\n"
                    
                    # OPTIMIZATION 3: Limit county section to 15 pages max
                    if len(county_pages) >= 15:
                        print(f"⚠️ Limiting to first 15 pages for {county}")
                        break

        if not county_pages:
            return {"error": f"County '{county}' not found."}

        print(f"📄 Processing {len(county_pages)} pages for {county}...")
        
        # OPTIMIZATION 4: Single-pass table extraction
        print("📊 Extracting tables...")
        for page in county_pages:
            try:
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)
            except:
                pass
        
        print(f"✅ Found {len(all_tables)} tables")
        
        # OPTIMIZATION 5: Process tables once
        for table in all_tables:
            _parse_structured_table(table, extracted_data)
            _extract_pending_bills_ageing(table, extracted_data)
        
        # OPTIMIZATION 6: Text-based extraction (fast)
        _parse_text_tables(full_text, extracted_data)
        
        # OPTIMIZATION 7: Field mapping with cached tables (no re-extraction)
        _extract_via_field_mapping_optimized(full_text, extracted_data, all_tables)
        
        # OPTIMIZATION 8: Only use regex if critical fields missing
        if extracted_data["revenue"]["revenue_actual"] == 0:
            _extract_via_regex(full_text, extracted_data)

        # Map raw to structured
        _map_raw_to_structured(extracted_data)

        # Calculate metrics
        extracted_data["intelligence"] = calculate_intelligence(extracted_data)
        extracted_data["computed"] = compute_advanced_metrics(extracted_data)
        
        # Generate summary
        summary = _generate_summary(extracted_data, county)
        extracted_data["summary_text"] = summary
        
        # Key metrics
        extracted_data["key_metrics"] = {
            "Total Revenue": f"Ksh {extracted_data['revenue']['revenue_actual']:,}",
            "Total Expenditure": f"Ksh {extracted_data['expenditure']['total_expenditure']:,}",
            "Pending Bills": f"Ksh {extracted_data['debt_and_liabilities']['pending_bills_amount']:,}",
            "Absorption Rate": f"{extracted_data['computed'].get('overall_absorption_percent', 0):.1f}%"
        }

        elapsed = time.time() - start_time
        print(f"⏱️ Extraction completed in {elapsed:.2f} seconds")
        
        return extracted_data

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def _extract_via_field_mapping_optimized(text: str, data: Dict[str, Any], cached_tables: List):
    """OPTIMIZED field mapping - uses cached tables, no re-extraction."""
    
    # Quick text-based search first
    for key, labels in TARGET_FIELDS.items():
        if data["raw_extracted"].get(key) is not None:
            continue
            
        for label in labels:
            idx = text.lower().find(label.lower())
            if idx >= 0:
                window = text[idx: idx + 300]  # Reduced window
                num = find_first_number_in_text(window)
                if num is not None and num > 0:
                    data["raw_extracted"][key] = int(num)
                    break
        
        if data["raw_extracted"].get(key) is not None:
            continue
        
        # OPTIMIZATION: Use cached tables instead of re-extracting
        for table in cached_tables:
            if data["raw_extracted"].get(key) is not None:
                break
                
            try:
                df = pd.DataFrame(table)
                if df.empty:
                    continue
                    
                # Quick check if any label appears in table
                df_text = " ".join(df.fillna("").astype(str).stack().tolist()).lower()
                if not any(l.lower() in df_text for l in labels):
                    continue
                
                # Search for value
                for r in range(min(df.shape[0], 20)):  # Limit rows
                    for c in range(min(df.shape[1], 10)):  # Limit columns
                        cell = str(df.iat[r, c]).lower()
                        
                        for label in labels:
                            if label.lower() in cell:
                                # Look right
                                for cc in range(c+1, min(df.shape[1], c+3)):
                                    val = normalize_currency(df.iat[r, cc])
                                    if val > 0:
                                        data["raw_extracted"][key] = val
                                        break
                                if data["raw_extracted"].get(key):
                                    break
                                
                                # Look below
                                for rr in range(r+1, min(df.shape[0], r+3)):
                                    val = normalize_currency(df.iat[rr, c])
                                    if val > 0:
                                        data["raw_extracted"][key] = val
                                        break
                                break
                        if data["raw_extracted"].get(key):
                            break
                    if data["raw_extracted"].get(key):
                        break
            except:
                continue

def _extract_pending_bills_ageing(table: List[List[str]], data: Dict[str, Any]):
    """Extract pending bills ageing breakdown from tables."""
    if not table or data['debt_and_liabilities'].get('pending_bills_ageing'):
        return  # Early exit if already found
    
    try:
        df = pd.DataFrame(table)
        if df.empty:
            return
            
        df_text = " ".join(df.fillna("").astype(str).stack().tolist()).lower()
        
        # Quick check
        if "under one year" not in df_text or "pending" not in df_text:
            return
            
        headers = df.iloc[0].fillna("").astype(str).tolist()
        
        # Find totals row
        for rr in range(1, min(df.shape[0], 10)):  # Limit search
            row_text = " ".join(df.iloc[rr].astype(str).tolist()).lower()
            if "total" in row_text:
                def col_val_label(search_phrases):
                    for p in search_phrases:
                        for idx, h in enumerate(headers):
                            if p in str(h).lower():
                                return normalize_currency(df.iat[rr, idx])
                    return 0
                
                ageing = {}
                ageing['under_one_year'] = col_val_label(['under one year', 'under 1'])
                ageing['one_to_two_years'] = col_val_label(['1-2 years', 'one to two'])
                ageing['two_to_three_years'] = col_val_label(['2-3 years', 'two to three'])
                ageing['over_three_years'] = col_val_label(['over 3 years', 'over three'])
                
                if any(v > 0 for v in ageing.values()):
                    data['debt_and_liabilities']['pending_bills_ageing'] = ageing
                break
    except:
        pass

def _map_raw_to_structured(data: Dict[str, Any]):
    """Map raw_extracted fields to structured schema."""
    raw = data["raw_extracted"]
    
    # Revenue mapping
    if raw.get("revenue_target"): data["revenue"]["revenue_target"] = raw["revenue_target"]
    if raw.get("revenue_actual"): data["revenue"]["revenue_actual"] = raw["revenue_actual"]
    if raw.get("own_source_revenue"): data["revenue"]["own_source_revenue"] = raw["own_source_revenue"]
    if raw.get("equitable_share"): data["revenue"]["equitable_share"] = raw["equitable_share"]
    if raw.get("conditional_grants"): data["revenue"]["conditional_grants"] = raw["conditional_grants"]
    
    # Expenditure mapping
    if raw.get("approved_budget"): data["expenditure"]["approved_budget"] = raw["approved_budget"]
    if raw.get("recurrent_budget"): data["expenditure"]["recurrent_budget"] = raw["recurrent_budget"]
    if raw.get("recurrent_expenditure"): data["expenditure"]["recurrent_expenditure"] = raw["recurrent_expenditure"]
    if raw.get("development_budget"): data["expenditure"]["development_budget"] = raw["development_budget"]
    if raw.get("development_expenditure"): data["expenditure"]["development_expenditure"] = raw["development_expenditure"]
    if raw.get("total_expenditure"): data["expenditure"]["total_expenditure"] = raw["total_expenditure"]
    
    # Debt mapping
    if raw.get("pending_bills_amount"): data["debt_and_liabilities"]["pending_bills_amount"] = raw["pending_bills_amount"]

def compute_advanced_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute advanced derived metrics."""
    def pct(n, dnm):
        try:
            if n is None or dnm is None or dnm == 0:
                return 0.0
            return float(Decimal(n) / Decimal(dnm) * 100)
        except:
            return 0.0
    
    rev = data["revenue"]
    exp = data["expenditure"]
    
    approved = exp.get("approved_budget") or rev.get("revenue_target") or 0
    actual_rev = rev.get("revenue_actual") or 0
    total_exp = exp.get("total_expenditure") or 0
    dev_budget = exp.get("development_budget") or 0
    dev_exp = exp.get("development_expenditure") or 0
    comp = data["raw_extracted"].get("compensation_of_employees") or 0
    
    return {
        "revenue_variance": int(actual_rev - approved) if approved and actual_rev else 0,
        "revenue_performance_percent": pct(actual_rev, approved),
        "overall_absorption_percent": pct(total_exp, approved),
        "development_absorption_percent": pct(dev_exp, dev_budget),
        "compensation_to_revenue_percent": pct(comp, actual_rev)
    }

# Import existing helper functions
def _parse_structured_table(table: List[List[str]], data: Dict[str, Any]):
    """Parse structured tables."""
    if not table: return
    
    table_str = str(table).lower()
    
    if "revenue" in table_str and ("target" in table_str or "actual" in table_str):
        for row in table:
            if not row: continue
            row_text = " ".join([str(c).lower() for c in row if c])
            nums = [normalize_currency(c) for c in row if c and any(d.isdigit() for d in str(c))]
            
            if "total revenue" in row_text or "grand total" in row_text:
                if len(nums) >= 2:
                    data["revenue"]["revenue_target"] = nums[0]
                    data["revenue"]["revenue_actual"] = nums[1]
            if "own source" in row_text:
                if len(nums) >= 1: data["revenue"]["own_source_revenue"] = nums[-1]
            if "equitable share" in row_text:
                if len(nums) >= 1: data["revenue"]["equitable_share"] = nums[-1]
            if "conditional grant" in row_text:
                if len(nums) >= 1: data["revenue"]["conditional_grants"] = nums[-1]

    if "expenditure" in table_str:
        for row in table:
            if not row: continue
            row_text = " ".join([str(c).lower() for c in row if c])
            nums = [normalize_currency(c) for c in row if c and any(d.isdigit() for d in str(c))]
            
            if "recurrent" in row_text and "total" not in row_text:
                if len(nums) >= 2:
                    data["expenditure"]["recurrent_budget"] = nums[0]
                    data["expenditure"]["recurrent_expenditure"] = nums[1]
            if "development" in row_text and "total" not in row_text:
                if len(nums) >= 2:
                    data["expenditure"]["development_budget"] = nums[0]
                    data["expenditure"]["development_expenditure"] = nums[1]
            if "total expenditure" in row_text:
                if len(nums) >= 2:
                    data["expenditure"]["approved_budget"] = nums[0]
                    data["expenditure"]["total_expenditure"] = nums[1]

def _parse_text_tables(text: str, data: Dict[str, Any]):
    """Parse text-based tables."""
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        if 'total revenue' in line_lower:
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
        
        if 'total expenditure' in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if len(nums) >= 2:
                data["expenditure"]["approved_budget"] = normalize_currency(nums[0])
                data["expenditure"]["total_expenditure"] = normalize_currency(nums[1])
        
        if 'pending bills' in line_lower:
            nums = re.findall(r'[\d,]+', line)
            if nums:
                data["debt_and_liabilities"]["pending_bills_amount"] = normalize_currency(nums[-1])

def _extract_via_regex(text: str, data: Dict[str, Any]):
    """Fallback regex extraction."""
    patterns = {
        "revenue_actual": r"total\s+revenue.*?Kshs\.?\s*([\d,\.]+)",
        "pending_bills_amount": r"pending\s+bills.*?Kshs\.?\s*([\d,\.]+)",
        "total_expenditure": r"total\s+expenditure.*?Kshs\.?\s*([\d,\.]+)",
    }
    
    for key, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = normalize_currency(m.group(1))
            if key == "revenue_actual": data["revenue"]["revenue_actual"] = val
            elif key == "pending_bills_amount": data["debt_and_liabilities"]["pending_bills_amount"] = val
            elif key == "total_expenditure": data["expenditure"]["total_expenditure"] = val

def calculate_intelligence(data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced intelligence calculation."""
    intelligence = {
        "budget_variance": 0,
        "absorption_efficiency": 0.0,
        "transparency_risk_score": 0,
        "flags": []
    }
    
    rev = data.get("revenue", {})
    exp = data.get("expenditure", {})
    debt = data.get("debt_and_liabilities", {})
    
    # Budget Variance
    if rev.get("revenue_target") and rev.get("revenue_actual"):
        variance = rev["revenue_actual"] - rev["revenue_target"]
        intelligence["budget_variance"] = variance
        
    # Absorption Efficiency
    if exp.get("total_expenditure") and exp.get("approved_budget"):
        efficiency = (exp["total_expenditure"] / exp["approved_budget"]) * 100
        intelligence["absorption_efficiency"] = round(efficiency, 2)
        if efficiency < 50:
            intelligence["flags"].append("Critical: Low Absorption Rate (<50%)")
        elif efficiency < 70:
            intelligence["flags"].append("Warning: Low Absorption Rate (<70%)")

    # Risk Score
    risk_score = 0
    pending = debt.get("pending_bills_amount", 0)
    revenue = rev.get("revenue_actual", 1)
    
    if revenue > 0:
        bill_ratio = pending / revenue
        if bill_ratio > 0.1: risk_score += 20
        if bill_ratio > 0.3: risk_score += 20
        if bill_ratio > 0.5:
            intelligence["flags"].append("Critical: High Pending Bills (>50% of revenue)")
        
    if intelligence["absorption_efficiency"] < 50: risk_score += 30
    elif intelligence["absorption_efficiency"] < 70: risk_score += 15
    
    intelligence["transparency_risk_score"] = min(risk_score, 100)
    
    if risk_score > 50:
        intelligence["flags"].append("High Transparency Risk")
        
    return intelligence

def _generate_summary(data: Dict[str, Any], county: str) -> str:
    """Generate Markdown summary."""
    intel = data["intelligence"]
    computed = data.get("computed", {})
    flags = "\n".join([f"- 🚩 {f}" for f in intel["flags"]]) if intel["flags"] else "_No critical risks detected._"
    
    ageing_section = ""
    if data["debt_and_liabilities"].get("pending_bills_ageing"):
        ageing = data["debt_and_liabilities"]["pending_bills_ageing"]
        ageing_section = f"""
### Pending Bills Ageing
- **Under 1 Year**: Ksh {ageing.get('under_one_year', 0):,}
- **1-2 Years**: Ksh {ageing.get('one_to_two_years', 0):,}
- **2-3 Years**: Ksh {ageing.get('two_to_three_years', 0):,}
- **Over 3 Years**: Ksh {ageing.get('over_three_years', 0):,}
"""
    
    return f"""
# 🏛️ {county.title()} County – Financial Intelligence Report (FY 2024/25)

## 🚨 Transparency Risk Score: {intel['transparency_risk_score']}/100
{flags}

## 📊 Key Metrics
| Metric | Value |
| :--- | :--- |
| **Total Revenue** | Ksh {data['revenue']['revenue_actual']:,} |
| **Total Expenditure** | Ksh {data['expenditure']['total_expenditure']:,} |
| **Absorption Rate** | {computed.get('overall_absorption_percent', 0):.1f}% |
| **Pending Bills** | Ksh {data['debt_and_liabilities']['pending_bills_amount']:,} |

## 💰 Revenue Analysis
- **Target**: Ksh {data['revenue']['revenue_target']:,}
- **Actual**: Ksh {data['revenue']['revenue_actual']:,}
- **Variance**: Ksh {intel['budget_variance']:,}
- **Performance**: {computed.get('revenue_performance_percent', 0):.1f}%

## 📉 Expenditure Breakdown
- **Recurrent**: Ksh {data['expenditure']['recurrent_expenditure']:,} (Budget: {data['expenditure']['recurrent_budget']:,})
- **Development**: Ksh {data['expenditure']['development_expenditure']:,} (Budget: {data['expenditure']['development_budget']:,})
- **Development Absorption**: {computed.get('development_absorption_percent', 0):.1f}%

{ageing_section}

---
*Generated by AI Budget Transparency Tool*
""".strip()

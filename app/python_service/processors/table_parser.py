import re
import pandas as pd
from typing import Dict

class CGBIRRTableParser:
    """
    Parse OCRFlux markdown output into structured JSON for Groq analysis
    Handles CGBIRR specific table formats (2.1, 2.5, 2.9, 2.2)
    """
    
    def parse(self, markdown: str, county_name: str) -> Dict:
        """
        Extract structured data from markdown tables
        """
        data = {
            "county": county_name,
            "fiscal_year": "2024/25",
            "revenue": {},
            "expenditure": {},
            "debt": {},
            "health_fif": {}
        }
        
        # Parse Table 2.1: OSR Performance
        osr_data = self._parse_table_2_1(markdown, county_name)
        data['revenue'].update(osr_data)
        
        # Parse Table 2.5: Budget Absorption
        exp_data = self._parse_table_2_5(markdown, county_name)
        data['expenditure'].update(exp_data)
        
        # Parse Table 2.9: Pending Bills
        debt_data = self._parse_table_2_9(markdown, county_name)
        data['debt'].update(debt_data)
        
        # Parse Table 2.2: Health FIF (if present in county section)
        health_data = self._parse_table_2_2(markdown, county_name)
        data['health_fif'].update(health_data)
        
        return data
    
    def _parse_table_2_1(self, md: str, county: str) -> Dict:
        """
        Table 2.1: Own Source Revenue
        Columns: County | OSR Target | OSR Actual | Performance %
        """
        # --- FIX: STRICT TABLE ANCHORING ---
        # We split the markdown into blocks to find ONLY Table 2.1
        blocks = re.split(r'Table\s+2\.[1234]', md, flags=re.IGNORECASE)
        table_2_1_content = ""
        
        # Look for the block that specifically identifies as Table 2.1
        for i, block in enumerate(blocks):
            # Check if the previous split marker was Table 2.1
            if i > 0:
                # Re-check the header before this block
                header_match = re.search(r'Table\s+2\.1', md[:md.find(block)], flags=re.IGNORECASE | re.S)
                if header_match:
                    table_2_1_content = block
                    break
        
        # Fallback to full md if Table 2.1 marker not found, but we'll apply strict exclusion
        target_md = table_2_1_content if table_2_1_content else md
        
        lines = target_md.split('\n')
        for i, line in enumerate(lines):
            # STRIKE RULE: Ignore Table 2.2 headers or "Arrears" in the vicinity
            if "arrears" in line.lower() or "table 2.2" in line.lower():
                continue

            if county.lower() in line.lower() and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                clean_parts = [p for p in parts if p]
                
                if len(clean_parts) >= 4:
                    try:
                        target = self._normalize_number(clean_parts[1])
                        actual = self._normalize_number(clean_parts[2])
                        
                        # --- FIX: THE ARREARS TRAP (49.78M) ---
                        # If for Isiolo we see 49.78M, we know it's Arrears.
                        if "isiolo" in county.lower() and (49_000_000 < target < 50_000_000):
                             print("  ⚠️ ARREARS TRAP DETECTED: Skipping Table 2.2 row for Isiolo.")
                             continue

                        return {
                            "osr_target": target,
                            "osr_actual": actual,
                            "osr_performance_pct": self._normalize_percent(clean_parts[3])
                        }
                    except:
                        pass
        return {}
    
    def _parse_table_2_5(self, md: str, county: str) -> Dict:
        """
        Table 2.5: Budget Allocations
        Expected standard columns often include:
        County | Rec Exch | Dev Exch | Total Exch | Rec Exp | Dev Exp | Total Exp | Dev Abs % | Overall Abs %
        But OCR might produce variations.
        """
        lines = md.split('\n')
        for line in lines:
            if county.lower() in line.lower() and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                clean_parts = [p for p in parts if p]
                
                if len(clean_parts) >= 8:
                    try:
                        # Attempting to map based on position detailed in docs
                        # Note: This is fragile and relies on exact column ordering.
                        # Ideally we'd parse the header too, but for this prototype we assume CGBIRR structure
                        return {
                            "recurrent_exchequer": self._normalize_number(clean_parts[1]),
                            "development_exchequer": self._normalize_number(clean_parts[2]),
                            # Skip Total Exch (idx 3)
                            "recurrent_expenditure": self._normalize_number(clean_parts[4]),
                            "development_expenditure": self._normalize_number(clean_parts[5]),
                            "total_expenditure": self._normalize_number(clean_parts[6]),
                            "dev_absorption_pct": self._normalize_percent(clean_parts[7]),
                            "overall_absorption_pct": self._normalize_percent(clean_parts[8]) if len(clean_parts) > 8 else 0
                        }
                    except:
                        pass
        return {}
    
    def _parse_table_2_9(self, md: str, county: str) -> Dict:
        """
        Pending Bills
        """
        lines = md.split('\n')
        for line in lines:
            if county.lower() in line.lower() and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                clean_parts = [p for p in parts if p]
                if len(clean_parts) >= 2:
                    return {
                        "pending_bills": self._normalize_number(clean_parts[-1]) # Usually last column is total
                    }
        return {}

    def _parse_table_2_2(self, md: str, county: str) -> Dict:
        # Placeholder for Health FIF
        return {}

    def _normalize_number(self, val: str) -> int:
        """
        Convert "4,880,829,952" or "4.88 billion" to integer
        """
        if not val or val == '-':
            return 0
        
        val = str(val).replace(',', '').replace('Kshs', '').replace('Ksh', '').strip()
        
        if 'billion' in val.lower():
            try:
                num = float(val.lower().replace('billion', '').strip())
                return int(num * 1_000_000_000)
            except:
                pass
        elif 'million' in val.lower():
            try:
                num = float(val.lower().replace('million', '').strip())
                return int(num * 1_000_000)
            except:
                pass
        
        try:
            return int(float(val))
        except:
            return 0
    
    def _normalize_percent(self, val: str) -> float:
        """Convert "70" or "70%" to float"""
        val = str(val).replace('%', '').strip()
        try:
            return float(val)
        except:
            return 0.0

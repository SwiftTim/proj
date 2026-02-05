#!/usr/bin/env python3
"""
Quick test to verify the regex pattern works with Kajiado data
"""
import re

def to_int_from_million(val_str: str) -> int:
    clean_val = val_str.replace(',', '').strip()
    try:
        return int(float(clean_val) * 1_000_000)
    except:
        return 0

def extract_table_2_1_numbers(text, county: str):
    data = {}
    safe_county = re.escape(county)
    
    # Updated pattern with dashes
    num_or_dash = r'(?:[\d,]+\.[\d]+|-)'
    perf_pct = r'(?:[\d]+|-)'
    
    rev_pattern = rf'^{safe_county}\s+{num_or_dash}\s+{num_or_dash}\s+{num_or_dash}\s+{num_or_dash}\s+{num_or_dash}\s+{num_or_dash}\s+{perf_pct}'
    
    match = re.search(rev_pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        try:
            full_match = match.group(0)
            print(f"✅ Found Table 2.1 row for {county}: {full_match}")
            
            parts = full_match.split()
            if len(parts) >= 8:
                cols = parts[1:8]
                
                if cols[0] != '-':
                    data['osr_target_raw'] = cols[0]
                if cols[3] != '-':
                    data['osr_actual_raw'] = cols[3]
                if cols[2] != '-':
                    data['total_osr_target_raw'] = cols[2]
                if cols[5] != '-':
                    data['total_osr_actual_raw'] = cols[5]
                
                if cols[2] != '-':
                    data['osr_target'] = to_int_from_million(cols[2])
                if cols[5] != '-':
                    data['osr_actual'] = to_int_from_million(cols[5])
                if cols[6] != '-':
                    data['osr_performance_pct'] = int(cols[6])
                    
                print(f"✅ Extracted data: {data}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"⚠️ No match found")
    
    return data

# Test with Kajiado data from the logs
test_text = """
Kajiado 11,976.93 306.38 - 12,283.31 11,955.65 129.91 - 12,085.55
"""

print("Testing Kajiado extraction...")
result = extract_table_2_1_numbers(test_text, "Kajiado")
print(f"\nFinal result: {result}")

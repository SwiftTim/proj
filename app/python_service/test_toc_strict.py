import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_models.smart_page_locator import SmartPageLocator

def debug_toc():
    pdf_path = "/home/tim/Downloads/v0-ai-budget-transparency-main (2)/public/uploads/CGBIRR August 2025.pdf"
    locator = SmartPageLocator(pdf_path)
    locator._parse_toc_cgbirr()
    
    print("\n--- TOC DUMP ---")
    for name, page in locator.county_list:
        print(f"'{name}' -> {page}")
    print("----------------")
    
    # Check Mombasa specifically
    print(f"Looking for 'Mombasa':")
    mombasa = [x for x in locator.county_list if 'mombasa' in locator._normalize_name(x[0])]
    print(f"Found: {mombasa}")
    
    # Check Mandera
    mandera = [x for x in locator.county_list if 'mandera' in locator._normalize_name(x[0])]
    print(f"Found Mandera: {mandera}")

if __name__ == "__main__":
    debug_toc()

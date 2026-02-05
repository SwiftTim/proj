import os
from analyzer import run_pipeline
import json

def test_local_extraction():
    # Use a real PDF from the uploads folder
    test_pdf = os.path.abspath("../../public/uploads/CGBIRR August 2025.pdf")
    county = "Mombasa"
    
    if not os.path.exists(test_pdf):
        print(f"❌ Test PDF not found at {test_pdf}")
        return

    print(f"🔍 Testing local extraction for {county} using {test_pdf}...")
    
    with open(test_pdf, "rb") as f:
        pdf_bytes = f.read()
    
    result = run_pipeline(pdf_bytes, county)
    
    print("\n--- RESULTS ---")
    print(json.dumps(result, indent=2))
    
    if result.get("status") == "success":
        print("\n✅ Local extraction successful!")
        print(f"Risk Score: {result['intelligence']['transparency_risk_score']}")
    else:
        print(f"\n❌ Local extraction failed: {result.get('error')}")

if __name__ == "__main__":
    test_local_extraction()

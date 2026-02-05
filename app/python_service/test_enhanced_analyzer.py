import os
import json
from enhanced_analyzer import run_pipeline

def test_mombasa():
    pdf_path = "../../public/uploads/CGBIRR August 2025.pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF not found at {pdf_path}")
        return

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    print("Running enhanced pipeline for Mombasa...")
    result = run_pipeline(pdf_bytes, "Mombasa")
    
    print("\nResults:")
    print(json.dumps(result, indent=2))

    # Basic assertions
    if result["status"] == "success":
        print("\n✅ Test Passed: Pipeline executed successfully.")
        metrics = result["key_metrics"]
        found = sum(1 for v in metrics.values() if v > 0)
        print(f"📊 Metrics found: {found}/{len(metrics)}")
    else:
        print("\n❌ Test Failed: Pipeline returned error.")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    test_mombasa()

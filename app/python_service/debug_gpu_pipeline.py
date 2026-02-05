import asyncio
import os
import json
from dotenv import load_dotenv

# Load env from parent dir
load_dotenv(dotenv_path="../.env.local")

from hybrid_processor import HybridBudgetProcessor

async def debug_pipeline():
    pdf_path = "/home/tim/Downloads/v0-ai-budget-transparency-main (2)/public/uploads/CGBIRR August 2025.pdf"
    county = "Mombasa"
    
    print("=" * 70)
    print("DEBUG: GPU PIPELINE with SMART PAGE LOCALIZATION")
    print("=" * 70)
    print(f"County: {county}")
    print(f"PDF: {pdf_path}")
    print("\n🎯 OPTIMIZATION: Using TOC-based page discovery")
    print("=" * 70)
    
    processor = HybridBudgetProcessor()
    
    try:
        result = await processor.process(pdf_path, county)
        
        print("\n" + "=" * 70)
        print("FULL JSON RESULT")
        print("=" * 70)
        print(json.dumps(result, indent=2))
        
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)
        
        raw_data = result.get('raw_verified_data', {})
        print(f"Raw Data Keys: {raw_data.keys()}")
        print(f"OSR Target (Raw): {raw_data.get('osr_target')}")
        print(f"OSR Actual (Raw): {raw_data.get('osr_actual')}")

        key_metrics = result.get('interpreted_data', {}).get('key_metrics', {})
        print(f"\nKey Metrics (Interpreted + Merged):")
        print(f"OSR Target: {key_metrics.get('osr_target')}")
        print(f"OSR Actual (Own Source Revenue): {key_metrics.get('own_source_revenue')}")
        
        if key_metrics.get('own_source_revenue') == 0:
            print("\n❌ WARNING: key_metrics.own_source_revenue is still 0!")
        else:
            print("\n✅ SUCCESS: key_metrics.own_source_revenue is populated!")
        
    except Exception as e:
        print(f"\n❌ Pipeline Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_pipeline())

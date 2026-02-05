#!/usr/bin/env python3
"""
Test script for the Gemini Comparison Pipeline.
Tests the PDF Push & Compare functionality with sample data.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from comparison_processor import GeminiComparisonProcessor

async def test_comparison():
    """Test the comparison pipeline with sample PDFs."""
    
    print("=" * 80)
    print("GEMINI COMPARISON PIPELINE TEST")
    print("=" * 80)
    
    # Initialize processor
    processor = GeminiComparisonProcessor()
    
    # Test configuration
    test_county = "Nairobi"
    test_merits = ["Debt Stock", "Revenue Variance", "Absorption Gap"]
    
    # Paths (adjust these to your actual file locations)
    base_dir = os.path.dirname(__file__)
    uploads_dir = os.path.abspath(os.path.join(base_dir, "../../public/uploads"))
    
    # Look for CBIRR file
    official_pdf = None
    for filename in os.listdir(uploads_dir):
        if "CGBIRR" in filename and filename.endswith(".pdf"):
            official_pdf = os.path.join(uploads_dir, filename)
            break
    
    if not official_pdf:
        print("❌ Error: CGBIRR PDF not found in uploads directory")
        print(f"   Searched in: {uploads_dir}")
        return
    
    # For testing, we'll use the same CBIRR file as both pushed and official
    # In production, the pushed_pdf would be a different county document
    pushed_pdf = official_pdf
    
    print(f"\n📋 Test Configuration:")
    print(f"   County: {test_county}")
    print(f"   Merits: {', '.join(test_merits)}")
    print(f"   Official PDF: {os.path.basename(official_pdf)}")
    print(f"   Pushed PDF: {os.path.basename(pushed_pdf)}")
    print()
    
    # Run comparison
    result = await processor.compare(
        pushed_pdf_path=pushed_pdf,
        official_pdf_path=official_pdf,
        county_name=test_county,
        merits=test_merits
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    
    if result.get("status") == "error":
        print(f"❌ Error: {result.get('error')}")
        return
    
    print(f"\n🏛️  County: {result.get('county')}")
    print(f"📊 Integrity Score: {result.get('integrity_score')}/100")
    print(f"⚖️  Verdict: {result.get('verdict')}")
    
    if result.get('integrity_alerts'):
        print(f"\n🚨 Integrity Alerts ({len(result['integrity_alerts'])}):")
        for i, alert in enumerate(result['integrity_alerts'], 1):
            print(f"   {i}. {alert}")
    
    if result.get('merit_comparison'):
        print(f"\n📈 Merit Comparisons ({len(result['merit_comparison'])}):")
        for comp in result['merit_comparison']:
            status_icon = "✅" if comp.get('status') == 'verified' else "⚠️"
            print(f"\n   {status_icon} {comp.get('merit')}")
            print(f"      Official: {comp.get('official_value')} (Source: {comp.get('official_source', 'N/A')})")
            print(f"      Pushed:   {comp.get('pushed_value')} (Source: {comp.get('pushed_source', 'N/A')})")
            print(f"      Variance: {comp.get('variance_percent', 0):.1f}%")
            print(f"      Analysis: {comp.get('discrepancy')}")
    
    if result.get('data_quality_notes'):
        print(f"\n📝 Data Quality Notes:")
        print(f"   {result['data_quality_notes']}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_comparison())

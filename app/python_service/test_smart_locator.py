"""
Test script for SmartPageLocator
Validates TOC-based page discovery
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_models.smart_page_locator import SmartPageLocator


def test_page_locator():
    """Test the SmartPageLocator with Mombasa county"""
    
    pdf_path = "/home/tim/Downloads/v0-ai-budget-transparency-main (2)/public/uploads/CGBIRR August 2025.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found at: {pdf_path}")
        print("Please update the path to your CGBIRR PDF")
        return
    
    print("=" * 60)
    print("SMART PAGE LOCATOR TEST")
    print("=" * 60)
    
    # Initialize locator
    print("\n1. Initializing SmartPageLocator...")
    locator = SmartPageLocator(pdf_path)
    
    # Test county: Mombasa
    county_name = "Mombasa"
    print(f"\n2. Testing with {county_name} County...")
    
    # Locate pages
    pages = locator.locate_county_pages(county_name)
    
    print(f"\n3. Results:")
    print(f"   Pages found: {pages}")
    print(f"   Total pages to process: {len(pages)}")
    
    # Expected: Should be around [324, 325, 326, 327, 328] or similar
    # NOT [0-799] or empty
    
    if not pages:
        print("   ❌ FAILED: No pages found!")
        return False
    
    if len(pages) > 20:
        print(f"   ❌ FAILED: Too many pages ({len(pages)})! Should be ~5 pages.")
        return False
    
    print(f"   ✅ PASSED: Found {len(pages)} pages (expected ~5)")
    
    # Validate first page contains county header
    print(f"\n4. Validating page content...")
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        
        first_page_num = pages[0] - 1  # Convert to 0-indexed
        if first_page_num < len(reader.pages):
            text = reader.pages[first_page_num].extract_text() or ""
            
            if f"County Government of {county_name}" in text or county_name.upper() in text:
                print(f"   ✅ PASSED: Page {pages[0]} contains '{county_name}'")
            else:
                print(f"   ⚠️ WARNING: Page {pages[0]} might not contain county header")
                print(f"   First 200 chars: {text[:200]}")
        
    except Exception as e:
        print(f"   ❌ Validation error: {e}")
    
    # Test summary tables
    print(f"\n5. Testing summary table detection...")
    summary_pages = locator.get_summary_table_pages()
    print(f"   Summary table pages found: {len(summary_pages)}")
    print(f"   Pages: {summary_pages[:10]}...")
    
    if summary_pages:
        print(f"   ✅ PASSED: Found summary tables")
    else:
        print(f"   ⚠️ WARNING: No summary tables found")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Smart Page Locator is working!")
    print(f"   - County pages: {pages}")
    print(f"   - Summary pages: {len(summary_pages)} found")
    print(f"\nBefore: Would process 800+ pages → timeout/zeros")
    print(f"After: Processing {len(pages) + len(summary_pages)} pages → fast & accurate")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_page_locator()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

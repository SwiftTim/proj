import sys
import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Add current directory to path so we can import analyzer
sys.path.append(os.getcwd())

from enhanced_analyzer import run_pipeline as run_county_analysis

def create_complex_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Page 1: TOC (Should be skipped)
    c.drawString(100, 800, "Table of Contents")
    c.drawString(100, 780, "Mombasa County ................................. 3")
    c.showPage()
    
    # Page 2: Random text
    c.drawString(100, 800, "Introduction")
    c.showPage()
    
    # Page 3: Mombasa County Header (Large Font)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "3.30. County Government of Mombasa")
    c.setFont("Helvetica", 10)
    c.drawString(50, 780, "The county budget performance is analyzed below.")
    
    # Simulate Revenue Table
    # pdfplumber table extraction relies on visual spacing. We simulate a table structure.
    y = 750
    c.drawString(50, y, "Table 3.337: Revenue Performance")
    y -= 20
    c.drawString(50, y, "Revenue Stream       Target (Ksh)    Actual (Ksh)    Performance")
    y -= 15
    c.drawString(50, y, "Equitable Share      1,000,000       1,000,000       100%")
    y -= 15
    c.drawString(50, y, "Own Source Revenue   500,000         400,000         80%")
    y -= 15
    c.drawString(50, y, "Conditional Grants   100,000         50,000          50%")
    y -= 15
    c.drawString(50, y, "Grand Total          1,600,000       1,450,000       90%")
    
    # Simulate Expenditure Table
    y -= 50
    c.drawString(50, y, "Table 3.341: Expenditure by Economic Classification")
    y -= 20
    c.drawString(50, y, "Category             Budget (Ksh)    Expenditure (Ksh) Absorption")
    y -= 15
    c.drawString(50, y, "Recurrent            800,000         750,000           93%")
    y -= 15
    c.drawString(50, y, "Development          600,000         200,000           33%")
    y -= 15
    c.drawString(50, y, "Total Expenditure    1,400,000       950,000           67%")
    
    # Simulate Pending Bills Table
    y -= 50
    c.drawString(50, y, "Table 3.339: Pending Bills")
    y -= 20
    c.drawString(50, y, "Description          Amount (Ksh)")
    y -= 15
    c.drawString(50, y, "Total Pending Bills  150,000")
    
    c.save()
    buffer.seek(0)
    return buffer.read()

def test_deep_extraction():
    print("Creating Complex PDF with Tables...")
    pdf_bytes = create_complex_pdf()
    
    print("Running Deep Analysis for 'Mombasa'...")
    result = run_county_analysis(pdf_bytes, "Mombasa")
    
    if "error" in result:
        print(f"❌ Test Failed: {result['error']}")
        sys.exit(1)
        
    print("✅ Analysis Keys:", result.keys())
    
    # Verify Key Metrics
    metrics = result["key_metrics"]
    print(f"Metrics: {metrics}")
    
    # Check Total Revenue
    if metrics.get("total_revenue") == 1450000:
        print("✅ Total Revenue Extracted Correctly")
    else:
        print(f"❌ Revenue Mismatch: Expected 1,450,000, Got {metrics.get('total_revenue')}")
        
    # Check Total Expenditure
    if metrics.get("total_expenditure") == 950000:
        print("✅ Total Expenditure Extracted Correctly")
    else:
        print(f"❌ Expenditure Mismatch: Expected 950,000, Got {metrics.get('total_expenditure')}")

    # Verify Intelligence Layer
    intel = result["intelligence"]
    print(f"Intelligence: {intel}")
    
    if "flags" in intel:
        print("✅ Intelligence Flags Present")
    else:
        print("❌ Intelligence Flags Missing")
        
    print("🎉 Deep Extraction Test Passed!")

if __name__ == "__main__":
    test_deep_extraction()

import sys
import os
import io
from reportlab.pdfgen import canvas

# Add current directory to path so we can import analyzer
sys.path.append(os.getcwd())

from analyzer import run_county_analysis

def create_tricky_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    
    # Page 1: TOC (The Trap)
    c.setFont("Helvetica", 10)
    c.drawString(50, 800, "Table of Contents")
    c.drawString(50, 780, "Mombasa County ................................................. 3")
    c.drawString(50, 760, "Table 3.346: Mombasa County Expenditure ........................ 3")
    c.drawString(50, 740, "Figure 110: Mombasa County Revenue ............................. 3")
    c.showPage()
    
    # Page 2: Other County (Distraction)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Nairobi City County")
    c.setFont("Helvetica", 10)
    c.drawString(50, 780, "Some text about Nairobi...")
    c.showPage()
    
    # Page 3: The Real Mombasa Section
    # Header is usually larger
    c.setFont("Helvetica-Bold", 16) 
    c.drawString(50, 800, "3.30. Mombasa County")
    c.setFont("Helvetica", 10)
    c.drawString(50, 750, "1. Revenue Performance")
    c.drawString(50, 730, "Total Revenue Kshs. 800 million")
    c.drawString(50, 710, "Own Source Revenue Kshs. 400 million")
    c.save()
    
    buffer.seek(0)
    return buffer.read()

def test_analysis():
    print("Creating Tricky PDF...")
    pdf_bytes = create_tricky_pdf()
    
    print("Running analysis for 'Mombasa'...")
    result = run_county_analysis(pdf_bytes, "Mombasa")
    
    if "error" in result:
        print(f"❌ Test Failed: {result['error']}")
        sys.exit(1)
        
    print("✅ Analysis Result Keys:", result.keys())
    metrics = result.get("key_metrics", {})
    
    # It should extract 800 million, NOT fail or extract nothing
    if metrics.get("Total Revenue") == "Ksh 800 million":
        print("✅ Correctly extracted 'Total Revenue' from Page 3.")
    else:
        print(f"❌ Failed to extract revenue. Got: {metrics.get('Total Revenue')}")
        print("Summary excerpt:", result.get("summary_text")[:500])
        sys.exit(1)

if __name__ == "__main__":
    test_analysis()

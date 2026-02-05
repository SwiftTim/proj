from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat, DocumentInput
import tempfile
import os
import uvicorn
import nest_asyncio
from pyngrok import ngrok
import re
import torch

# This allows uvicorn to run inside the Colab notebook event loop
nest_asyncio.apply()

app = FastAPI(title="Docling Colab GPU Server")

# Initialize Docling with GPU options
print("⏳ Loading Docling models...")
options = PdfPipelineOptions()
options.do_table_structure = True
options.do_ocr = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=options)
    }
)
print("✅ Models Loaded!")

@app.get("/")
def read_root():
    return {"status": "Docling GPU Server is Online", "gpu_available": torch.cuda.is_available()}

@app.post("/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    county: str = Form(...)
):
    """
    Receives a PDF file and a county name. 
    Returns high-fidelity Markdown filtered for that county.
    """
    print(f"📥 Received file: {file.filename} for county: {county}")
    
    # Save to a real file path
    pdf_path = f"/tmp/{file.filename}"
    with open(pdf_path, "wb") as f:
        content = await file.read()
        f.write(content)
        f.flush()

    try:
        # Run Docling conversion
        print(f"⚙️ Processing {file.filename} with Docling...")
        
        doc = DocumentInput.from_file(pdf_path)
        result = converter.convert(doc)
        
        markdown = result.document.export_to_markdown()
        print(f"✅ Conversion complete. Markdown length: {len(markdown)}")
        
        # --- DYNAMIC COUNTY EXTRACTION ---
        lines = markdown.splitlines()
        header = None
        county_rows = []

        # Identify header (first line with pipes and "County")
        for line in lines:
            if "County" in line and "|" in line:
                header = line
                break

        # Extract only lines matching the county (case-insensitive)
        for line in lines:
            if re.search(rf"\b{re.escape(county)}\b", line, re.IGNORECASE):
                # Clean extra spaces before pipes
                clean_line = re.sub(r"\s+\|", " |", line)
                county_rows.append(clean_line.strip())

        if not county_rows:
            county_rows = [f"⚠️ {county} data not found in Docling output"]

        # Prepend header if found
        if header:
            # Add separator line if it's missing or if we want a clean MD table
            county_rows.insert(0, "|---|---|---|---|---|---|---|---|") # Simple MD divider
            county_rows.insert(0, header)

        county_markdown = "\n".join(county_rows)

        return {
            "success": True,
            "markdown": county_markdown,
            "county": county,
            "filename": file.filename
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

# --- NGROK SETUP ---
def start_ngrok():
    ngrok.kill()
    ngrok.set_auth_token("2bgNrSjCqjzMq8K9CjlT5GN0tFp_5ahs5AUfSTpj3Cq4VvNHF")
    public_url = ngrok.connect(8000)
    print("\n" + "="*50)
    print(f"🚀 DOCLING COLAB URL: {public_url}")
    print("="*50 + "\n")
    return public_url

if __name__ == "__main__":
    # Start Ngrok
    public_url = start_ngrok()
    
    # Run Uvicorn directly (nest_asyncio permits this)
    uvicorn.run(app, host="0.0.0.0", port=8000)

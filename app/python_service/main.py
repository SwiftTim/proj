from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from enhanced_analyzer import run_county_analysis

app = FastAPI(
    title="Budget Integrity Analyzer API",
    description="Analyzes county budget PDFs and returns structured financial summaries.",
    version="2.0.0"
)

# Enable CORS for your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "✅ Budget Analyzer API is live",
        "usage": "POST /analyze_pdf with 'file' (PDF) and 'county' (string)"
    }


@app.post("/analyze_pdf")
async def analyze_pdf(
    file: UploadFile = File(...),
    county: str = Form(...)
):
    """
    Receives a county PDF and extracts key financial information
    using run_county_analysis() from analyzer.py
    """
    try:
        # --- Read PDF ---
        pdf_bytes = await file.read()
        print(f"📂 Received PDF: {file.filename}, County: {county}")

        # --- Run Analyzer ---
        result = run_county_analysis(pdf_bytes, county)
        if "error" in result:
            print(f"⚠️ Analysis error: {result['error']}")
            return {"success": False, "error": result["error"]}

        # --- Return structured JSON for frontend ---
        print(f"✅ Analysis complete for {county}: keys={list(result.keys())}")
        return {
            "success": True,
            "county": result["county"],
            "summary_text": result.get("summary_text", "No summary available."),
            "key_metrics": result.get("key_metrics", {})
        }

    except Exception as e:
        print("🚨 Error during analysis:", str(e))
        return {"success": False, "error": str(e)}

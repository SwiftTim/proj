from fastapi import FastAPI, File, Form, UploadFile, Body, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from comparison_engine import ComparisonEngine
from report_generator import ReportGenerator
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import tempfile
import os
import shutil
import json
from dotenv import load_dotenv
from datetime import date, datetime

# Load environment variables from .env or .env.local
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env.local"))

# Import new Hybrid Processor
from hybrid_processor import HybridBudgetProcessor
from docling_processor import DoclingProcessor
from gemini_processor import GeminiBudgetProcessor

from comparison_processor import GeminiComparisonProcessor

# Import Hot Take functionality
from hot_take_extractor import HotTakeExtractor
from hot_take_scheduler import get_scheduler
from merit_mapper import MeritMapper
from db import get_db_connection, init_db

app = FastAPI(
    title="Budget Integrity Analyzer API",
    description="Analyzes county budget PDFs and returns structured financial summaries.",
    version="2.3.0"
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
        "usage": "POST /analyze_pdf with 'file' (PDF), 'county' (string), and 'method' (local|ai)"
    }

class GPUAnalysisRequest(BaseModel):
    pdf_id: str
    county: str
    extraction_model: Optional[str] = "ocrflux-3b"
    analysis_model: Optional[str] = "groq-llama-70b"
    use_vision: bool = True

@app.post("/analyze/gpu")
async def gpu_analysis_endpoint(
    request: GPUAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Hybrid AI Analysis Pipeline:
    Stage 1: OCRFlux-3B (Vision-based table extraction)
    Stage 2: Groq LLaMA-70B (Fiscal analysis & risk assessment)
    """
    print(f"🚀 Starting GPU Analysis for {request.county} (PDF: {request.pdf_id})")
    
    # Initialize hybrid processor
    processor = HybridBudgetProcessor()
    
    try:
        # Check if pdf_id is a file path that exists, otherwise we might fail
        if not os.path.exists(request.pdf_id):
             # Try to resolve relative to public/uploads
             # Assuming script is in app/python_service, public/uploads is at ../../public/uploads
             possible_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../public/uploads", request.pdf_id))
             
             if os.path.exists(possible_path):
                 print(f"📂 Found PDF at resolved path: {possible_path}")
                 request.pdf_id = possible_path
             else:
                 print(f"⚠️ PDF not found at {request.pdf_id} or {possible_path}")
                 # We'll fail later if not found
                 pass

        # Run the pipeline
        result = await processor.process(
            pdf_path=request.pdf_id,
            county_name=request.county
        )
        
        print(f"📦 GPU Analysis Response Data: {json.dumps(result, indent=2)}")
        return {
            "status": "success",
            "method": "hybrid_ocrflux_groq",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ GPU Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"GPU Analysis failed: {str(e)}."
        )


class DoclingAnalysisRequest(BaseModel):
    pdf_id: str
    county: str

@app.post("/analyze/docling")
async def docling_analysis_endpoint(
    request: DoclingAnalysisRequest
):
    """
    Docling Extraction Pipeline:
    Stage 1: Docling (PDF to Markdown conversion with high fidelity)
    Stage 2: Groq LLaMA-70B (Fiscal analysis & risk assessment)
    """
    print(f"📄 Starting Docling Extract for {request.county} (PDF: {request.pdf_id})")
    
    # Initialize Docling processor
    processor = DoclingProcessor()
    
    try:
        # Resolve PDF Path
        if not os.path.exists(request.pdf_id):
             possible_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../public/uploads", request.pdf_id))
             if os.path.exists(possible_path):
                 print(f"📂 Found PDF at resolved path: {possible_path}")
                 request.pdf_id = possible_path
             else:
                 print(f"⚠️ PDF not found at {request.pdf_id} or {possible_path}")

        # Run the pipeline
        result = await processor.process(
            pdf_path=request.pdf_id,
            county_name=request.county
        )
        
        if result.get("status") == "error":
             raise HTTPException(status_code=500, detail=result.get("error"))
             
        return result
        
    except Exception as e:
        print(f"❌ Docling Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Docling Analysis failed: {str(e)}."
        )


class GeminiAnalysisRequest(BaseModel):
    pdf_id: str
    county: str

@app.post("/analyze/gemini")
async def gemini_analysis_endpoint(
    request: GeminiAnalysisRequest
):
    """
    Google Gemini Direct Extraction Pipeline:
    Sends the entire PDF to Gemini for zero-shot data extraction.
    """
    print(f"🌟 Starting Google Gemini Analysis for {request.county} (PDF: {request.pdf_id})")
    
    # Initialize Gemini processor
    processor = GeminiBudgetProcessor()
    
    try:
        # Resolve PDF Path
        if not os.path.exists(request.pdf_id):
             possible_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../public/uploads", request.pdf_id))
             if os.path.exists(possible_path):
                 print(f"📂 Found PDF at resolved path: {possible_path}")
                 request.pdf_id = possible_path
             else:
                 print(f"⚠️ PDF not found at {request.pdf_id} or {possible_path}")

        # Run the pipeline
        result = await processor.process(
            pdf_path=request.pdf_id,
            county_name=request.county
        )
        
        if result.get("status") == "error":
             raise HTTPException(status_code=500, detail=result.get("error"))
             
        return result
        
    except Exception as e:
        print(f"❌ Gemini Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Gemini Analysis failed: {str(e)}."
        )



@app.post("/compare_counties")
async def compare_counties(
    data: Dict[str, Any] = Body(...)
):
    """
    Compare two counties.
    Expects JSON: { "county_a": {...}, "county_b": {...} }
    """
    try:
        engine = ComparisonEngine()
        comparison = engine.compare_counties(data["county_a"], data["county_b"])
        return {"success": True, "comparison": comparison}
    except Exception as e:
        return {"success": False, "error": str(e)}

class GeminiCompareRequest(BaseModel):
    pushed_pdf_id: str
    county: str
    merits: List[str]

@app.post("/compare/gemini")
async def compare_gemini_endpoint(request: GeminiCompareRequest):
    """
    Gemini PDF Push & Compare Pipeline.
    """
    print(f"🕵️ Starting Gemini Comparison for {request.county}")
    
    # Resolve Pushed PDF Path
    pushed_path = request.pushed_pdf_id
    if not os.path.exists(pushed_path):
        pushed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../public/uploads", request.pushed_pdf_id))
    
    # Resolve Official CBIRR Path (Hardcoded for this demo to the known official report)
    official_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../public/uploads/CGBIRR August 2025.pdf"))
    
    if not os.path.exists(pushed_path):
        raise HTTPException(status_code=404, detail=f"Pushed PDF not found: {request.pushed_pdf_id}")
    if not os.path.exists(official_path):
        # Fallback to any file starting with CGBIRR August 2025
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../public/uploads"))
        fallback = [f for f in os.listdir(uploads_dir) if "CGBIRR August 2025" in f and f.endswith(".pdf")]
        if fallback:
            official_path = os.path.join(uploads_dir, fallback[0])
        else:
            raise HTTPException(status_code=404, detail="Official CBIRR reference PDF not found in uploads.")

    processor = GeminiComparisonProcessor()
    try:
        result = await processor.compare(
            pushed_pdf_path=pushed_path,
            official_pdf_path=official_path,
            county_name=request.county,
            merits=request.merits
        )
        return {"success": True, "data": result}
    except Exception as e:
        print(f"❌ Gemini Comparison Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rank_counties")
async def rank_counties(
    data: Dict[str, Any] = Body(...)
):
    """
    Rank counties.
    Expects JSON: { "counties": [...], "metric": "revenue" }
    """
    try:
        engine = ComparisonEngine()
        ranking = engine.rank_counties(data["counties"], data.get("metric", "revenue"))
        return {"success": True, "ranking": ranking}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/generate_report")
async def generate_report(
    data: Dict[str, Any] = Body(...)
):
    """
    Generate a report format.
    Expects JSON: { "data": {...}, "format": "markdown" }
    """
    try:
        gen = ReportGenerator()
        report_struct = gen.generate_report(data["data"])
        
        if data.get("format") == "markdown":
            md = gen.generate_markdown(report_struct)
            return {"success": True, "report": md, "format": "markdown"}
        
        return {"success": True, "report": report_struct, "format": "json"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# HOT TAKE / TRENDING MERITS ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize database and start the hot take scheduler on app startup.
    """
    print("🚀 Starting Budget Analyzer API...")
    
    # Initialize database tables
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    # Start the hot take scheduler
    try:
        scheduler = get_scheduler()
        scheduler.start()
        print("✅ Hot Take Scheduler started")
    except Exception as e:
        print(f"⚠️ Scheduler initialization warning: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Gracefully shutdown the scheduler.
    """
    print("🛑 Shutting down Budget Analyzer API...")
    try:
        scheduler = get_scheduler()
        scheduler.stop()
        print("✅ Hot Take Scheduler stopped")
    except Exception as e:
        print(f"⚠️ Scheduler shutdown warning: {e}")


@app.get("/api/trending-merits")
async def get_trending_merits(days: int = 7):
    """
    Fetch cached trending merits (hot takes) from the database.
    
    Query Parameters:
        days: Number of days to look back (default: 7)
    
    Returns:
        List of trending merits with mapped fields
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch recent hot takes
        cur.execute("""
            SELECT 
                id, date, topic_name, description, keywords, 
                priority_score, daily_audit, economic_ticker, created_at
            FROM trending_merits
            WHERE date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY date DESC, priority_score DESC
            LIMIT 10
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format results
        merits = []
        mapper = MeritMapper()
        
        for row in rows:
            merit = {
                "id": row["id"],
                "date": row["date"].isoformat() if row["date"] else None,
                "topic_name": row["topic_name"],
                "description": row["description"],
                "keywords": row["keywords"],
                "priority_score": row["priority_score"],
                "daily_audit": row["daily_audit"],
                "economic_ticker": row["economic_ticker"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            
            # Enhance with mapper data
            if row["keywords"]:
                mapped_data = mapper.map_keywords_to_fields(row["keywords"])
                merit["data_fields"] = mapped_data
            
            merits.append(merit)
        
        return {
            "success": True,
            "count": len(merits),
            "merits": merits
        }
        
    except Exception as e:
        print(f"❌ Error fetching trending merits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trending-merits/{merit_id}/data")
async def get_merit_data(merit_id: int, counties: Optional[str] = None):
    """
    Get mapped budget data for a specific trending merit across counties.
    
    Path Parameters:
        merit_id: ID of the trending merit
    
    Query Parameters:
        counties: Comma-separated list of county names (optional, defaults to all)
    
    Returns:
        Visualization-ready data for the merit
    """
    try:
        # Fetch the merit
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT topic_name, keywords, mapped_fields
            FROM trending_merits
            WHERE id = %s
        """, (merit_id,))
        
        merit = cur.fetchone()
        
        if not merit:
            raise HTTPException(status_code=404, detail="Merit not found")
        
        # For now, return mock visualization data
        # In production, this would query actual county budget data
        mapper = MeritMapper()
        mapped_fields = mapper.map_keywords_to_fields(merit["keywords"])
        
        # Mock data structure for visualization
        visualization_data = {
            "merit_id": merit_id,
            "topic_name": merit["topic_name"],
            "mapped_fields": mapped_fields,
            "chart_type": "bar",  # Could be dynamic based on merit type
            "data": {
                "labels": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Machakos"],
                "datasets": [
                    {
                        "label": mapped_fields[0]["field_name"] if mapped_fields else "Value",
                        "data": [450000000, 280000000, 180000000, 220000000, 150000000],
                        "backgroundColor": "rgba(59, 130, 246, 0.5)",
                        "borderColor": "rgb(59, 130, 246)",
                        "borderWidth": 2
                    }
                ]
            },
            "note": "This is mock data. In production, this would fetch real CBIRR data."
        }
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "data": visualization_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching merit data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trigger-hot-take-analysis")
async def trigger_hot_take_analysis():
    """
    Manually trigger hot take extraction (for testing/admin purposes).
    
    This endpoint allows manual triggering of the daily extraction process
    without waiting for the scheduled time.
    """
    try:
        extractor = HotTakeExtractor()
        result = await extractor.run_daily_extraction()
        
        return {
            "success": result["status"] == "success",
            "message": result["message"],
            "data": result.get("data")
        }
        
    except Exception as e:
        print(f"❌ Manual trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

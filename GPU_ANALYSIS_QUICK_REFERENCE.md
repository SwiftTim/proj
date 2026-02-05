# GPU Analysis Quick Reference Guide

## 🚀 Quick Start

### Running the GPU Analysis

1. **Start the backend**:
   ```bash
   cd app/python_service
   uvicorn main:app --reload
   ```

2. **Open the frontend** and navigate to the Analysis tab

3. **Select county and year** from dropdowns

4. **Click "GPU Analysis (OCRFlux)"** button (purple button)

5. **Wait 30-90 seconds** for processing

6. **View results** displayed automatically

---

## 🔑 Key Environment Variables

```bash
# Required
HF_API_KEY=hf_xxxxxxxxxxxxx          # HuggingFace API key
GROQ_API_KEY=gsk_xxxxxxxxxxxxx       # Groq API key

# Optional
OCRFLUX_URL=http://localhost:5000    # Local OCRFlux instance
```

---

## 📊 What Gets Extracted

### Revenue Metrics
- OSR Target (Own Source Revenue target)
- OSR Actual (Actual revenue collected)
- OSR Performance % (Performance percentage)
- Equitable Share (Government allocation)

### Expenditure Metrics
- Total Expenditure
- Recurrent Expenditure
- Development Expenditure
- Development Absorption %
- Overall Absorption %
- Recurrent Exchequer
- Development Exchequer

### Debt Metrics
- Pending Bills (Total)
- Pending Bills > 3 Years

### Health FIF Metrics
- SHA Approved (Social Health Authority approved)
- SHA Paid (Amount paid)
- Payment Rate %

### Analysis Outputs
- Integrity Scores (Transparency, Compliance, Fiscal Health, Overall)
- Risk Assessment (Level: High/Moderate/Low, Score: 0-100)
- Executive Summary (3-4 sentences)
- Recommendations (for Executive, Assembly, Citizens)
- Anomalies (Detected issues)

---

## 🐛 Debugging Commands

### Test the full pipeline
```bash
cd app/python_service
python debug_gpu_pipeline.py
```

### Check API connectivity
```bash
curl -X POST http://127.0.0.1:8000/analyze/gpu \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_id": "CGBIRR August 2025.pdf",
    "county": "Mombasa",
    "extraction_model": "ocrflux-3b",
    "analysis_model": "groq-llama-70b",
    "use_vision": true
  }'
```

### View backend logs
```bash
# Backend logs show:
# 🚀 Starting GPU Analysis for {county}
# 🔍 Stage 1: OCRFlux extracting...
# 📊 Found summary table {page}
# 📍 Found {county} main section on page {page}
# 🧠 Stage 1.5: Intelligent Parsing via Groq...
# 🧬 Stage 2: Insights & Fiscal Analysis...
# ✅ Analysis complete
```

---

## 📁 Target Tables in CGBIRR PDFs

| Table | Description | Typical Pages |
|-------|-------------|---------------|
| 2.1 | Own Source Revenue Performance | 40-120 |
| 2.5 | Budget Allocations & Absorption | 40-120 |
| 2.9 | Pending Bills | 40-120 |
| 2.2 | Health FIF (SHA Payments) | 40-120 |
| 3.X | County-Specific Section | Varies (discovered) |

---

## ⚡ Performance Tips

1. **Use local OCRFlux** for faster processing (set `OCRFLUX_URL`)
2. **Pre-warm HuggingFace models** by making a test call
3. **Ensure good PDF quality** (200+ DPI recommended)
4. **Check page discovery** - verify correct pages are being processed

---

## 🔄 API Request/Response Format

### Request
```json
{
  "pdf_id": "CGBIRR August 2025.pdf",
  "county": "Mombasa",
  "extraction_model": "ocrflux-3b",
  "analysis_model": "groq-llama-70b",
  "use_vision": true
}
```

### Response
```json
{
  "status": "success",
  "method": "hybrid_ocrflux_groq",
  "data": {
    "extraction": {
      "county": "Mombasa",
      "fiscal_year": "2024/25",
      "revenue": { ... },
      "expenditure": { ... },
      "debt": { ... },
      "health_fif": { ... }
    },
    "analysis": {
      "integrity_scores": { ... },
      "risk_assessment": { ... },
      "executive_summary": "...",
      "recommendations": { ... },
      "anomalies": [ ... ]
    },
    "metadata": {
      "ocrflux_confidence": 0.95,
      "processing_method": "hybrid_ocrflux_groq_v2"
    }
  }
}
```

---

## 🎯 Risk Scoring Rules

| Risk Level | Criteria |
|------------|----------|
| **High (>70)** | OSR <50% OR Dev Absorption <30% OR Pending Bills >40% of budget |
| **Moderate (40-70)** | OSR 50-70% OR Dev Absorption 30-60% |
| **Low (<40)** | OSR >80% AND Absorption >70% |

---

## 🛠️ Common Fixes

### Problem: "Connection Error: Is the local Python backend running?"
**Solution**: Start FastAPI server
```bash
cd app/python_service
uvicorn main:app --reload
```

### Problem: Zero values returned
**Solution**: Check page discovery and OCRFlux output
```bash
python debug_gpu_pipeline.py
# Look for "📊 Found summary table" messages
```

### Problem: "Model loading, waiting 20s..."
**Solution**: Wait for HuggingFace cold start, or use local OCRFlux

### Problem: Groq parsing failed
**Solution**: System automatically falls back to regex parser

---

## 📞 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/analyze/gpu` | POST | GPU-accelerated hybrid analysis |
| `/analyze_pdf` | POST | Standard analysis (local/ai/hybrid) |
| `/` | GET | Health check |

---

## 🔐 Security Notes

- API keys should be in `.env.local` (not committed to git)
- FastAPI runs on localhost:8000 (not exposed publicly)
- CORS is enabled for frontend communication

---

## 📚 Related Files

- **Workflow**: `.agent/workflows/gpu-analysis-workflow.md`
- **Debug Script**: `app/python_service/debug_gpu_pipeline.py`
- **Main Endpoint**: `app/python_service/main.py`
- **Frontend Button**: `components/gpu-analysis-button.tsx`
- **Analysis UI**: `components/analysis-module.tsx`

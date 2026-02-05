# 🚀 Application Startup Guide

## Quick Start (2 Steps)

### **Step 1: Start Backend (Python FastAPI)**

Open a terminal and run:

```bash
cd app/python_service
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process using StatReload
```

✅ **Backend is ready when you see**: `Uvicorn running on http://127.0.0.1:8000`

---

### **Step 2: Start Frontend (Next.js)**

Open a **NEW** terminal (keep backend running) and run:

```bash
npm run dev
```

**Expected Output**:
```
> budget-transparency@0.1.0 dev
> next dev

  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

✓ Ready in 2.5s
```

✅ **Frontend is ready when you see**: `Ready in X.Xs`

---

## **Step 3: Access the Application**

Open your browser and go to:

```
http://localhost:3000
```

---

## **Current Status** ✅

Both services are now running:

- ✅ **Backend**: http://127.0.0.1:8000
- ✅ **Frontend**: http://localhost:3000

---

## **Testing the GPU Analysis**

1. **Navigate to Analysis Tab** in the web interface

2. **Select County and Year**:
   - County: Mombasa
   - Year: 2025

3. **Click "GPU Analysis (OCRFlux)" button** (purple button)

4. **Wait 30-60 seconds** for processing

5. **View Results**:
   - OSR Actual: Should show non-zero value (e.g., Ksh 4,880,829,952)
   - Total Expenditure: Should show non-zero value
   - Risk Assessment: High/Moderate/Low
   - Executive Summary: AI-generated insights

---

## **Troubleshooting**

### Issue: "Connection Error: Is the local Python backend running?"

**Solution**: Make sure backend is running on port 8000
```bash
# Check if backend is running
curl http://127.0.0.1:8000/

# Should return: {"message": "✅ Budget Analyzer API is live", ...}
```

### Issue: "Module not found" errors in backend

**Solution**: Install Python dependencies
```bash
cd app/python_service
pip install -r requirements.txt
```

### Issue: Frontend won't start

**Solution**: Install Node dependencies
```bash
npm install
```

### Issue: GPU Analysis returns zeros

**Solution**: 
1. Check environment variables in `.env.local`:
   ```bash
   GROQ_API_KEY=gsk_xxxxxxxxxxxxx
   HF_API_KEY=hf_xxxxxxxxxxxxx  # Optional
   OCRFLUX_URL=https://...      # Optional (Google Colab)
   ```

2. Test the smart locator:
   ```bash
   cd app/python_service
   python test_smart_locator.py
   ```

---

## **Environment Variables Setup**

Create/edit `.env.local` in the project root:

```bash
# Required for GPU Analysis
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Optional: HuggingFace API (fallback)
HF_API_KEY=hf_xxxxxxxxxxxxx

# Optional: Google Colab OCRFlux instance (recommended)
OCRFLUX_URL=https://your-ngrok-url.ngrok.io
```

---

## **Stopping the Application**

### Stop Backend:
Press `Ctrl+C` in the backend terminal

### Stop Frontend:
Press `Ctrl+C` in the frontend terminal

---

## **Development Workflow**

### **Terminal 1: Backend**
```bash
cd app/python_service
uvicorn main:app --reload
```
- Auto-reloads on Python file changes
- API available at http://127.0.0.1:8000
- API docs at http://127.0.0.1:8000/docs

### **Terminal 2: Frontend**
```bash
npm run dev
```
- Auto-reloads on file changes
- App available at http://localhost:3000

### **Terminal 3: Testing/Debugging**
```bash
# Test smart locator
cd app/python_service
python test_smart_locator.py

# Test full pipeline
python debug_gpu_pipeline.py

# Run other tests
python test_hybrid_pipeline.py
```

---

## **API Endpoints**

Once backend is running, you can test these endpoints:

### Health Check
```bash
curl http://127.0.0.1:8000/
```

### GPU Analysis
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

### Standard Analysis
```bash
curl -X POST http://127.0.0.1:8000/analyze_pdf \
  -F "file=@/path/to/pdf.pdf" \
  -F "county=Mombasa" \
  -F "method=local"
```

---

## **Production Deployment**

### Backend (FastAPI)
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
cd app/python_service
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Next.js)
```bash
# Build for production
npm run build

# Start production server
npm start
```

---

## **Port Configuration**

| Service | Port | URL |
|---------|------|-----|
| **Frontend** | 3000 | http://localhost:3000 |
| **Backend** | 8000 | http://127.0.0.1:8000 |
| **Backend Docs** | 8000 | http://127.0.0.1:8000/docs |

---

## **Logs and Debugging**

### Backend Logs
Backend logs appear in the terminal where you ran `uvicorn`:
```
🚀 Starting GPU Analysis for Mombasa
🔍 Smart Discovery: Locating Mombasa using TOC-based algorithm...
📚 TOC extracted: 47 counties found
📍 Located Mombasa section: pages [324, 325, 326, 327, 328]
✅ Analysis complete
```

### Frontend Logs
Frontend logs appear in:
1. **Terminal**: Build and server logs
2. **Browser Console**: Client-side logs (F12 → Console)

---

## **Quick Commands Reference**

```bash
# Start backend
cd app/python_service && uvicorn main:app --reload

# Start frontend
npm run dev

# Test smart locator
cd app/python_service && python test_smart_locator.py

# Test full pipeline
cd app/python_service && python debug_gpu_pipeline.py

# Install backend dependencies
cd app/python_service && pip install -r requirements.txt

# Install frontend dependencies
npm install

# Check backend health
curl http://127.0.0.1:8000/

# View API documentation
# Open browser: http://127.0.0.1:8000/docs
```

---

## **System Requirements**

### Backend
- Python 3.8+
- pip
- Virtual environment (recommended)

### Frontend
- Node.js 18+
- npm or yarn

### Optional
- Google Colab account (for OCRFlux)
- ngrok (for Colab tunneling)

---

## **First-Time Setup**

### 1. Install Backend Dependencies
```bash
cd app/python_service
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
npm install
```

### 3. Set Environment Variables
```bash
# Create .env.local in project root
echo "GROQ_API_KEY=your_key_here" > .env.local
```

### 4. Start Both Services
```bash
# Terminal 1: Backend
cd app/python_service && uvicorn main:app --reload

# Terminal 2: Frontend
npm run dev
```

### 5. Open Browser
```
http://localhost:3000
```

---

## **Success Checklist**

✅ Backend running on http://127.0.0.1:8000  
✅ Frontend running on http://localhost:3000  
✅ Environment variables set in `.env.local`  
✅ Can access app in browser  
✅ GPU Analysis button visible in Analysis tab  
✅ Test returns non-zero values  

---

**You're all set! 🎉**

The application is now running with the optimized GPU Analysis feature using smart page localization.

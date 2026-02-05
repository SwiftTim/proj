# BudgetAI: AI-Powered County Budget Transparency Platform

BudgetAI is a comprehensive platform designed to transform government budget documents (specifically Kenyan County Budget Implementation Review Reports - CBIRR) into actionable insights using advanced AI and PDF parsing technologies.

![Project Status](https://img.shields.io/badge/Status-Prototype-orange)
![Tech Stack](https://img.shields.io/badge/Stack-Next.js_14_|_FastAPI_|_PostgreSQL-blue)

## 🏗 System Architecture

The project consists of two main components:
1.  **Frontend (Next.js):** A modern, interactive dashboard for users to upload documents, view analyses, and compare counties.
2.  **Backend (Python Service):** An intelligent processing engine that extracts financial data from complex PDF reports.

### 1. Frontend (Next.js App)
Located in the `app/` and `components/` directories.

*   **Framework:** Next.js 14 (App Router) with TypeScript.
*   **UI Library:** Shadcn UI + Tailwind CSS.
*   **Key Features:**
    *   **Dashboard:** Central hub (`app/dashboard/page.tsx`) with tabs for:
        *   **Overview:** Visual charts and stats.
        *   **Upload:** Drag-and-drop PDF upload (`components/upload-module.tsx`).
        *   **Analysis:** Detailed scorecard views of specific counties (`components/analysis-module.tsx`).
        *   **Comparison:** Side-by-side county benchmarking.
    *   **Authentication:** Simulated auth flow for role-based access (Researcher, Journalist, Government).
    *   **Direct API Integration:** The frontend directly communicates with the Python backend for real-time analysis.

### 2. Backend (Python Service)
Located in `app/python_service/`.

*   **Framework:** FastAPI (`main.py`).
*   **Core Functionality:**
    *   **Hybrid Extraction Engine:**
        *   **Method A (Local Enhanced):** Uses `enhanced_analyzer.py` to map the PDF Table of Contents, convert specific pages to Markdown, and apply a "Regex Sieve" to extract high-confidence metrics (e.g., "Own Source Revenue"). Fast and free.
        *   **Method B (AI-Powered):** Uses `ai_analyzer.py` as a fallback. It sends PDF content to LLMs (OpenAI GPT-4o or Llama via Groq) to find complex or missing data points.
    *   **Comparison Engine:** Logic for ranking and benchmarking counties.
    *   **Report Generation:** Automatic creation of PDF summaries using extracted data.

## 🚀 Getting Started

### Prerequisites
*   Node.js 18+
*   Python 3.10+
*   PostgreSQL (optional, for persistent storage)
*   API Keys (OpenAI or Groq) for AI features.

### 1. Start the Backend
```bash
cd app/python_service
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Create .env.local file with your API keys
# OPENAI_API_KEY=sk-...
# GROQ_API_KEY=gsk_...

# Run the server
uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend
Open a new terminal in the project root:
```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Visit `http://localhost:3000` to access the application.

## 📂 Key Directories

| Directory | Description |
|bbox|---|
| `app/` | Next.js App Router pages and layouts. |
| `app/python_service/` | FastAPI backend and extraction logic. |
| `components/` | Reusable UI components (Shadcn) and feature modules. |
| `public/uploads/` | Storage for uploaded PDF budget reports. |

## 🧠 Extraction Logic Details

The system handles the complexity of CBIRR reports (often 100+ pages) through a smart pipeline:
1.  **TOC Mapping:** Identifies exactly which pages belong to a specific county (e.g., "Mombasa").
2.  **Targeted OCR:** Converts only the relevant pages to Markdown.
3.  **Regex Extraction:** Scans for standard financial terms.
4.  **AI Intelligence:** Calculates "Transparency Risk Scores" and flags anomalies (e.g., abnormally high pending bills).
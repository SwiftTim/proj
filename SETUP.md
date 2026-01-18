# Budget Transparency Project - Setup Guide

## Overview

This is an AI-powered budget transparency platform that analyzes county budget PDFs using Next.js and Python FastAPI.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** 18+ and npm
- **Python** 3.8+
- **PostgreSQL** 14+

## Quick Start

### 1. Database Setup

First, create a PostgreSQL database:

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE budget_transparency;

# Exit psql
\q

# Run the schema
psql -U postgres -d budget_transparency -f database/schema.sql
```

### 2. Environment Configuration

Create a `.env.local` file in the project root:

```bash
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/budget_transparency
NEXT_PUBLIC_API_URL=http://localhost:3000
PYTHON_SERVICE_URL=http://localhost:8000
```

### 3. Python Service Setup

```bash
# Navigate to Python service directory
cd app/python_service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Next.js Frontend Setup

```bash
# Navigate back to project root
cd ../..

# Install Node dependencies
npm install
```

## Running the Application

You'll need **two terminal windows** to run both services:

### Terminal 1: Python FastAPI Service

```bash
cd app/python_service
source venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload --port 8000
```

The Python API will be available at: http://localhost:8000

### Terminal 2: Next.js Development Server

```bash
npm run dev
```

The web application will be available at: http://localhost:3000

## Testing the Application

1. Open your browser to http://localhost:3000
2. Navigate to the upload section
3. Select a county budget PDF file
4. Choose the county name and year
5. Click "Analyze" to process the PDF
6. View the extracted financial data and insights

## Project Structure

```
.
├── app/
│   ├── api/              # Next.js API routes
│   ├── python_service/   # FastAPI backend
│   │   ├── analyzer.py   # PDF analysis logic
│   │   ├── main.py       # FastAPI app
│   │   └── requirements.txt
│   └── page.tsx          # Main frontend page
├── components/           # React components
├── database/
│   └── schema.sql        # PostgreSQL schema
├── public/               # Static assets
└── package.json          # Node dependencies
```

## API Endpoints

### Python Service (Port 8000)

- `GET /` - Health check
- `POST /analyze_pdf` - Analyze a county budget PDF
  - Parameters: `file` (PDF), `county` (string)

### Next.js API (Port 3000)

- `POST /api/analyze` - Proxy to Python service
- `POST /api/upload` - Upload and store PDFs
- `GET /api/documents` - List uploaded documents

## Troubleshooting

### Python Service Won't Start

- Ensure virtual environment is activated
- Check all dependencies are installed: `pip list`
- Verify Python version: `python --version` (should be 3.8+)

### Database Connection Errors

- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check DATABASE_URL in `.env.local`
- Ensure database exists: `psql -l`

### Next.js Build Errors

- Clear cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 18+)

### Port Already in Use

If port 8000 or 3000 is already in use:
```bash
# Find process using port
lsof -i :8000
# Kill the process
kill -9 <PID>
```

## Development Notes

### PDF Analysis Features

The analyzer supports:
- Multi-strategy extraction (structured tables, text-based, regex)
- 40+ field label variations
- Pending bills aging breakdown
- Advanced computed metrics
- Risk scoring and intelligence

### Database Schema

- `uploads`: Tracks uploaded PDF files
- `analysis_results`: Stores extracted financial data

## Production Deployment

For production deployment:

1. Set up a production PostgreSQL database
2. Update environment variables for production
3. Build the Next.js app: `npm run build`
4. Deploy Python service with a production ASGI server
5. Use a reverse proxy (nginx) for both services

## Support

For issues or questions, refer to:
- `app/python_service/ENHANCED_EXTRACTION_README.md` - PDF extraction details
- Project README.md - General project information

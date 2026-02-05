#!/bin/bash

# Budget Transparency App - Complete Setup Script
# This script sets up both backend and frontend

echo "=========================================="
echo "Budget Transparency App - Setup"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Setup Backend (Python)
echo -e "\n${YELLOW}Step 1: Setting up Python Backend...${NC}"

cd app/python_service

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install pdfplumber pypdf pdf2image groq python-dotenv fastapi uvicorn pydantic requests

echo -e "${GREEN}✅ Backend setup complete!${NC}"

# Step 2: Setup Frontend (Node.js)
echo -e "\n${YELLOW}Step 2: Setting up Frontend...${NC}"

cd ../..

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
else
    echo "Node modules already installed"
fi

echo -e "${GREEN}✅ Frontend setup complete!${NC}"

# Step 3: Check environment variables
echo -e "\n${YELLOW}Step 3: Checking environment variables...${NC}"

if [ ! -f ".env.local" ]; then
    echo -e "${RED}⚠️  .env.local not found!${NC}"
    echo "Creating template .env.local..."
    cat > .env.local << EOF
# Required for GPU Analysis
GROQ_API_KEY=your_groq_api_key_here

# Optional: HuggingFace API (fallback)
HF_API_KEY=your_hf_api_key_here

# Optional: Google Colab OCRFlux instance (recommended)
OCRFLUX_URL=https://your-ngrok-url.ngrok.io
EOF
    echo -e "${YELLOW}⚠️  Please edit .env.local and add your API keys${NC}"
else
    echo -e "${GREEN}✅ .env.local found${NC}"
fi

# Summary
echo -e "\n=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start Backend (Terminal 1):"
echo "   cd app/python_service"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload"
echo ""
echo "2. Start Frontend (Terminal 2):"
echo "   npm run dev"
echo ""
echo "3. Open browser:"
echo "   http://localhost:3000"
echo ""
echo "=========================================="

#!/bin/bash

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_DIR="${PROJECT_ROOT}/src/ui"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo -e "${GREEN}🚀 Tic-Tac-Toe UI Setup & Start${NC}"
echo "================================="

# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Check if npm is installed
if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ npm found: $(npm --version)${NC}"

# Detect and activate Python virtual environment
echo ""
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo -e "${GREEN}✓ Python virtual environment already active${NC}"
    echo -e "  ${VIRTUAL_ENV}"
else
    echo -e "${YELLOW}🐍 Looking for Python virtual environment...${NC}"

    # Check common venv directory names
    VENV_FOUND=""
    for venv_dir in "venv" ".venv" "env"; do
        if [ -d "${PROJECT_ROOT}/${venv_dir}" ] && [ -f "${PROJECT_ROOT}/${venv_dir}/bin/activate" ]; then
            VENV_FOUND="${PROJECT_ROOT}/${venv_dir}"
            break
        fi
    done

    if [ -n "$VENV_FOUND" ]; then
        echo -e "${GREEN}✓ Found virtual environment: ${venv_dir}${NC}"
        echo -e "${YELLOW}  Activating...${NC}"
        source "${VENV_FOUND}/bin/activate"
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}⚠️  No virtual environment found (checked: venv, .venv, env)${NC}"
        echo -e "${YELLOW}  Proceeding with system Python...${NC}"
    fi
fi

# Check if Python/uvicorn is available for backend
echo ""
if ! command -v uvicorn >/dev/null 2>&1 && ! python -m uvicorn --version >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: uvicorn not found${NC}"
    echo "Please install backend dependencies:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

if command -v uvicorn >/dev/null 2>&1; then
    echo -e "${GREEN}✓ uvicorn found: $(uvicorn --version 2>&1 | head -1)${NC}"
else
    echo -e "${GREEN}✓ uvicorn found (via python -m)${NC}"
fi

# Navigate to UI directory
cd "${UI_DIR}"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo ""
    echo -e "${YELLOW}📦 Installing UI dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

# Start backend API in background
echo ""
echo -e "${YELLOW}🔧 Starting backend API on port ${BACKEND_PORT}...${NC}"
cd "${PROJECT_ROOT}"

# Create a temporary file to store backend PID
BACKEND_PID_FILE="/tmp/tictactoe-backend-$$.pid"

if command -v uvicorn >/dev/null 2>&1; then
    uvicorn src.api.main:app --host 0.0.0.0 --port "${BACKEND_PORT}" >/tmp/tictactoe-backend.log 2>&1 &
else
    python -m uvicorn src.api.main:app --host 0.0.0.0 --port "${BACKEND_PORT}" >/tmp/tictactoe-backend.log 2>&1 &
fi

BACKEND_PID=$!
echo $BACKEND_PID > "${BACKEND_PID_FILE}"

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start backend API${NC}"
    echo "Check logs at /tmp/tictactoe-backend.log"
    exit 1
fi

echo -e "${GREEN}✓ Backend API started (PID: ${BACKEND_PID})${NC}"
echo -e "${GREEN}  API URL: http://localhost:${BACKEND_PORT}${NC}"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down...${NC}"

    if [ -f "${BACKEND_PID_FILE}" ]; then
        BACKEND_PID=$(cat "${BACKEND_PID_FILE}")
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "Stopping backend API (PID: ${BACKEND_PID})..."
            kill $BACKEND_PID 2>/dev/null || true
        fi
        rm -f "${BACKEND_PID_FILE}"
    fi

    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Register cleanup function
trap cleanup EXIT INT TERM

# Start frontend
echo ""
echo -e "${YELLOW}🎨 Starting UI development server on port ${FRONTEND_PORT}...${NC}"
cd "${UI_DIR}"

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✨ Everything is ready!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "Backend API:  ${GREEN}http://localhost:${BACKEND_PORT}${NC}"
echo -e "Frontend UI:  ${GREEN}http://localhost:${FRONTEND_PORT}${NC}"
echo ""
echo -e "Backend logs: /tmp/tictactoe-backend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Start Next.js dev server (this runs in foreground)
npm run dev

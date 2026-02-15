#!/usr/bin/env bash
# Complete System Startup Script
# Starts all components in optimized order

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BOLD}${GREEN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Video Generation System - Complete Startup          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
echo -e "${YELLOW}[1/5] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi
python3 --version

# Check Node
echo -e "${YELLOW}[2/5] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found"
    exit 1
fi
node --version

# Install Python dependencies
echo -e "${YELLOW}[3/5] Installing Python dependencies...${NC}"
pip install -q -r requirements.txt 2>/dev/null || pip3 install -q -r requirements.txt

# Install frontend dependencies
if [ ! -d "ui/node_modules" ]; then
    echo -e "${YELLOW}[4/5] Installing frontend dependencies...${NC}"
    cd ui && npm install --silent && cd ..
else
    echo -e "${YELLOW}[4/5] Frontend dependencies already installed${NC}"
fi

# Validation
echo -e "${YELLOW}[5/5] Running validation...${NC}"
python3 validate_system.py

echo -e "${GREEN}${BOLD}"
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ System ready! Start services in separate terminals:║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BOLD}Terminal 1 (Backend):${NC}"
echo "  python run_all_services.py"
echo ""

echo -e "${BOLD}Terminal 2 (Frontend):${NC}"
echo "  cd ui && npm run dev"
echo ""

echo -e "${BOLD}Terminal 3 (Testing):${NC}"
echo "  python test_api_comprehensive.py"
echo ""

echo -e "${GREEN}Frontend URL: ${BOLD}http://localhost:3000${NC}"
echo -e "${GREEN}API URL: ${BOLD}http://localhost:8080${NC}"
echo -e "${GREEN}WebSocket URL: ${BOLD}ws://localhost:8085${NC}"
echo ""

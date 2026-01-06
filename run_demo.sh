#!/bin/bash
# Simple script to setup environment and run demo scripts

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================="
echo -e "Agentic Tic-Tac-Toe - Demo Runner"
echo -e "==================================================${NC}\n"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}\n"

# Check if project is installed
if ! python -c "import src" 2>/dev/null; then
    echo -e "${YELLOW}Project not installed. Installing...${NC}"
    pip install -e . > /dev/null 2>&1
    echo -e "${GREEN}✓ Project installed${NC}\n"
else
    echo -e "${GREEN}✓ Project already installed${NC}\n"
fi

# Show available demos
echo -e "${BLUE}Available demos:${NC}"
echo "  1) Human vs Human (Phase 2 - Game Engine)"
echo "  2) Exit"
echo ""

# Get user choice
read -p "Select demo to run (1-2): " choice

case $choice in
    1)
        echo -e "\n${BLUE}Running Human vs Human demo...${NC}\n"
        python -m scripts.play_human_vs_human
        ;;
    2)
        echo -e "${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Demo completed!${NC}"

#!/bin/bash
# Simple script to setup environment and run demo scripts
#
# Usage:
#   ./run_demo.sh              # Default: Human vs Agent (Phase 3 - Rule-based Agent System)
#   ./run_demo.sh h2agent      # Human vs Agent (Phase 3 - Rule-based Agent System)
#   ./run_demo.sh h2h          # Human vs Human (Phase 2 - Game Engine)
#   ./run_demo.sh api          # Play via REST API (Phase 4 - REST API Layer)
#   ./run_demo.sh interactive  # Interactive menu

set -e  # Exit on error

# Cleanup function for API server
cleanup_server() {
    if [ -n "$SERVER_PID" ] && [ "$SERVER_STARTED_BY_SCRIPT" = true ]; then
        echo -e "\n${BLUE}Cleaning up: Stopping API server (PID: ${SERVER_PID})...${NC}"
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
        echo -e "${GREEN}✓ Server stopped${NC}"
    fi
}

# Set trap to cleanup on exit
trap cleanup_server EXIT INT TERM

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

# Parse command line argument
choice=""
if [ $# -eq 0 ]; then
    # No argument provided - default to Human vs Agent (Phase 3 - Rule-based Agent System)
    choice="phase3"
elif [ $# -eq 1 ]; then
    arg=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    case $arg in
        h2h|humanvshuman|human-vs-human)
            choice="phase2"
            ;;
        h2agent|humanvsagent|human-vs-agent)
            choice="phase3"
            ;;
        api|playviaapi|play-via-api)
            choice="phase4"
            ;;
        interactive|menu|i)
            choice="interactive"
            ;;
        *)
            echo -e "${YELLOW}Invalid argument: $1${NC}"
            echo -e "${BLUE}Usage:${NC}"
            echo "  ./run_demo.sh              # Default: Human vs Agent (Phase 3 - Rule-based Agent System)"
            echo "  ./run_demo.sh h2agent      # Human vs Agent (Phase 3 - Rule-based Agent System)"
            echo "  ./run_demo.sh h2h          # Human vs Human (Phase 2 - Game Engine)"
            echo "  ./run_demo.sh api          # Play via REST API (Phase 4 - REST API Layer)"
            echo "  ./run_demo.sh interactive  # Interactive menu"
            exit 1
            ;;
    esac
else
    echo -e "${YELLOW}Too many arguments. Usage: ./run_demo.sh [h2h|h2agent|api|interactive]${NC}"
    exit 1
fi

# Run selected demo
if [ "$choice" = "interactive" ]; then
    # Interactive mode
    echo -e "${BLUE}Available demos:${NC}"
    echo "  1) Human vs Human (Phase 2 - Game Engine)"
    echo "  2) Human vs Agent (Phase 3 - Rule-based Agent System)"
    echo "  3) Play via REST API (Phase 4 - REST API Layer)"
    echo "  4) Exit"
    echo ""
    read -p "Select demo to run (1-4): " menu_choice

    case $menu_choice in
        1)
            choice="phase2"
            ;;
        2)
            choice="phase3"
            ;;
        3)
            choice="phase4"
            ;;
        4)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
fi

# Execute the selected demo
case $choice in
    phase2)
        echo -e "\n${BLUE}Running: Human vs Human (Phase 2 - Game Engine)${NC}\n"
        python -m scripts.play_human_vs_human
        ;;
    phase3)
        echo -e "\n${BLUE}Running: Human vs Agent (Phase 3 - Rule-based Agent System)${NC}\n"
        python -m scripts.play_human_vs_ai
        ;;
    phase4)
        echo -e "\n${BLUE}Running: Play via REST API (Phase 4 - REST API Layer)${NC}\n"
        
        # Check if server is already running
        API_PORT=8000
        if curl -s "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ API server is already running on port ${API_PORT}${NC}\n"
            SERVER_STARTED_BY_SCRIPT=false
            SERVER_PID=""
        else
            echo -e "${YELLOW}API server is not running. Starting it in the background...${NC}"
            echo -e "${BLUE}Starting server: uvicorn src.api.main:app --host 127.0.0.1 --port ${API_PORT}${NC}"
            
            # Start server in background
            uvicorn src.api.main:app --host 127.0.0.1 --port ${API_PORT} > /dev/null 2>&1 &
            SERVER_PID=$!
            SERVER_STARTED_BY_SCRIPT=true
            
            # Wait for server to be ready (max 10 seconds)
            echo -e "${BLUE}Waiting for server to start...${NC}"
            for i in {1..20}; do
                if curl -s "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
                    echo -e "${GREEN}✓ Server is ready!${NC}\n"
                    break
                fi
                if [ $i -eq 20 ]; then
                    echo -e "${YELLOW}⚠ Server did not start in time. Continuing anyway...${NC}\n"
                else
                    sleep 0.5
                fi
            done
        fi
        
        # Run the demo script
        python -m scripts.play_via_api
        ;;
    *)
        echo -e "${YELLOW}Invalid choice: $choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Demo completed!${NC}"

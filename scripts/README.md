# Demo Scripts

Demonstration scripts showing implemented phase capabilities.

## Run Demo

```bash
# Default: Human vs Agent (Phase 3 - Rule-based Agent System)
./run_demo.sh

# Human vs Agent (Phase 3)
./run_demo.sh h2agent

# Human vs Human (Phase 2)
./run_demo.sh h2h

# Play via REST API (Phase 4)
./run_demo.sh api

# Interactive menu
./run_demo.sh interactive
```

## Available Demos

### Human vs Human Game

Demonstrates Phase 2 (Game Engine):
- Game rules enforcement (win/draw detection)
- Move validation
- State management
- Random valid moves (stateless gameplay)

**Run:** `python scripts/play_human_vs_human.py`

### Human vs Agent Game

Demonstrates Phase 3 (Rule-based Agent System):
- **Note**: This uses rule-based agents (not LLM-based AI). LLM integration comes in Phase 5.
- Agent Pipeline orchestration (Scout → Strategist → Executor)
- Scout Agent: Rule-based board analysis, threat/opportunity detection
- Strategist Agent: Priority-based move selection using rule-based logic
- Executor Agent: Move validation and execution with fallback strategies
- Fallback strategies for timeouts and failures
- Two modes: Interactive (human input) or Simulation (auto)

**Run:** `python scripts/play_human_vs_ai.py`

### Play via REST API

Demonstrates Phase 4 (REST API Layer):
- Complete game via HTTP requests
- All API endpoints (POST /api/game/new, POST /api/game/move, GET /api/game/status)
- Error handling (invalid moves, out of bounds, occupied cells)
- Game board display from API responses
- AI move execution details (position, reasoning, execution time)
- Interactive gameplay with human input

**Note:** The FastAPI server will be automatically started by `run_demo.sh` if it's not already running.
If running the script directly, start the server manually with: `uvicorn src.api.main:app --reload`

**Run:** `./run_demo.sh api` (recommended - automatically starts server if needed) or `python scripts/play_via_api.py`

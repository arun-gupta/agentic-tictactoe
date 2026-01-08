# Demo Scripts

Demonstration scripts showing implemented phase capabilities.

## Run Demo

```bash
./run_demo.sh
```

## Available Demos

### Human vs Human Game

Demonstrates Phase 2 (Game Engine):
- Game rules enforcement (win/draw detection)
- Move validation
- State management
- Random valid moves (stateless gameplay)

**Run:** `python scripts/play_human_vs_human.py`

### Human vs AI Game

Demonstrates Phase 3 (Agent System):
- Agent Pipeline orchestration (Scout → Strategist → Executor)
- Scout Agent: Board analysis, threat/opportunity detection
- Strategist Agent: Priority-based move selection
- Executor Agent: Move validation and execution
- Fallback strategies for timeouts and failures
- Two modes: Interactive (human input) or Simulation (auto)

**Run:** `python scripts/play_human_vs_ai.py`

### Coming Soon

- AI vs AI - Phase 3 (Agent System)

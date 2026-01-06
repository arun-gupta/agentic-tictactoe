# Demo Scripts

This directory contains demonstration scripts showing the capabilities of each implemented phase.

## Available Demos

### Human vs Human Game (`play_human_vs_human.py`)

Demonstrates Phase 2 (Game Engine) capabilities with a simulated human vs human game.

**What it shows:**
- Complete game engine API usage
- Game rules enforcement (win detection, draw detection)
- Move validation
- State management and validation
- All public methods: `make_move()`, `validate_move()`, `check_winner()`, `check_draw()`, `get_available_moves()`, `get_current_state()`, `validate_state()`, `reset_game()`

**How to run:**
```bash
# From project root
python -m scripts.play_human_vs_human
```

**Expected output:**
- Visual board display showing game progression
- Move-by-move validation and execution
- Winner detection
- Complete API capability demonstration

## Future Demos

- `play_human_vs_ai.py` - Coming in Phase 3 (Agent System)
- `play_ai_vs_ai.py` - Coming in Phase 3 (Agent System)

# How to Improve Code Coverage

## Current Status

**Coverage: 14%** (as of current implementation)

### What's Covered
- ✅ `src/domain/models.py` (Position class) - **100% coverage**
  - 11 statements, 0 missed
  - All 13 tests passing

### What's Not Covered (but expected)
- ❌ `src/domain/errors.py` - 0% (17 statements)
  - **Note**: This is just constants/error code definitions, doesn't need tests
- ❌ `src/utils/logging_config.py` - 0% (56 statements, 14 branches)
  - **Note**: Utility code, can be tested later (optional)
- ❌ Many placeholder files (empty `__init__.py`, placeholder modules)
  - These will be covered as implementation progresses

## Strategy to Improve Coverage

### Immediate Next Steps (Continue Phase 1)

Following the implementation plan, continue with domain models:

1. **Task 1.0.2: Board** (Next)
   - Implement `Board` class
   - Add tests (10 acceptance criteria)
   - Expected: +~30-50 statements covered

2. **Task 1.0.3: GameState**
   - Implement `GameState` class
   - Add tests (10 acceptance criteria)
   - Expected: +~40-60 statements covered

3. **Task 1.1: Agent Domain Models** (8 models)
   - Threat, Opportunity, StrategicMove, BoardAnalysis, MovePriority, MoveRecommendation, Strategy, MoveExecution
   - Expected: +~150-200 statements covered

4. **Task 1.2: Result Wrappers**
   - AgentResult
   - Expected: +~30-40 statements covered

**After Phase 1 completion, expected coverage: ~60-70%** (domain layer)

### Long-term Strategy

Continue with the implementation plan phases:

- **Phase 2: Game Engine** → +~20-30% coverage
- **Phase 3: Agent System** → +~10-15% coverage
- **Phase 4: REST API** → +~5-10% coverage
- **Phase 5-10: Remaining features** → Target 80%+ coverage

## Optional: Test Utility Code

If you want to improve coverage sooner (without waiting for full implementation):

### Test `logging_config.py` (Optional)

```python
# tests/unit/utils/test_logging_config.py
def test_setup_logging():
    from src.utils.logging_config import setup_logging
    setup_logging()
    # Verify logging is configured
```

**Note**: This is optional - utility code can be tested later. Focus on domain models first.

## Coverage Goals by Phase

| Phase | Expected Coverage | Notes |
|-------|------------------|-------|
| Phase 0 | 0% | Setup only |
| Phase 1 (Current) | 14% → 60-70% | Domain models |
| Phase 2 | 60-70% → 80-85% | Game engine |
| Phase 3 | 80-85% → 85-90% | Agents |
| Phase 4+ | 85-90% → 90%+ | API, UI, etc. |

## Best Practices

1. **Test-Driven Development**: Write tests first (TDD)
2. **Follow the Plan**: Continue with implementation plan tasks
3. **Acceptance Criteria**: Each test should cover specific acceptance criteria
4. **Don't Worry About Utility Code**: Focus on business logic first
5. **Incremental Progress**: Coverage will increase naturally as you implement features

## Quick Win: Continue Phase 1

**Next Task: 1.0.2 - Board**

This will immediately increase coverage by implementing:
- Board class (~30-50 statements)
- 10 test cases
- Expected coverage increase: +5-10%

Just continue with the implementation plan - coverage will improve naturally! 🚀

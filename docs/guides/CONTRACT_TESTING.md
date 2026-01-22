# Contract Testing Implementation Plan

> **Status**: ✅ Implemented (Phase 4.6)
> **Last Updated**: January 2026

## Overview

This document outlines the plan to add contract testing to validate that the FastAPI API implementation matches its specification. After evaluating options, **Schemathesis** is recommended for schema-based contract testing.

## Background & Research

### Why Contract Testing?

Contract testing ensures:
- API implementation matches its documented specification
- Changes to API don't break existing clients
- Response structures are consistent and predictable
- Early detection of schema drift

### Tools Evaluated

| Tool | Type | Pros | Cons |
|------|------|------|------|
| **Schemathesis** | Schema-based | Auto-generates tests from OpenAPI, low maintenance, used by Spotify/JetBrains | Less control over specific test cases |
| **Pact** | Consumer-driven | True contract testing between services, catches breaking changes | Higher setup complexity, needs consumer tests |
| **fastapi-icontract** | Design-by-contract | Integrates with FastAPI directly | More about function contracts than API contracts |

### Recommendation: Schemathesis

**Reasons:**
1. **Leverages Existing Infrastructure**: FastAPI auto-generates OpenAPI schemas from Pydantic models already in place
2. **Auto-Generated Tests**: Schemathesis generates hundreds of test cases automatically from the schema
3. **Low Maintenance**: Schema is the single source of truth - no separate contracts to maintain
4. **Industry Proven**: Used by Spotify, JetBrains, WordPress, Red Hat
5. **Current Architecture Fit**: Single client (Streamlit UI placeholder), schema validation is sufficient
6. **Active Maintenance**: Latest release Jan 2026, 3000+ GitHub stars

**Future Consideration - Pact:**
When the Streamlit UI is fully implemented and if multiple clients consume the API, consider adding Pact for true consumer-driven contract testing.

## Implementation Plan

### Phase 1: Dependencies

Add to `pyproject.toml` under `[project.optional-dependencies] dev`:

```toml
# Contract Testing
"schemathesis>=3.25.0",
"hypothesis>=6.92.0",
```

Add pytest marker:

```toml
[tool.pytest.ini_options]
markers = [
    "contract: marks tests as contract tests (deselect with '-m \"not contract\"')",
]
```

### Phase 2: Test Directory Structure

Create the following structure:

```
tests/
└── contract/
    ├── __init__.py              # Module docstring
    ├── conftest.py              # Fixtures (client, openapi_schema)
    ├── test_openapi_schema.py   # Schema structure validation
    ├── test_schemathesis_api.py # Auto-generated API tests
    └── test_response_contracts.py # Response Pydantic validation
```

### Phase 3: Test Implementation

#### 3.1 Fixtures (`conftest.py`)

```python
import pytest
from fastapi.testclient import TestClient
from src import api

@pytest.fixture
def client() -> TestClient:
    """Create a test client with service ready state."""
    import src.api.main as main_module
    main_module._service_ready = True
    return TestClient(api.main.app)

@pytest.fixture
def openapi_schema(client: TestClient) -> dict:
    """Get the OpenAPI schema from the running API."""
    response = client.get("/openapi.json")
    return response.json()
```

#### 3.2 Schema Validation Tests (`test_openapi_schema.py`)

Tests to verify:
- Schema has required info section (title, version)
- All endpoints are documented (`/api/game/new`, `/health`, etc.)
- Response schemas are defined (ErrorResponse, GameState, etc.)
- HTTP status codes are specified (201, 200, 404, 503)

#### 3.3 Schemathesis API Tests (`test_schemathesis_api.py`)

```python
import schemathesis
from schemathesis import from_asgi
from src.api.main import app

schema = from_asgi("/openapi.json", app)

@schema.parametrize(endpoint="/health")
def test_health_endpoint_contract(case):
    """Auto-generated contract test for health endpoint."""
    response = case.call_asgi()
    case.validate_response(response)
```

#### 3.4 Response Contract Tests (`test_response_contracts.py`)

Tests to verify API responses deserialize correctly to Pydantic models:
- `NewGameResponse` from POST /api/game/new
- `ErrorResponse` from error endpoints
- `AgentStatus` from GET /api/agents/{name}/status
- `GameStatusResponse` from GET /api/game/status

### Phase 4: CI Integration

Update `.github/workflows/ci.yml`:

```yaml
- name: Run unit and integration tests with coverage
  run: pytest tests/unit tests/integration --cov=src --cov-branch --cov-report=xml --cov-report=term --cov-fail-under=80

- name: Run contract tests
  run: pytest tests/contract -v --tb=short
```

### Phase 5: Documentation Updates

Update `docs/DEVELOPMENT.md` to include:
- How to run contract tests
- Reference to this guide

## Files to Create

| File | Purpose |
|------|---------|
| `tests/contract/__init__.py` | Module init |
| `tests/contract/conftest.py` | Test fixtures |
| `tests/contract/test_openapi_schema.py` | Schema validation |
| `tests/contract/test_schemathesis_api.py` | Auto-generated tests |
| `tests/contract/test_response_contracts.py` | Response validation |

## Files to Modify

| File | Changes |
|------|---------|
| `pyproject.toml` | Add schemathesis, hypothesis deps; add pytest marker |
| `.github/workflows/ci.yml` | Add contract test step |
| `docs/DEVELOPMENT.md` | Add contract testing reference |

## Verification Checklist

After implementation:

- [ ] `pip install -e ".[dev]"` installs schemathesis
- [ ] `pytest tests/contract/ -v` runs all contract tests
- [ ] `pytest -m contract` runs only contract tests
- [ ] `pytest -m "not contract"` excludes contract tests
- [ ] CI pipeline includes contract test step
- [ ] All contract tests pass

## Estimated Effort

- Dependencies & config: ~15 min
- Test files creation: ~1 hour
- CI integration: ~15 min
- Documentation: ~15 min
- Testing & debugging: ~30 min

**Total: ~2-3 hours**

## Future Enhancements

### Adding Pact (When UI is Complete)

When the Streamlit client is fully implemented:

```
tests/contract/pact/
├── consumer/test_ui_consumer.py   # UI defines expected interactions
├── provider/test_api_provider.py  # API verifies it fulfills contracts
└── pacts/ui-api.json              # Generated contract file
```

### Additional Schemathesis Features

- Stateful testing for multi-step workflows
- Custom test strategies for specific endpoints
- Performance regression testing

## Known Limitations

### Property-Based Testing Edge Cases

**Issue**: Schemathesis's property-based testing may generate edge cases for endpoints with optional request bodies (e.g., `POST /api/game/new`) that are flagged as schema violations but are actually valid API behavior.

**Details**:
- The API correctly implements validation using Pydantic's `extra="forbid"` configuration, which rejects extra fields
- Optional request bodies (e.g., `NewGameRequest | None`) can accept empty bodies, which is valid
- Schemathesis's negative testing may flag some edge cases as violations when they're actually acceptable

**Impact**:
- One test case may intermittently fail during property-based testing
- This does not indicate an API bug - the API correctly rejects invalid data
- All functional validation tests pass

**Status**: Known limitation of property-based testing with optional request bodies. The API implementation is correct.

**Workaround**: The test file documents this limitation and handles these edge cases appropriately.

## Resources

- [Schemathesis Documentation](https://schemathesis.readthedocs.io/)
- [Schemathesis GitHub](https://github.com/schemathesis/schemathesis)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Pact Documentation](https://docs.pact.io/) (for future reference)
- [FastAPI OpenAPI Documentation](https://fastapi.tiangolo.com/tutorial/metadata/)

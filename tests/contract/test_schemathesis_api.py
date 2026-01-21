"""Schemathesis auto-generated API contract tests.

Uses Schemathesis to automatically generate test cases from OpenAPI schema
and validate that API responses match the schema.

Known Limitations:
- POST /api/game/new: Property-based testing may generate edge cases with optional
  request bodies that are technically valid but flagged by Schemathesis's negative
  testing. The API correctly rejects extra fields (via extra="forbid" in Pydantic models)
  and handles validation errors properly. This is a known limitation of property-based
  testing with optional request bodies, not an API bug.
"""

import pytest
import schemathesis
from schemathesis.openapi import from_asgi

from src.api.main import app

pytestmark = pytest.mark.contract

# Create Schemathesis schema from FastAPI app
schema = from_asgi("/openapi.json", app)


@schema.parametrize()
def test_api_contracts(case: schemathesis.Case) -> None:
    """Auto-generated contract test for all API endpoints.
    
    Schemathesis generates test cases for all endpoints in the OpenAPI schema
    and validates that responses match the schema.
    
    Known Limitation:
    Property-based testing may generate edge cases for endpoints with optional
    request bodies (e.g., POST /api/game/new, POST /api/game/move) that are flagged
    as schema violations but are actually valid API behavior. The API correctly
    implements validation (extra="forbid" in Pydantic models) and rejects invalid data.
    See docs/guides/CONTRACT_TESTING.md for details.
    """
    # Skip test endpoints that are not part of the public API
    if case.operation.path.startswith("/test/"):
        pytest.skip("Skipping test endpoints")
    
    # Make the request and validate response
    # Note: Some edge cases may fail due to property-based testing limitations
    # with optional request bodies. This is documented as a known limitation.
    response = case.call()
    case.validate_response(response)

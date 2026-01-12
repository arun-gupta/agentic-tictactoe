# Agentic Tic-Tac-Toe

[![CI](https://github.com/arun-gupta/agentic-tictactoe/actions/workflows/ci.yml/badge.svg)](https://github.com/arun-gupta/agentic-tictactoe/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/arun-gupta/agentic-tictactoe/branch/main/graph/badge.svg)](https://codecov.io/gh/arun-gupta/agentic-tictactoe)

A multi-agent AI system for playing Tic-Tac-Toe, featuring specialized agents (Scout, Strategist, Executor) that collaborate to make optimal moves. Includes LLM provider abstraction, experimentation tracking for A/B testing different AI models, and comprehensive game state management.

## Planned Features

> **Note**: Implementation is in progress. Phases 0-4 are complete (Domain Models, Game Engine, Agent System, REST API). Features below include both implemented and planned components.

- **Multi-Agent Architecture**: Three specialized agents (Scout, Strategist, Executor) working in coordination
- **LLM Integration**: Support for OpenAI, Anthropic, and Google Gemini models with provider abstraction
- **API-First Design**: RESTful API with comprehensive error handling and status codes
- **Comprehensive Testing**: 399+ acceptance criteria with full test coverage traceability
- **Observability**: Structured logging, metrics collection, and health checks
- **Deployment Ready**: Docker containerization and Kubernetes Helm charts
- **Design System**: Complete UI specification with Figma integration

## Planned Architecture

The system is designed to follow a layered architecture:

- **Domain Layer**: Core game models and business logic
- **Agent Layer**: AI agents (Scout, Strategist, Executor) with rule-based and LLM-enhanced intelligence
- **API Layer**: FastAPI REST endpoints for game control and state access
- **UI Layer**: Web-based interface (Streamlit) for playing the game
- **Infrastructure Layer**: Configuration, logging, metrics, and deployment

## Documentation

### Core Documentation

- [Full Specification](docs/spec/spec.md) - Complete system architecture and design (4000+ lines)
- [JSON Schemas](docs/spec/schemas.md) - Formal schema definitions for all domain models
- [UI Specification](docs/spec/ui-spec.md) - User interface requirements and design with Figma integration
- [Implementation Plan](docs/implementation-plan.md) - 10-phase implementation guide with test coverage

### UI Design

- [UI Preview](docs/spec/ui/preview/game-board-preview.html) - Interactive design preview
- [Figma Frames](docs/spec/ui/frames/) - Design assets exported from Figma

### Analysis & Planning

- [Test Coverage Analysis](docs/analysis/test-coverage-analysis.md) - Test coverage and spec traceability analysis across all phases

## Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **Data Validation**: Pydantic v2
- **UI Framework**: Streamlit
- **LLM Integration**: Pydantic AI (OpenAI, Anthropic, Google Gemini SDKs)
- **Testing**: pytest, pytest-cov, pytest-asyncio, mypy
- **Code Quality**: black, ruff, pre-commit hooks
- **Coverage**: Codecov
- **API Documentation**: OpenAPI/Swagger (built into FastAPI)
- **Persistence**: JSON file-based storage
- **Deployment**: Docker, Kubernetes Helm charts, GitHub Actions CI/CD

## Project Status

**Current Phase**: Implementation - Phase 5 (LLM Integration) 🚧

### Completed
- ✅ **Phase 0**: Project Setup and Foundation
- ✅ **Phase 1**: Domain Models (Foundation Layer)
- ✅ **Phase 2**: Game Engine (Business Logic Layer)
- ✅ **Phase 3**: Agent System (AI Layer) - Scout, Strategist, Executor, and Pipeline
- ✅ **Phase 4**: REST API Layer - All endpoints, error handling, and API demo script

### Current Metrics
- **412 tests passing**
- **Complete REST API** with all endpoints (game control, agent status, error handling)
- **Test coverage**: See badge above for current Codecov coverage
  - Codecov excludes unimplemented placeholder files for agents, API, and UI layers
  - 100% coverage on all implemented code (domain models, game engine, agents, API)
- **100% type checking** (mypy strict mode)

### Next Steps
- Phase 5: LLM Integration (LLM provider abstraction and agent enhancement)
- Phase 6: Web UI Layer

See the [Implementation Plan](docs/implementation-plan.md) for full details on all phases and estimated timeline.

## Getting Started

### Quick Demo

```bash
./run_demo.sh
```

### Development Setup

See [Development Guide](docs/DEVELOPMENT.md) for setup instructions and development workflow.

See [Documentation](#documentation) for specifications and implementation details.

## Contributing

This project follows a specification-driven development approach. All changes should align with the documented specification and implementation plan.

## License

See [LICENSE](LICENSE) file for details.

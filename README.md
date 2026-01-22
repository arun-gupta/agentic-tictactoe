# Agentic Tic-Tac-Toe

[![CI](https://github.com/arun-gupta/agentic-tictactoe/actions/workflows/ci.yml/badge.svg)](https://github.com/arun-gupta/agentic-tictactoe/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/arun-gupta/agentic-tictactoe/branch/main/graph/badge.svg)](https://codecov.io/gh/arun-gupta/agentic-tictactoe)

A multi-agent AI system for playing Tic-Tac-Toe, featuring specialized agents (Scout, Strategist, Executor) that collaborate to make optimal moves. Includes LLM provider abstraction, experimentation tracking for A/B testing different AI models, and comprehensive game state management.

## Getting Started

### Quick Demo

```bash
./run_demo.sh
```

### Development Setup

See [Development Guide](docs/DEVELOPMENT.md) for setup instructions and development workflow.

## Project Status

**Current Phase**: Phase 4 Complete ✅ | Next: Phase 5 (LLM Integration) ⏸️

> **Note**: Phases 0-4 are complete (Domain Models, Game Engine, Agent System, REST API). Features listed below include both implemented and planned components.

### Completed (Phases 0-4)
- ✅ **Phase 0**: Project Setup and Foundation
- ✅ **Phase 1**: Domain Models (Foundation Layer)
- ✅ **Phase 2**: Game Engine (Business Logic Layer)
- ✅ **Phase 3**: Agent System (AI Layer) - Scout, Strategist, Executor, and Pipeline
- ✅ **Phase 4**: REST API Layer - All endpoints, error handling, API demo script, and contract testing (Phase 4.6)

### Current Metrics
- **429 tests passing** (unit, integration, contract tests)
- **Complete REST API** with all endpoints (game control, agent status, error handling)
- **Contract Testing**: 16/18 contract tests passing (validates API matches OpenAPI specification; known limitation documented)
- **Test coverage**: See badge above for current Codecov coverage
  - Codecov excludes unimplemented placeholder files for agents, API, and UI layers
  - 100% coverage on all implemented code (domain models, game engine, agents, API)
- **100% type checking** (mypy strict mode)

### Remaining Phases (5-11)
- ⏸️ **Phase 5**: LLM Integration - LLM provider abstraction (OpenAI, Anthropic, Google Gemini) and agent enhancement
- ⏸️ **Phase 6**: Cloud Native Deployment - Docker containerization and Kubernetes deployment
- ⏸️ **Phase 7**: MCP Distributed Mode - Distributed agent coordination using Model Context Protocol
- ⏸️ **Phase 8**: Web UI Layer - Interactive web interface for playing the game
- ⏸️ **Phase 9**: Testing and Quality Assurance - System-level testing, performance validation, and resilience testing (complements TDD from previous phases)
- ⏸️ **Phase 10**: Configuration and Observability - Production-ready logging, metrics, and configuration
- ⏸️ **Phase 11**: Documentation - Complete user and developer documentation

See the [Implementation Plan](docs/implementation-plan.md) for full details on all phases and estimated timeline.

## Features

- **Multi-Agent Architecture**: Three specialized agents (Scout, Strategist, Executor) working in coordination
- **LLM Integration**: Support for OpenAI, Anthropic, and Google Gemini models with provider abstraction
- **API-First Design**: RESTful API with comprehensive error handling and status codes
- **Comprehensive Testing**: 412 tests with full test coverage traceability
- **Observability**: Structured logging, metrics collection, and health checks
- **Deployment Ready**: Docker containerization and Kubernetes Helm charts
- **Design System**: Complete UI specification with Figma integration

## Architecture

The system follows a layered architecture:

- **Domain Layer**: Core game models and business logic
- **Agent Layer**: AI agents (Scout, Strategist, Executor) with rule-based and LLM-enhanced intelligence
- **API Layer**: FastAPI REST endpoints for game control and state access
- **UI Layer**: Web-based interface (Streamlit) for playing the game
- **Infrastructure Layer**: Configuration, logging, metrics, and deployment

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

## Documentation

### Core Documentation

- [Development Guide](docs/DEVELOPMENT.md) - Development setup and workflow
- [Full Specification](docs/spec/spec.md) - Complete system architecture and design (4000+ lines)
- [JSON Schemas](docs/spec/schemas.md) - Formal schema definitions for all domain models
- [UI Specification](docs/spec/ui-spec.md) - User interface requirements and design with Figma integration
- [Implementation Plan](docs/implementation-plan.md) - 12-phase implementation guide with test coverage

### UI Design

- [UI Preview](docs/spec/ui/preview/game-board-preview.html) - Interactive design preview
- [Figma Frames](docs/spec/ui/frames/) - Design assets exported from Figma

### Analysis & Planning

- [Test Coverage Analysis](docs/analysis/test-coverage-analysis.md) - Test coverage and spec traceability analysis across all phases

## Contributing

This project follows a specification-driven development approach. All changes should align with the documented specification and implementation plan.

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Collaboration guidelines
- Branching strategy
- Pull request process
- Code review workflow
- Coordination with other developers

## License

See [LICENSE](LICENSE) file for details.

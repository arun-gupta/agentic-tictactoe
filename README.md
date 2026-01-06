# Agentic Tic-Tac-Toe

[![codecov](https://codecov.io/gh/arun-gupta/agentic-tictactoe/branch/main/graph/badge.svg)](https://codecov.io/gh/arun-gupta/agentic-tictactoe)

A multi-agent AI system for playing Tic-Tac-Toe, featuring specialized agents (Scout, Strategist, Executor) that collaborate to make optimal moves. Includes LLM provider abstraction, experimentation tracking for A/B testing different AI models, and comprehensive game state management.

## Planned Features

> **Note**: This project is currently in the specification and planning phase. The features below are designed and specified but not yet implemented.

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
- **LLM Integration**: LiteLLM (OpenAI, Anthropic, Google Gemini SDKs)
- **Testing**: pytest, pytest-cov, pytest-asyncio, mypy
- **Code Quality**: black, ruff, pre-commit hooks
- **Coverage**: Codecov
- **API Documentation**: OpenAPI/Swagger (built into FastAPI)
- **Persistence**: JSON file-based storage
- **Deployment**: Docker, Kubernetes Helm charts, GitHub Actions CI/CD

## Project Status

**Current Phase**: Specification & Planning ✅

- ✅ Complete specification (spec.md, schemas.md, ui-spec.md)
- ✅ Implementation plan with 10 phases
- ✅ Test coverage documentation for all phases
- ✅ Design system with Figma integration
- ⏸️ Implementation (not started)

**Next Steps**: Implementation will begin with Phase 0 (Project Setup) as outlined in the [Implementation Plan](docs/implementation-plan.md). Estimated timeline: 6-8 weeks for full implementation.

## Getting Started

Since the project is currently in the specification and planning phase:

1. **Start with the Documentation**: Review the [Documentation](#documentation) section below for all available resources
2. **Understand the System**: Read the [Full Specification](docs/spec/spec.md) to understand requirements and architecture
3. **Follow the Plan**: Study the [Implementation Plan](docs/implementation-plan.md) to understand the phased approach
4. **Review Current Status**: Check the [Project Status](#project-status) section for what's been completed

When implementation begins, setup and installation instructions will be added here.

## Contributing

This project follows a specification-driven development approach. All changes should align with the documented specification and implementation plan.

## License

See [LICENSE](LICENSE) file for details.

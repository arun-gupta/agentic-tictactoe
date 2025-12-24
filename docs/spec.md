# Tic-Tac-Toe Multi-Agent Game Specification

## 1. System Overview

### Purpose
A Tic-Tac-Toe game between a human player and an AI opponent. The AI uses three specialized agents (Scout, Strategist, Executor) to make moves. Players interact via a Streamlit UI, and the system supports both local execution and distributed MCP-based coordination.

### Design Principles

**Architectural Foundations:**
- **Domain-Driven Design**: Clear domain models separate from infrastructure
- **Separation of Concerns**: Game logic, agent logic, and UI are independent
- **Clean Interfaces**: Agents communicate via domain models, not dictionaries
- **Protocol Abstraction**: MCP is a transport layer, not the API design

**Implementation Standards:**
- **Type Safety**: Pydantic models throughout for validation and IDE support
- **Statelessness**: Agents are stateless; all context comes from inputs, enabling horizontal scaling
- **DRY (Don't Repeat Yourself)**: Avoid code duplication through shared utilities, base classes, and reusable components
- **Convention over Configuration (CoC)**: Sensible defaults reduce configuration burden while allowing overrides when needed

**Flexibility & Runtime Adaptability:**
- **Configuration over Code**: Behavior controlled through config files, environment variables, and command-line arguments
- **Hot-swappability**: LLM providers and models can be changed via configuration without code changes
- **Mode Interchangeability**: Agents can switch between local (LangChain) and distributed (MCP) modes at runtime
- **Extensibility**: Well-defined interfaces allow adding new agents or features without modifying existing code

**Operational Resilience:**
- **Graceful Degradation**: System continues operating with fallback strategies when agents or LLMs fail
- **Observability**: Built-in metrics, logging, and monitoring for agents, games, and system performance

---

## 2. Domain Model Design

### Core Game Entities

**Position**: Represents a board cell with row and column (0-2). Immutable and hashable.

**Board**: A 3x3 grid of symbols (X, O, or empty). Provides methods to get/set cells, check emptiness, and list empty positions. Validates size.

**Game State**: Complete game state including:
- Current board
- Current player (player or AI)
- Move number
- Player and AI symbols
- Game over status
- Winner (if any)
- Draw status

Includes helper methods to get the current player's symbol and the opponent.

### Agent Domain Models

**Threat**: Represents an immediate threat where the opponent can win. Includes position, line type (row/column/diagonal), line index, and severity (always critical for Tic-Tac-Toe).

**Opportunity**: Represents a winning opportunity. Includes position, line type, line index, and confidence (0.0 to 1.0).

**Strategic Move**: A strategic position recommendation with position, move type (center/corner/edge/fork/block_fork), priority (1-10), and reasoning.

**Board Analysis**: Scout agent output containing:
- List of threats
- List of opportunities
- List of strategic moves
- Human-readable analysis
- Game phase (opening/midgame/endgame)
- Board evaluation score (-1.0 to 1.0)

**Move Recommendation**: Strategist output with position, priority (BLOCK/WIN/STRATEGIC), confidence, reasoning, and expected outcome.

**Strategy**: Strategist output containing:
- Primary move recommendation
- Alternative move recommendations
- Overall game plan
- Risk assessment (low/medium/high)

**Move Execution**: Executor output with position, success status, validation errors, execution time, reasoning, and actual priority used.

### Result Wrappers

**Agent Result**: Generic wrapper for agent outputs containing:
- Domain data (typed)
- Success/failure status
- Error message (if failed)
- Execution time in milliseconds
- Timestamp
- Optional metadata dictionary

Provides factory methods for success and error results.

---

## 3. Agent Architecture

### Agent Responsibilities

**Scout Agent**: Analyzes the board to identify:
- Immediate threats (opponent can win)
- Winning opportunities (we can win)
- Strategic positions (center, corners, edges)
- Game phase assessment
- Board evaluation score

Uses a fast path for rule-based checks (immediate wins/blocks) and falls back to LLM analysis for strategic decisions.

**Strategist Agent**: Synthesizes Scout analysis into a strategy:
- Prioritizes moves (BLOCK > WIN > STRATEGIC)
- Recommends primary move with alternatives
- Provides game plan and risk assessment
- Considers long-term position

**Executor Agent**: Executes the recommended move:
- Validates move (bounds, empty cell, rules)
- Executes if valid
- Provides alternative if invalid
- Returns execution result with timing

### Agent Interface Contract

All agents implement a protocol with a single primary method:
- Scout: analyze method takes GameState, returns AgentResult containing BoardAnalysis
- Strategist: plan method takes GameState and BoardAnalysis, returns AgentResult containing Strategy
- Executor: execute method takes GameState and Strategy, returns AgentResult containing MoveExecution

Agents are stateless; all context comes from inputs. Results include execution metadata (timing, success/failure).

### Agent Pipeline Flow

The coordinator orchestrates a sequential pipeline:
1. Convert current game state to GameState domain model
2. Call Scout.analyze with GameState
3. If Scout succeeds, call Strategist.plan with GameState and Scout's BoardAnalysis
4. If Strategist succeeds, call Executor.execute with GameState and Strategist's Strategy
5. Extract position from Executor's MoveExecution
6. Apply move to game engine
7. Return result or fallback on any failure

Each step validates the previous result before proceeding.

---

## 4. Game Engine Design

### Core Responsibilities

**Game Rules Enforcement**: Validates moves (bounds, empty cell), checks for wins (rows, columns, diagonals), detects draws, manages turn order.

**State Management**: Maintains board state, tracks move history, manages player turns, updates game over status.

**Move Application**: Applies validated moves, updates board, switches players, increments move counter, checks for game end.

### Game Engine Interface

The engine exposes methods to:
- Make a move (position and player) - returns success/failure
- Check for winner - returns player or None
- Check for draw - returns boolean
- Get available moves - returns list of positions
- Reset game - clears state
- Get current state - returns GameState domain model

The engine is stateless regarding agent coordination; it only manages game rules and state.

---

## 5. API Design

### REST API Endpoints

**Game Management**:
- POST /api/game/move - Make a player move (row, col), returns MoveResponse with game state and AI move
- GET /api/game/status - Get current game status including game state, agent status, and metrics
- POST /api/game/reset - Reset game to initial state
- GET /api/game/history - Get move history

**Agent Status**:
- GET /api/agents/scout/status - Get Scout agent status and metrics
- GET /api/agents/strategist/status - Get Strategist agent status and metrics
- GET /api/agents/executor/status - Get Executor agent status and metrics

**MCP Protocol** (optional, for distributed mode):
- POST /mcp/{agent_id}/tools/list - List available tools for agent
- POST /mcp/{agent_id}/tools/call - Call a tool on an agent
- GET /mcp/{agent_id}/resources/{resource_id} - Get agent resource

**Configuration** (optional, for programmatic model management):
- GET /api/config/models - Get current LLM model configuration (provider, model name, parameters)
- GET /api/config/models/available - List available models per provider
- POST /api/config/models - Update LLM model configuration (requires game reset to take effect)

**Note**: Model configuration is primarily managed through the Streamlit UI Configuration Panel, config files, environment variables, or command-line arguments. Configuration API endpoints are optional and primarily useful for programmatic control, external system integration, or observability. Changing models via API should require a game reset to ensure consistency, as model changes affect agent behavior mid-game.

### Request/Response Models

**MoveRequest**: Contains row and column integers (0-2).

**MoveResponse**: Contains success status, position (if successful), updated GameState, AI move execution details (if AI moved), and error message (if failed).

**GameStatusResponse**: Contains current GameState, agent status dictionary, and metrics dictionary.

All API responses use Pydantic models for validation and serialization.

---

## 6. Streamlit UI Requirements

### Main Panel (Active During Game)

The main panel displays the game interface and is visible throughout gameplay:

**Game Board Display**: Visual 3x3 grid showing X, O, and empty cells. Clickable cells for player moves. Highlights last move. Shows current player turn. Displays move history directly on the board game interface, showing a chronological list of moves with player/AI indicator, move number, position, and timestamp. Move history entries include expandable details showing agent reasoning.

**Agent Insights Panel**: Real-time display of:
- Scout analysis (threats, opportunities, strategic moves)
- Strategist strategy (recommended move, reasoning, priority)
- Executor execution (validation, success status, timing)

**Game Status Display**: Shows current player, move number, game over status, winner (if any), and draw status.

### Metrics Panel (Available After Game Completion)

The Metrics panel becomes available and displayed after the game is completed (win, loss, or draw). It provides detailed insights into the agent coordination and LLM interactions:

**Coordinator-Agent Communication**: JSON payloads showing:
- Coordinator requests to each agent (Scout, Strategist, Executor)
- Agent responses and results
- Input/output data structures for each agent call
- Request/response flow through the agent pipeline

**Backend LLM Interactions**: 
- LLM API calls made by each agent
- Request prompts sent to LLM
- LLM responses received
- Token usage per LLM call
- Response times for each LLM interaction
- Model/provider information for each call

**Agent Switch Information**:
- Agent mode used (LangChain local or LangChain+MCP distributed)
- Agent initialization details
- Agent configuration settings
- Mode switching events (if any occurred during the game)

**Performance Summary**:
- Per-agent execution times (min, max, average)
- Total LLM calls per agent
- Total token usage
- Success/failure rates
- Error details (if any)

**Game Metrics**:
- Total moves
- Game duration
- Win/loss/draw outcome
- Average move time

### Configuration Panel

**Model Selection**: Dropdown to select LLM provider (OpenAI, Anthropic, Google Gemini, Ollama) and model name.

**Agent Mode Selection**: Toggle between LangChain mode (local, fast) and LangChain+MCP mode (distributed, protocol-based).

**Game Settings**: Option to reset game, change player symbol, adjust difficulty (if implemented).

### Real-time Updates

UI updates automatically when:
- Player makes a move
- AI makes a move
- Game state changes
- Agent metrics update

Uses Streamlit's session state to manage game state and prevent unnecessary reruns.

---

## 7. Project Structure

### Directory Organization

**schemas/**: Domain models as Pydantic classes:
- game.py: Core game models (Position, Board, GameState)
- analysis.py: Scout agent models (Threat, Opportunity, StrategicMove, BoardAnalysis)
- strategy.py: Strategist agent models (MoveRecommendation, Strategy)
- execution.py: Executor agent models (ValidationError, MoveExecution)
- results.py: Result wrapper models (AgentResult)
- api.py: API request/response models

**agents/**: Agent implementations:
- interfaces.py: Abstract base classes and protocols
- scout_langchain.py: LangChain Scout implementation
- strategist_langchain.py: LangChain Strategist implementation
- executor_langchain.py: LangChain Executor implementation
- scout_langchain_mcp.py: Scout with MCP protocol support
- strategist_langchain_mcp.py: Strategist with MCP protocol support
- executor_langchain_mcp.py: Executor with MCP protocol support
- base_mcp_agent.py: Base class for MCP protocol support

**game/**: Game logic:
- engine.py: Core game rules and state management
- coordinator.py: Orchestrates agent pipeline
- state.py: Game state management (if separate from engine)

**api/**: FastAPI application:
- main.py: FastAPI app setup and routes
- routes/game.py: Game management endpoints
- routes/agents.py: Agent status endpoints
- routes/mcp.py: MCP protocol endpoints (optional)

**ui/**: Streamlit application:
- streamlit_app.py: Main Streamlit app
- components/board.py: Game board component
- components/metrics.py: Metrics dashboard component
- components/insights.py: Agent insights component

**models/**: LLM management:
- shared_llm.py: Shared LLM connection manager
- factory.py: LLM factory for different providers

**utils/**: Utilities:
- config.py: Configuration management
- validators.py: Validation helpers

**tests/**: Test suite:
- test_game_engine.py: Game logic tests
- test_agents.py: Agent tests
- test_api.py: API endpoint tests
- test_integration.py: End-to-end tests

**docs/**: Documentation:
- ARCHITECTURE.md: System architecture
- API.md: API documentation
- USER_GUIDE.md: User guide
- spec.md: This specification document

**config/**: Configuration files:
- config.json: Main configuration
- .env.example: Environment variables template

---

## 8. Dependencies and Requirements

### Core Dependencies

**FastAPI**: Web framework for REST API. Includes uvicorn for ASGI server.

**Pydantic**: Data validation and settings management. Version 2.x for modern features.

**LangChain**: Framework for LLM applications. Includes langchain-openai, langchain-anthropic, langchain-community for provider support.

**Streamlit**: Web framework for UI. Includes streamlit-agraph for visualizations.

**MCP SDK**: Multi-Context Protocol SDK for distributed agent communication (optional, for MCP mode).

### Supporting Libraries

**python-dotenv**: Environment variable management.

**requests**: HTTP client for API calls.

**psutil**: System and process utilities for metrics.

**pandas**: Data manipulation for metrics dashboard.

### Development Dependencies

**pytest**: Testing framework.

**pytest-asyncio**: Async test support.

**black**: Code formatter.

**mypy**: Type checking.

**ruff**: Linting.

### Virtual Environment Setup

**Python Version**: Python 3.11 or higher.

**Virtual Environment**: Use venv module. Create in project root as `venv/` directory.

**Activation**: Source `venv/bin/activate` on Unix/Mac, `venv\Scripts\activate` on Windows.

**Installation**: Install from requirements.txt using pip. Separate requirements_streamlit.txt for Streamlit-specific dependencies if needed.

**Environment Variables**: Load from `.env` file in project root. Include API keys for OpenAI, Anthropic, Google Gemini, and Ollama configuration.

---

## 9. Configuration Management

### Configuration Structure

**Agent Framework Configuration**: Mode selection (langchain or langchain_mcp), model selection per agent or shared, timeout settings, retry logic.

**LLM Provider Configuration**: Provider selection (OpenAI, Anthropic, Google Gemini, Ollama), API keys (from environment), model names, temperature and other parameters, token limits. Default models: OpenAI uses GPT-5 mini (fallback: GPT-4.1), Anthropic uses Claude Opus 4.5, Google Gemini uses Gemini 3 Flash (fallback: Gemini 2.5 Flash).

**Game Configuration**: Default player symbol, AI symbol, game rules (if configurable), move timeout.

**MCP Configuration** (if using MCP mode): Port assignments per agent, server URLs for distributed mode, protocol settings, transport type (stdio, HTTP, SSE).

**UI Configuration**: Streamlit theme, refresh intervals, metrics display preferences, debug mode.

### Configuration Sources

**config.json**: Main configuration file with default settings.

**.env file**: Environment-specific settings (API keys, secrets, local paths).

**Environment Variables**: Override config.json values. Prefixed with project name to avoid conflicts.

**Command-line Arguments**: Override for quick testing (model selection, mode selection).

Configuration is loaded in priority order: defaults in code, config.json, .env file, environment variables, command-line arguments.

---

## 10. Deployment Considerations

### Local Development

**Single Process**: All components (API, agents, UI) run in one process. FastAPI and Streamlit can run in same process or separate processes on different ports.

**Development Server**: Use uvicorn reload mode for API, Streamlit auto-reload for UI.

**Debug Mode**: Enable verbose logging, detailed error messages, agent reasoning display.

### Production Deployment

**Separate Services**: API server, Streamlit UI, and agent services (if distributed) as separate processes or containers.

**Process Management**: Use systemd, supervisor, or container orchestration (Docker Compose, Kubernetes).

**Scaling**: API and UI can scale horizontally. Agents can be distributed across machines using MCP protocol.

**Monitoring**: Logging to files or centralized system, metrics collection, health check endpoints, error tracking.

### MCP Distributed Mode

**Agent Servers**: Each agent runs as independent MCP server on assigned port. Communicate via MCP protocol (JSON-RPC over HTTP/SSE).

**Coordinator**: Connects to agent servers via MCP client. Can run on same machine or separate machine.

**Discovery**: Agent servers register capabilities via MCP tools/list. Coordinator discovers available tools dynamically.

**Fault Tolerance**: Handle agent server failures gracefully, retry logic, fallback to local mode if MCP unavailable.

---

## 11. Testing Strategy

### Unit Tests

**Domain Models**: Test Pydantic model validation, edge cases, helper methods.

**Game Engine**: Test move validation, win detection, draw detection, state management.

**Agents**: Test each agent in isolation with mocked LLM, validate input/output types, test error handling.

### Integration Tests

**Agent Pipeline**: Test full pipeline (Scout → Strategist → Executor) with real or mocked LLM.

**API Endpoints**: Test API endpoints with test client, validate request/response models, test error cases.

**Game Flow**: Test complete game from start to finish, test win/loss/draw scenarios, test player and AI moves.

### End-to-End Tests

**Full System**: Test with Streamlit UI, FastAPI backend, and real agents. Test user interactions, verify game state persistence, test metrics collection.

### Performance Tests

**Agent Response Times**: Measure agent execution times, identify bottlenecks, test with different LLM providers.

**Concurrent Games**: Test multiple simultaneous games, verify no state leakage, test resource usage.

---

## 12. Error Handling and Resilience

### Error Categories

**Validation Errors**: Invalid moves, malformed requests, type mismatches. Return clear error messages with validation details.

**Agent Errors**: LLM failures, timeout errors, parsing errors. Log details, return fallback responses, continue game if possible.

**System Errors**: Network failures, database errors, configuration errors. Log critical errors, provide user-friendly messages, implement circuit breakers if needed.

### Fallback Strategies

**Agent Fallbacks**: If Scout fails, use rule-based analysis. If Strategist fails, use Scout's best opportunity. If Executor fails, use Strategist's primary move directly.

**Game Continuity**: Game continues even if agent fails. Use last known good state, provide default moves, allow player to continue.

**UI Resilience**: UI handles API failures gracefully, shows error messages, allows retry, maintains local game state.

---

## 13. Security Considerations

### API Security

**Input Validation**: All inputs validated via Pydantic models, sanitize user inputs, prevent injection attacks.

**Rate Limiting**: Limit API request rates, prevent abuse, implement per-user limits if multi-user.

**Authentication** (if multi-user): Implement user authentication, session management, authorization checks.

### Data Security

**API Keys**: Store in environment variables, never commit to version control, use secrets management in production.

**Game State**: Validate game state integrity, prevent state manipulation, log state changes.

**Agent Communication**: If using MCP over network, use HTTPS, validate MCP protocol messages, prevent unauthorized agent access.

---

## 14. Performance Optimization

### Agent Performance

**Fast Path Analysis**: Rule-based checks for immediate wins/blocks before LLM calls, cache common patterns, optimize LLM prompts.

**Shared LLM Connection**: Reuse LLM connections across agents, connection pooling, efficient token usage.

**Async Operations**: All agent calls are async, parallel execution where possible, non-blocking I/O.

### Game Performance

**State Management**: Efficient board representation, minimize state copies, lazy evaluation where possible.

**UI Performance**: Efficient Streamlit reruns, minimize data transfer, use caching for expensive operations.

### Scalability

**Stateless Agents**: Agents are stateless, can be scaled horizontally, easy to distribute.

**Efficient Protocols**: MCP protocol is lightweight, minimal overhead, efficient serialization.

---

## 15. Agent Mode Architecture

### Mode 1: LangChain (Local, Fast)

**Description**: Direct LangChain chains with shared LLM connection. No MCP protocol overhead.

**Characteristics**:
- Fast execution (< 1 second per move)
- Direct Python method calls
- Shared LLM connection for efficiency
- Rule-based pre-checks for immediate wins/blocks
- Best for production use

**Implementation**: Agents implement interfaces directly using LangChain chains. Coordinator calls agents via direct Python methods.

### Mode 2: LangChain + MCP (Distributed, Protocol-Based)

**Description**: LangChain agents with MCP protocol support for distributed coordination.

**Characteristics**:
- MCP protocol for inter-agent communication
- Can distribute agents across machines
- Protocol overhead (3-8 seconds per move)
- Standardized API for external clients
- Best for demonstration and distributed scenarios

**Implementation**: Agents inherit from BaseMCPAgent, expose MCP tools, run as MCP servers. Coordinator uses MCP client to communicate.

### Mode Selection

**Configuration**: Selected via config.json or command-line argument.

**Runtime**: Can switch modes without code changes (different agent implementations).

**Fallback**: If MCP mode fails, can fall back to local mode automatically.

---

## 16. LLM Integration

### Supported Providers

**OpenAI**: GPT-5 mini (default), GPT-4.1 (fallback), GPT-4o, GPT-4o-mini, GPT-4 Turbo, GPT-4, GPT-3.5 Turbo, o1-preview, o1-mini. Via langchain-openai.

**Anthropic**: Claude Opus 4.5 (default), Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku. Via langchain-anthropic.

**Google Gemini**: Gemini 3 Flash (default), Gemini 2.5 Flash (fallback), Gemini Pro, Gemini Flash, Gemini 1.5 Pro, Gemini 1.5 Flash. Via langchain-google-genai.

**Ollama**: Local models (Llama, Mistral, etc.). Via langchain-community.

### Shared LLM Connection

**Purpose**: Reuse single LLM connection across all agents to reduce overhead.

**Implementation**: SharedLLMConnection class manages connection, provides get_connection() method.

**Configuration**: Model selection in config, API keys from environment. Default models: OpenAI uses GPT-5 mini (fallback: GPT-4.1), Anthropic uses Claude Opus 4.5, Google Gemini uses Gemini 3 Flash (fallback: Gemini 2.5 Flash).

**Error Handling**: Connection retry logic, fallback to individual connections if shared fails.

### LLM Usage Patterns

**Scout**: Uses LLM for strategic analysis when rule-based checks don't find immediate wins/blocks.

**Strategist**: Always uses LLM to synthesize analysis into strategy.

**Executor**: Uses LLM for move validation and reasoning, but can fall back to rule-based validation.

---

## 17. Metrics and Observability

### Agent Metrics

**Per-Agent Tracking**:
- Execution time (min, max, average)
- Success/failure rate
- LLM call count
- Token usage
- Error count and types

**Aggregation**: Metrics aggregated per agent, per game, and system-wide.

### Game Metrics

**Game-Level Tracking**:
- Total moves
- Game duration
- Win/loss/draw statistics
- Average move time
- Agent pipeline success rate

### System Metrics

**System-Level Tracking**:
- Total games played
- System uptime
- Resource usage (CPU, memory)
- API request rates
- Error rates

### Metrics Display

**Streamlit Dashboard**: Real-time metrics display with charts and tables.

**API Endpoints**: Metrics available via REST API for external monitoring.

**Logging**: Metrics logged to files for historical analysis.

---

## 18. Future Enhancements

### Potential Features

**Difficulty Levels**: Adjust agent sophistication based on difficulty setting.

**Multi-Player Support**: Support for multiple human players or AI vs AI.

**Game Variants**: Support for different board sizes or game rules.

**Learning**: Track game patterns, learn from player behavior.

**Tournament Mode**: Multiple games, statistics tracking.

### Technical Improvements

**Caching**: Cache common board patterns and analysis results.

**Optimization**: Further optimize LLM prompts, reduce token usage.

**Testing**: Expand test coverage, add property-based testing.

**Documentation**: Expand user guides, add video tutorials.

---

## Appendix

### Agent-to-Agent (A2A) Communication

The core architecture uses coordinator-mediated communication (see Section 3: Agent Architecture, Agent Pipeline Flow). Agent-to-Agent (A2A) communication, where agents communicate directly without coordinator mediation, is an optional enhancement for advanced use cases.

**Note**: For the Tic-Tac-Toe game, the coordinator pattern is simpler, sufficient, and recommended. A2A introduces additional complexity including multiple communication paths, more complex error handling, increased coupling between agents, and additional configuration requirements. Consider A2A only if specific requirements emerge that justify the added complexity, such as iterative refinement between agents or advanced collaborative workflows.

If implementing A2A, it should use the same domain models (GameState, BoardAnalysis, Strategy, etc.) to maintain type safety and consistency. In local mode, agents can use direct method calls via dependency injection. In distributed MCP mode, agents would act as both MCP servers and clients for peer-to-peer communication.

---

This specification provides a comprehensive foundation for implementing the Tic-Tac-Toe multi-agent game with clear abstractions, type safety, and separation of concerns. The design emphasizes domain models, clean interfaces, and protocol abstraction while maintaining flexibility for different deployment scenarios.


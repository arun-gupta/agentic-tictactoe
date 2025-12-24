# Tic-Tac-Toe Multi-Agent Game Specification

## 1. System Overview

### Purpose
A Tic-Tac-Toe game between a human player and an AI opponent. The AI uses three specialized agents (Scout, Strategist, Executor) to make moves. The application is built API-first, with all communication API-driven through REST endpoints. Players interact via a Streamlit UI that communicates with the backend through the API layer. The system supports both local execution and distributed MCP-based coordination.

### Design Principles

**Architectural Foundations:**
- **API-First Design**: All communication is API-driven; the application is built API-first with REST endpoints as the primary interface. The UI and other clients communicate exclusively through the API layer.
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
- **Mode Interchangeability**: Agents can switch between local (LLM framework-based) and distributed (MCP) modes at runtime
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

**Move Priority**: Enum defining priority levels for move recommendations (see Priority System below for details):
- IMMEDIATE_WIN (priority: 100) - We can win on this move
- BLOCK_THREAT (priority: 90) - Opponent can win next move, must block
- FORCE_WIN (priority: 80) - Create unstoppable winning position (fork)
- PREVENT_FORK (priority: 70) - Block opponent from creating a fork
- CENTER_CONTROL (priority: 50) - Take center position (opening)
- CORNER_CONTROL (priority: 40) - Take corner position (strategic)
- EDGE_PLAY (priority: 30) - Take edge position (less strategic)
- RANDOM_VALID (priority: 10) - Any valid move (fallback)

**Move Recommendation**: Strategist output with position, priority (MovePriority enum), confidence (0.0-1.0), reasoning, and expected outcome.

**Strategy**: Strategist output containing:
- Primary move recommendation (highest priority)
- Alternative move recommendations (sorted by priority descending)
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
- Prioritizes moves using the Move Priority System (see below)
- Recommends primary move with alternatives (all sorted by priority)
- Provides game plan and risk assessment
- Considers long-term position and confidence scoring

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

### Agent Timeout Configuration

**Per-Agent Timeouts**:
- **Scout Agent**: 5 seconds (rule-based fallback available)
- **Strategist Agent**: 5 seconds (uses Scout's best opportunity as fallback)
- **Executor Agent**: 3 seconds (direct move execution, minimal processing)
- **Total Pipeline Timeout**: 15 seconds (sum of all agents + 2s buffer)

**Timeout Behavior**:
- At 2 seconds: Show loading spinner with "AI is thinking..."
- At 5 seconds: Update message to "AI is analyzing carefully..." and show progress bar
- At 10 seconds: Update message to "Taking longer than usual, preparing fallback..."
- At timeout: Execute fallback strategy and show completion message

**Configuration**:
- Timeout values configurable via config file
- Different timeouts for local mode (5s/5s/3s) vs distributed MCP mode (10s/10s/5s)
- Per-provider timeout adjustments (e.g., local Ollama may need longer timeouts)

### Move Priority System

The Move Priority System defines a strict ordering for move selection with numeric priority values and clear decision rules:

**Priority Levels (Descending Order)**:

1. **IMMEDIATE_WIN (100)**: We have two in a row and can complete three
   - Detection: Check all lines (rows, cols, diagonals) for 2 AI symbols + 1 empty
   - Action: Always take this move immediately
   - Confidence: 1.0 (guaranteed win)
   - Example: AI has X at (0,0) and (0,1), play (0,2) to win

2. **BLOCK_THREAT (90)**: Opponent has two in a row and will win next move
   - Detection: Check all lines for 2 opponent symbols + 1 empty
   - Action: Must block immediately (defensive)
   - Confidence: 1.0 (necessary to continue)
   - Example: Opponent has O at (1,0) and (1,1), must play (1,2)

3. **FORCE_WIN (80)**: Create a fork (two winning opportunities simultaneously)
   - Detection: Move creates two unblocked lines with 2 AI symbols each
   - Action: Opponent cannot block both, guarantees eventual win
   - Confidence: 0.95 (near-certain advantage)
   - Example: Play corner to create two diagonal threats

4. **PREVENT_FORK (70)**: Block opponent from creating a fork
   - Detection: Opponent's move would create two winning threats
   - Action: Block the setup position or force opponent to defend
   - Confidence: 0.85 (prevents opponent advantage)
   - Example: Block opponent's second corner when they hold opposite corner

5. **CENTER_CONTROL (50)**: Take center position (1,1)
   - Detection: Center is empty and no higher priority moves exist
   - Action: Center provides most strategic flexibility (4 lines)
   - Confidence: 0.75 (strong opening/midgame)
   - Example: First move or early game when center available

6. **CORNER_CONTROL (40)**: Take corner position (0,0 / 0,2 / 2,0 / 2,2)
   - Detection: Corner is empty and no higher priority moves exist
   - Action: Corners participate in 3 lines each (row, col, diagonal)
   - Confidence: 0.60 (solid strategic position)
   - Example: Opening move or when center taken

7. **EDGE_PLAY (30)**: Take edge position (0,1 / 1,0 / 1,2 / 2,1)
   - Detection: Edge is empty and no higher priority moves exist
   - Action: Edges only participate in 2 lines each (less strategic)
   - Confidence: 0.40 (weaker position)
   - Example: Most corners and center taken

8. **RANDOM_VALID (10)**: Any valid empty cell
   - Detection: No strategic patterns detected
   - Action: Pick any available move (fallback)
   - Confidence: 0.20 (minimal strategic value)
   - Example: Backup when analysis fails

**Decision Algorithm**:

```
1. Scout identifies all opportunities and threats
2. Strategist evaluates each possible move:
   a. Check for IMMEDIATE_WIN (priority 100)
   b. Check for BLOCK_THREAT (priority 90)
   c. Check for FORCE_WIN (priority 80)
   d. Check for PREVENT_FORK (priority 70)
   e. Check for CENTER_CONTROL (priority 50)
   f. Check for CORNER_CONTROL (priority 40)
   g. Check for EDGE_PLAY (priority 30)
   h. Fallback to RANDOM_VALID (priority 10)
3. Select move with highest priority value
4. If multiple moves have same priority, use confidence score as tiebreaker
5. If still tied, prefer moves in this order: center > corners > edges
```

**Tie-Breaking Rules**:
1. Higher numeric priority always wins
2. Same priority → higher confidence score
3. Same confidence → position preference (center > corner > edge)
4. Same position type → prefer positions that participate in more open lines
5. Final tiebreaker → deterministic position ordering (0,0 < 0,1 < 0,2 < 1,0...)

**Validation**:
- All moves must be validated before recommendation
- Invalid moves (occupied, out of bounds) are automatically filtered
- If highest priority move is invalid, try next priority
- Executor performs final validation before execution

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

**Game Board Display**: Visual 3x3 grid showing X, O, and empty cells. Clickable cells for player moves. Highlights last move with animated transitions. Shows current player turn. Displays move history directly on the board game interface, showing a chronological list of moves with player/AI indicator, move number, position, and timestamp. Move history entries include expandable details showing agent reasoning. Animated moves provide smooth visual transitions when pieces are placed on the board.

**Agent Insights Panel**: Real-time display of:
- Scout analysis (threats, opportunities, strategic moves)
- Strategist strategy (recommended move, reasoning, priority)
- Executor execution (validation, success status, timing)
- Loading indicators for each agent step showing current agent activity
- Agent "thinking" animation/progress indicator with visual feedback during LLM processing
- Estimated time remaining for AI move based on historical agent performance

**AI Processing Status Display**:

Progressive status updates based on elapsed time:
- **0-2 seconds**: Show subtle loading spinner next to current agent name (e.g., "Scout analyzing...")
- **2-5 seconds**: Upgrade to animated progress bar with message "AI is thinking..."
- **5-10 seconds**: Show detailed progress with message "AI is analyzing carefully..." and elapsed time counter
- **10-15 seconds**: Show warning indicator with message "Taking longer than usual, preparing fallback..." and option to force fallback
- **15+ seconds**: Automatically trigger fallback, show message "Using quick analysis..." with explanation

**Status Indicators**:
- Green pulse: Agent actively processing
- Yellow pulse: Agent taking longer than expected (>5s)
- Orange pulse: Approaching timeout (>10s)
- Blue checkmark: Agent completed successfully
- Red X: Agent failed, using fallback
- Gray: Agent not yet started or skipped

**Interactive Elements**:
- "Force Fallback" button appears after 10 seconds, allows user to skip waiting
- "Show Details" expands to show exact timeout values and fallback strategy
- "Retry with Different Model" option appears on timeout/failure

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
- Agent mode used (local or distributed MCP)
- LLM framework used (see Section 19: Implementation Choices)
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

**Model Selection**: Dropdown to select LLM provider (OpenAI, Anthropic, Google Gemini, Ollama) and model name. User preferences for LLM settings are automatically saved and restored in future sessions.

**Agent Mode Selection**: Toggle between local mode (LLM framework-based, fast) and distributed MCP mode (protocol-based). LLM framework selection (LangChain, LiteLLM, Instructor, or Direct SDKs) determines which multi-provider abstraction layer is used - see Section 19 for options.

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
- strategy.py: Strategist agent models (MovePriority enum, MoveRecommendation, Strategy)
- execution.py: Executor agent models (ValidationError, MoveExecution)
- results.py: Result wrapper models (AgentResult)
- api.py: API request/response models

Note: MovePriority enum defines 8 priority levels (IMMEDIATE_WIN=100, BLOCK_THREAT=90, FORCE_WIN=80, PREVENT_FORK=70, CENTER_CONTROL=50, CORNER_CONTROL=40, EDGE_PLAY=30, RANDOM_VALID=10) - see Section 3 for full priority system specification.

**agents/**: Agent implementations:
- interfaces.py: Abstract base classes and protocols
- scout_local.py: Local Scout implementation using configured LLM framework
- strategist_local.py: Local Strategist implementation using configured LLM framework
- executor_local.py: Local Executor implementation using configured LLM framework
- scout_mcp.py: Scout with MCP protocol support
- strategist_mcp.py: Strategist with MCP protocol support
- executor_mcp.py: Executor with MCP protocol support
- base_mcp_agent.py: Base class for MCP protocol support

Note: Agents use an LLM framework abstraction layer that supports multiple providers. LLM framework choice (LangChain, LiteLLM, Instructor, Direct SDKs) determines the multi-provider abstraction implementation - see Section 19.

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
- shared_llm.py: Shared LLM connection manager with pooling
- factory.py: LLM provider factory supporting multi-provider frameworks
- provider_adapter.py: Abstraction layer for different LLM frameworks

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

**LLM Integration Framework**: One of LangChain, LiteLLM, Instructor, or Direct SDKs (see Section 19 for comparison and selection guidance). Include appropriate provider packages (OpenAI SDK, Anthropic SDK, Google GenAI SDK) based on framework choice.

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

**Agent Framework Configuration**: Mode selection (local or distributed_mcp), LLM framework selection for multi-provider support (see Section 19), model selection per agent or shared, timeout settings per agent (Scout: 5s, Strategist: 5s, Executor: 3s in local mode; 10s/10s/5s in distributed mode), retry logic.

**LLM Provider Configuration**: Provider selection (OpenAI, Anthropic, Google Gemini, Ollama), API keys (from environment), model names, temperature and other parameters, token limits. Default models: OpenAI uses GPT-5 mini (fallback: GPT-4.1), Anthropic uses Claude Opus 4.5, Google Gemini uses Gemini 3 Flash (fallback: Gemini 2.5 Flash).

**Game Configuration**: Default player symbol, AI symbol, game rules (if configurable), move timeout.

**MCP Configuration** (if using MCP mode): Port assignments per agent, server URLs for distributed mode, protocol settings, transport type (stdio, HTTP, SSE).

**Port Configuration**: All service ports must be configurable through the configuration file. API server port (default: 8000), Streamlit UI port (default: 8501), MCP agent server ports (if using distributed mode). No hardcoded ports in application code.

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

### Containerization and Orchestration

**Docker Files**:

The project should include simple, functional Dockerfiles:

**Dockerfile**: Single Dockerfile for the application
- Base image: Python 3.11+
- Install dependencies from requirements.txt
- Copy application code
- Expose ports: 8000 (API) and 8501 (UI)
- Default command to run the application

**Docker Compose**:

**docker-compose.yml**: Simple compose file for local development
- Services: api (FastAPI) and ui (Streamlit)
- Network for service communication
- Environment variables from .env file
- Volume mounts for code (development only)

**Kubernetes Helm Charts**:

**Chart Structure**:
```
helm/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml  # Deployments for API and UI services
    ├── service.yaml     # Services for API and UI
    ├── configmap.yaml   # Application configuration
    └── secret.yaml      # API keys and secrets
```

**Helm Chart Components**:

**Deployments**: Simple deployments for API and UI services
- Single replica per service (configurable via values)
- Environment variables from ConfigMap and Secrets
- Basic container image configuration

**Services**: ClusterIP services for API and UI
- API service on port 8000
- UI service on port 8501

**ConfigMap**: Application configuration (model names, timeouts, feature flags)

**Secret**: LLM API keys and sensitive configuration
- Store API keys for OpenAI, Anthropic, Google Gemini
- Use Kubernetes secrets (create manually or via kubectl)

**values.yaml**: Basic configuration
- Image name and tag
- Number of replicas (default: 1)
- Service ports
- LLM provider settings
- Environment-specific overrides

---

## 11. Testing Strategy

### Unit Tests

**Domain Models**: Test Pydantic model validation, edge cases, helper methods. Schema validation for all domain models to ensure type safety and data integrity.

**Game Engine**: Test move validation, win detection, draw detection, state management. Use parameterized tests for multiple scenarios to cover all game states efficiently.

**Agents**: Test each agent in isolation with mocked LLM, validate input/output types, test error handling. Agent interface contract validation to ensure all agents comply with protocol definitions.

**Test Data Management**: Fixture strategies for common game states (opening, midgame, endgame, win scenarios). Test data generators for board positions to create diverse test cases programmatically.

### Integration Tests

**Agent Pipeline**: Test full pipeline (Scout → Strategist → Executor) with real or mocked LLM.

**API Endpoints**: Test API endpoints with test client, validate request/response models, test error cases.

**Game Flow**: Test complete game from start to finish, test win/loss/draw scenarios, test player and AI moves.

**Contract Tests**: API contract tests between UI and backend to ensure interface compatibility and prevent breaking changes.

**MCP Protocol Tests**: Test MCP client/server communication, protocol compliance, and mode switching between local and distributed modes.

### End-to-End Tests

**Full System**: Test with Streamlit UI, FastAPI backend, and real agents. Test user interactions, verify game state persistence, test metrics collection.

### Performance Tests

**Agent Response Times**: Measure agent execution times, identify bottlenecks, test with different LLM providers.

**Concurrent Games**: Test multiple simultaneous games, verify no state leakage, test resource usage.

### Resilience Tests

**LLM Failure Scenarios**: Simulate LLM timeouts/failures to verify graceful degradation and fallback strategies work correctly.

**Agent Failure Cascade Testing**: Test system behavior when agents fail in sequence, verify error propagation and recovery mechanisms.

### Test Coverage

**Coverage Targets**: Minimum code coverage targets of 80% for unit tests and 70% for integration tests. Use pytest-cov for coverage reporting.

**Critical Path Testing**: Critical path smoke tests for CI/CD to validate core functionality in automated pipelines.

### CI/CD Integration

**GitHub Actions**: Integration with GitHub Actions for automated testing on pull requests and commits. Run unit tests, integration tests, and smoke tests in CI pipeline. Enforce coverage thresholds before merging.

---

## 12. Error Handling and Resilience

### Error Categories

**Validation Errors**: Invalid moves, malformed requests, type mismatches. Return clear error messages with validation details.

**Agent Errors**: LLM failures, timeout errors, parsing errors. Log details, return fallback responses, continue game if possible.

**System Errors**: Network failures, database errors, configuration errors. Log critical errors, provide user-friendly messages, implement circuit breakers if needed.

### Error Handling Matrix

This table defines standardized handling for all error scenarios:

| Error Type | Error Code | Retry Policy | Fallback Strategy | User Message | Log Level | Test Coverage |
|------------|------------|--------------|-------------------|--------------|-----------|---------------|
| **LLM API Timeout** | `LLM_TIMEOUT` | 3 retries, exponential backoff (1s, 2s, 4s); per-agent timeouts: Scout 5s, Strategist 5s, Executor 3s (local mode) | Use rule-based move selection | "AI is taking longer than expected. Using quick analysis..." | WARNING | Resilience test required |
| **LLM Parse Error** | `LLM_PARSE_ERROR` | 2 retries with prompt refinement | Use previous successful agent output or rule-based | "AI response unclear. Using backup strategy..." | ERROR | Unit test required |
| **LLM Rate Limit** | `LLM_RATE_LIMIT` | Wait + retry once after rate limit window | Queue request or use cached response | "AI is busy. Please wait a moment..." | WARNING | Integration test required |
| **LLM Invalid API Key** | `LLM_AUTH_ERROR` | No retry | Fallback to rule-based moves entirely | "AI configuration error. Using rule-based play." | CRITICAL | Smoke test required |
| **Scout Agent Failure** | `SCOUT_FAILED` | 1 retry | Use rule-based board analysis (immediate wins/blocks/center) | "AI analysis unavailable. Using standard tactics..." | ERROR | Resilience test required |
| **Strategist Agent Failure** | `STRATEGIST_FAILED` | 1 retry | Use Scout's highest priority opportunity directly | "AI strategy unavailable. Using tactical move..." | ERROR | Resilience test required |
| **Executor Agent Failure** | `EXECUTOR_FAILED` | 1 retry | Use Strategist's primary move with basic validation | "AI execution error. Applying recommended move..." | ERROR | Resilience test required |
| **Invalid Move (Out of Bounds)** | `MOVE_OUT_OF_BOUNDS` | No retry | Return error to user, request new move | "Invalid move: Position out of bounds (0-2 only)" | INFO | Unit test required |
| **Invalid Move (Cell Occupied)** | `MOVE_OCCUPIED` | No retry | Return error to user, request new move | "Invalid move: Cell already occupied" | INFO | Unit test required |
| **MCP Connection Failed** | `MCP_CONN_FAILED` | 2 retries with 5s delay | Switch to local mode agents | "Distributed mode unavailable. Using local agents..." | ERROR | Integration test required |
| **MCP Agent Timeout** | `MCP_TIMEOUT` | 1 retry with 10s timeout | Switch to local mode for that agent | "Agent not responding. Using local fallback..." | WARNING | Resilience test required |
| **API Request Malformed** | `API_MALFORMED` | No retry | Return 400 Bad Request with validation details | "Invalid request: [specific validation error]" | INFO | Contract test required |
| **Game State Corrupted** | `STATE_CORRUPTED` | No retry | Reset game state, log incident | "Game state error. Please restart the game." | CRITICAL | Integration test required |
| **Network Error (API)** | `NETWORK_ERROR` | 3 retries with exponential backoff | Show cached state, allow offline mode | "Connection lost. Retrying..." | WARNING | E2E test required |
| **Configuration Error** | `CONFIG_ERROR` | No retry | Use default configuration | "Configuration issue. Using defaults..." | ERROR | Smoke test required |
| **Pydantic Validation Error** | `SCHEMA_VALIDATION_ERROR` | No retry | Log error, return sanitized default | "Data format error. Using safe defaults..." | ERROR | Unit test required |

### Fallback Strategies

**Agent Fallbacks**: If Scout fails, use rule-based analysis. If Strategist fails, use Scout's best opportunity. If Executor fails, use Strategist's primary move directly.

**Game Continuity**: Game continues even if agent fails. Use last known good state, provide default moves, allow player to continue.

**UI Resilience**: UI handles API failures gracefully, shows error messages, allows retry, maintains local game state.

### Implementation Guidelines

**Retry Logic**:
- Use exponential backoff for transient errors
- Include jitter to prevent thundering herd
- Set maximum retry limits to prevent infinite loops
- Log each retry attempt with context

**Fallback Execution**:
- Always validate fallback outputs before applying
- Track fallback usage in metrics
- Alert on excessive fallback usage (> 10% of moves)
- Document fallback behavior for users

**Error Logging**:
- Include error code, context, and stack trace
- Track error frequency and patterns
- Implement alerting for CRITICAL errors
- Sanitize sensitive data before logging

**User Communication**:
- Use user-friendly, non-technical language
- Provide actionable guidance when possible
- Show progress indicators during retries
- Allow manual override/retry for failed actions

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

### Mode 1: Local (Fast)

**Description**: In-process agent execution using an LLM framework with shared connection pooling. No MCP protocol overhead. The LLM framework (LangChain, LiteLLM, Instructor, or Direct SDKs - see Section 19) provides multi-provider support, allowing LLM provider switching via configuration.

**Characteristics**:
- Fast execution (< 1 second per move)
- Direct Python method calls between coordinator and agents
- Shared LLM connection for efficiency
- Rule-based pre-checks for immediate wins/blocks
- LLM provider hot-swapping via configuration
- Best for production use

**Implementation**: Agents implement interfaces using the configured LLM framework. Coordinator calls agents via direct Python methods. The framework handles provider abstraction and connection management.

### Mode 2: Distributed MCP (Protocol-Based)

**Description**: Agents with MCP protocol support for distributed coordination. Can use any LLM framework internally (see Section 19).

**Characteristics**:
- MCP protocol for inter-agent communication (note: MCP is designed for tool integration and cross-process communication, not optimized for high-frequency agent coordination; use this mode when agents need to run on separate machines)
- Can distribute agents across machines
- Protocol overhead (3-8 seconds per move)
- Standardized API for external clients
- Best for demonstration and distributed scenarios

**Implementation**: Agents inherit from BaseMCPAgent, expose MCP tools, run as MCP servers. Coordinator uses MCP client to communicate.

### Mode Selection

**Configuration**: Agent mode and LLM framework selected via config.json or command-line argument. See Section 19 for framework comparison.

**Runtime**: Can switch modes without code changes (different agent implementations).

**Fallback**: If MCP mode fails, can fall back to local mode automatically.

---

## 16. LLM Integration

**Note**: This section describes LLM provider and model configuration. For LLM framework selection (LangChain, LiteLLM, Instructor, Direct SDKs), see Section 19: Implementation Choices.

### Supported Providers

**OpenAI**: GPT-5 mini (default), GPT-4.1 (fallback), GPT-4o, GPT-4o-mini, GPT-4 Turbo, GPT-4, GPT-3.5 Turbo, o1-preview, o1-mini.

**Anthropic**: Claude Opus 4.5 (default), Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku.

**Google Gemini**: Gemini 3 Flash (default), Gemini 2.5 Flash (fallback), Gemini Pro, Gemini Flash, Gemini 1.5 Pro, Gemini 1.5 Flash.

**Ollama**: Local models (Llama, Mistral, etc.).

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

## 19. Implementation Choices and Alternatives

This section discusses architectural decisions and alternative approaches for key system components.

### Agent Communication Patterns

**Coordinator-Mediated (Current Architecture)**:

The core architecture uses coordinator-mediated communication (see Section 3: Agent Architecture, Agent Pipeline Flow). The coordinator orchestrates a sequential pipeline (Scout → Strategist → Executor) where each agent receives input from the coordinator and returns results.

**Why This Pattern**: This game implements a **sequential pipeline architecture** where agents have strict dependencies. Each agent requires the previous agent's output as input, and the coordinator manages the authoritative game state. This pattern provides centralized error handling, clear data flow, and simplified state management.

**Agent-to-Agent (A2A) Communication**:

Agent-to-Agent (A2A) communication, where agents communicate directly without coordinator mediation, is an optional enhancement for advanced use cases.

**Why A2A Is Not Used Here**: The coordinator pattern is simpler, sufficient, and recommended for this game. A2A introduces additional complexity including multiple communication paths, more complex error handling, increased coupling between agents, and additional configuration requirements. A2A is designed for peer-to-peer collaboration scenarios, not sequential pipelines with centralized state management.

**When to Consider A2A**: Consider A2A only if specific requirements emerge that justify the added complexity, such as iterative refinement between agents (Strategist requests Scout re-analyze), advanced collaborative workflows, or autonomous agent negotiation.

If implementing A2A, it should use the same domain models (GameState, BoardAnalysis, Strategy, etc.) to maintain type safety and consistency. In local mode, agents can use direct method calls via dependency injection. In distributed MCP mode, agents would act as both MCP servers and clients for peer-to-peer communication.

### MCP Protocol Usage

**When MCP Is Useful**:

The MCP (Model Context Protocol) mode is useful in specific scenarios:
- **Distributed Deployments**: Agents running on separate physical machines for resource isolation or geographic distribution
- **Microservices Architecture**: Each agent as an independent service with standardized API
- **External Agent Access**: Exposing agents to external systems or third-party clients
- **Development/Learning**: Demonstrating protocol-based agent communication patterns
- **Fault Isolation**: Isolating agent failures to separate processes

**When MCP Is Not Needed**:

For single-machine deployments with co-located agents, the local mode provides better performance (< 1 second vs 3-8 seconds) without protocol overhead. MCP is a transport layer for cross-process communication, not optimized for high-frequency in-process agent coordination.

### LLM Integration Framework Options

Multiple LLM integration framework options exist with different trade-offs:

**Option 1: LangChain**

**Description**: Full-featured LLM application framework with chains, agents, and multi-provider support.

**Pros**:
- Rich ecosystem and community support
- Built-in multi-provider support (OpenAI, Anthropic, Google, Ollama)
- Chain abstractions for agent workflows
- Prompt management and templates
- MCP integration available

**Cons**:
- Heavy framework with abstraction layers
- Performance overhead from middleware
- Frequent API changes between versions
- May be overkill for simple LLM calls

**Best for**: Rapid prototyping, complex agent workflows, projects requiring LangChain ecosystem tools.

**Option 2: LiteLLM**

**Description**: Lightweight unified interface for 100+ LLM providers.

**Pros**:
- Single interface for all providers
- Much lighter than LangChain
- Drop-in replacement pattern
- Minimal overhead
- Good for multi-model testing

**Cons**:
- Fewer features than LangChain
- Smaller ecosystem
- Limited agent workflow abstractions

**Best for**: Multi-provider support without framework weight, performance-sensitive applications.

**Option 3: Direct SDK Calls**

**Description**: Use provider SDKs directly (OpenAI SDK, Anthropic SDK, Google GenAI SDK).

**Pros**:
- Lightweight, minimal overhead
- Direct control over API calls
- Better performance (no middleware)
- Stable provider APIs
- Easier debugging

**Cons**:
- Need separate code per provider
- Manual prompt management
- More boilerplate code
- Provider switching requires code changes

**Best for**: Production deployments prioritizing performance, single-provider applications.

**Option 4: Instructor (with Pydantic)**

**Description**: Type-safe structured outputs from LLMs using Pydantic models.

**Pros**:
- Perfect fit for Pydantic-based architectures (like this project)
- Type-safe LLM responses validated against domain models
- Works with multiple providers
- Automatic retry and validation
- Clean, minimal API

**Cons**:
- Focused on structured outputs
- Needs to be combined with direct SDKs
- Less comprehensive than LangChain

**Best for**: Projects using Pydantic domain models, type-safe architectures, production deployments requiring validation.

**Recommended Approach**:

For this project, **Instructor + Direct SDKs** is recommended for production use due to:
- Existing Pydantic domain models (BoardAnalysis, Strategy, MoveExecution)
- Type-safe validation of agent outputs
- Lightweight and performant
- Easy provider switching via configuration

**LangChain** remains a valid choice for rapid prototyping and if ecosystem features are needed.

**Implementation Strategy**: Make the LLM framework selection configurable. Create an abstraction layer (LLMProvider interface) that can be implemented by any framework, allowing runtime selection via configuration.

---

## Appendix

---

This specification provides a comprehensive foundation for implementing the Tic-Tac-Toe multi-agent game with clear abstractions, type safety, and separation of concerns. The design emphasizes domain models, clean interfaces, and protocol abstraction while maintaining flexibility for different deployment scenarios.


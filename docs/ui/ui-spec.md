# UI Visual Design Specification

## Overview

This document defines the visual design for the Tic-Tac-Toe Multi-Agent Game UI. It complements the functional requirements in [spec.md Section 6](./spec.md#6-web-ui-functional-requirements) by providing visual specifications, layouts, styling, and animations.

## Design Frames

Visual designs are provided as exported PNG frames from Figma, located in `docs/ui/frames/`.

**Frame Index:**
- `game-board.png` - Game board and move history panel (US-001 through US-007)
  - Game board: 3x3 grid with cell states and game status (US-001, US-002, US-003, US-004, US-005)
  - Move history: Chronological move list in same panel (US-006, US-007)
- `metrics-panel.png` - Agent insights and post-game metrics panel (US-008 through US-018)
  - Agent insights: Real-time agent status and analysis (US-008, US-009, US-010, US-011, US-012)
  - Post-game metrics: Performance data and LLM interactions (US-013, US-014, US-015, US-016, US-017, US-018)
- `config-panel.png` - Configuration panel (US-019, US-020, US-021)
  - LLM provider and model selection (US-019)
  - Agent mode configuration (US-020)
  - Game settings (US-021)

## Design System

### Color Palette

**Primary Colors:**
- Background: `#1a1a2e` (Dark navy)
- Surface: `#16213e` (Darker blue-gray)
- Card/Panel: `#0f3460` (Deep blue)

**Game Colors:**
- Player X: `#e94560` (Vibrant red/pink)
- Player O: `#00adb5` (Cyan/teal)
- Empty Cell: `#eaeaea` (Light gray)
- Grid Lines: `#533483` (Purple-gray)

**UI Elements:**
- Primary Action: `#00adb5` (Cyan)
- Secondary Action: `#533483` (Purple)
- Success: `#06d6a0` (Green)
- Warning: `#ffd166` (Yellow)
- Error: `#e94560` (Red)
- Disabled: `#6c757d` (Gray)

**Text Colors:**
- Primary Text: `#eaeaea` (Light gray)
- Secondary Text: `#a8a8a8` (Medium gray)
- Heading: `#ffffff` (White)

**Accent Colors:**
- Highlight: `#f72585` (Hot pink)
- Agent Activity: `#4361ee` (Bright blue)
- Win Line: `#06d6a0` (Green)

**Agent Status Colors:**
- Scout: `#4361ee` (Bright blue)
- Strategist: `#533483` (Purple)
- Executor: `#00adb5` (Cyan)
- Idle: `#6c757d` (Gray)
- Running: `#4361ee` (Bright blue) with pulse animation
- Success: `#06d6a0` (Green)
- Failed: `#e94560` (Red)

### Typography

**Font Family:**
- Primary: `'SF Pro Display', -apple-system, 'Helvetica Neue', 'Arial', sans-serif`
- Monospace (for metrics/code): `'SF Mono', 'Monaco', 'Menlo', monospace`

**Font Sizes:**
- Heading 1: `2.5rem` (40px) - Page title
- Heading 2: `1.5rem` (24px) - Panel titles
- Heading 3: `1.25rem` (20px) - Section headers
- Body: `1rem` (16px) - Default text
- Small: `0.875rem` (14px) - Secondary text
- Caption: `0.75rem` (12px) - Timestamps, labels
- Code/Metrics: `0.9rem` (14.4px) - Monospace content

**Font Weights:**
- Regular: `400` - Body text
- Medium: `500` - Secondary emphasis
- Semibold: `600` - Buttons, labels
- Bold: `700` - Headings, important data

**Line Heights:**
- Tight: `1.2` - Headings
- Normal: `1.5` - Body text
- Relaxed: `1.75` - Long-form content

### Spacing

**Grid System:**
- Base unit: `8px` (all spacing is multiples of 8)
- Gutter: `24px` (between major panels)
- Container max-width: `1200px`
- Container padding: `40px 20px`

**Component Spacing:**
- XSmall: `4px` - Tight element spacing
- Small: `8px` - Related items
- Medium: `16px` - Component internal spacing
- Large: `24px` - Section spacing
- XLarge: `32px` - Major section dividers
- XXLarge: `48px` - Page-level spacing

### Border Radius

- Small (buttons, inputs, tags): `6px`
- Medium (cards, panels, board cells): `12px`
- Large (modals, board container): `16px`
- XLarge (hero sections): `24px`
- Full (circular badges, avatars): `50%`

### Shadows

- **Elevation 1** (Subtle, for cards): `0 2px 4px rgba(0, 0, 0, 0.2)`
- **Elevation 2** (Medium, for hover states): `0 4px 8px rgba(0, 0, 0, 0.3)`
- **Elevation 3** (High, for dropdowns): `0 8px 16px rgba(0, 0, 0, 0.4)`
- **Elevation 4** (Very high, for modals): `0 16px 32px rgba(0, 0, 0, 0.5)`
- **Board container**: `0 8px 32px rgba(0, 0, 0, 0.4)`
- **Button hover**: `0 4px 12px rgba(0, 173, 181, 0.3)` (Primary color glow)
- **Glow effect** (highlights): `0 0 12px rgba(247, 37, 133, 0.4)` (Accent color)
- **Error glow**: `0 0 12px rgba(233, 69, 96, 0.4)` (Error color)
- **Success glow**: `0 0 12px rgba(6, 214, 160, 0.4)` (Success color)

## Component Specifications

### Game Board Panel

**User Stories:** US-001, US-002, US-003, US-004, US-005

**Visual Design:** `docs/ui/frames/game-board.png`

**Layout:**
- 3x3 grid with equal cell sizes
- Cell dimensions: `100px x 100px` (min-height enforced)
- Gap between cells: `12px`
- Board container padding: `30px`
- Board background: `#0f3460` (Card/Panel color)
- Board border-radius: `16px`
- Total board width: `336px` (3×100 + 2×12 + 2×30)

**Cell States:**
- **Empty**:
  - Background: `#16213e` (Surface)
  - Border: `3px solid #533483` (Grid Lines)
  - Border-radius: `12px`
  - Cursor: `pointer`
  - Font-size: `3rem` (48px)

- **Occupied (X)**:
  - Color: `#e94560` (Player X)
  - Font-weight: `700` (Bold)
  - Background: `#16213e` (Surface)
  - Cursor: `default`

- **Occupied (O)**:
  - Color: `#00adb5` (Player O)
  - Font-weight: `700` (Bold)
  - Background: `#16213e` (Surface)
  - Cursor: `default`

- **Hover (empty cell)**:
  - Background: `#0f3460` (Card)
  - Border-color: `#00adb5` (Primary Action)
  - Transform: `scale(1.05)`
  - Transition: `all 0.2s ease`

- **Disabled (AI turn)**:
  - Opacity: `0.6`
  - Cursor: `not-allowed`

- **Last move**:
  - Border-color: `#f72585` (Highlight)
  - Box-shadow: `0 0 12px rgba(247, 37, 133, 0.4)`

- **Winning cell**:
  - Background: `#06d6a0` (Win Line)
  - Border-color: `#06d6a0`
  - Animation: `pulse 0.5s ease-in-out`

**Game Status Display:**
- **Status bar**:
  - Background: `#16213e` (Surface)
  - Border-radius: `8px`
  - Padding: `15px 20px`
  - Margin-bottom: `20px`
  - Display: `flex`, justify-content: `space-between`

- **Current turn indicator**:
  - Font-size: `1.1rem` (17.6px)
  - Font-weight: `600` (Semibold)
  - Color (X turn): `#e94560`
  - Color (O turn): `#00adb5`

- **Move count**:
  - Font-size: `1rem` (16px)
  - Color: `#a8a8a8` (Secondary Text)

- **Game over message**:
  - Background: `#06d6a0` (Success)
  - Color: `#1a1a2e` (Background - for contrast)
  - Padding: `15px`
  - Border-radius: `8px`
  - Font-weight: `600`
  - Text-align: `center`
  - Margin-bottom: `15px`
  - Animation: `slideDown 0.3s ease-out`

- **Winner announcement**:
  - Same as game over message
  - Position: Above board, replaces status bar

**Interactions:**
- **Click empty cell**:
  - Scale animation: `scale(0.95)` for 100ms, then back to normal
  - Border pulse: Brief `#00adb5` glow

- **Invalid click**:
  - Shake animation: `translateX(-10px) -> translateX(10px)`, 3 cycles, 400ms total
  - Border flash: `#e94560` (Error) for 300ms
  - Optional error sound/haptic feedback

- **Disabled board**:
  - Semi-transparent overlay: `rgba(15, 52, 96, 0.7)`
  - Cursor: `not-allowed` on all cells
  - Pointer-events: `none` on grid

### Move History Panel

**User Stories:** US-006, US-007

**Visual Design:** `docs/ui/frames/game-board.png` (included in same panel as game board)

**Layout:**
- Position: Right side panel or below game board
- Background: `#16213e` (Surface)
- Border-radius: `12px`
- Padding: `20px`
- Border: `1px solid #533483` (Grid Lines)
- Max-height: `400px`
- Overflow-y: `auto` (scrollable)
- Move entry height: `auto` (min `50px`)
- Gap between entries: `8px`

**Move Entry:**
- Background: `#0f3460` (Card)
- Border-radius: `6px`
- Padding: `10px`
- Margin-bottom: `8px`
- Font-size: `0.9rem` (14.4px)
- Display: `flex`, align-items: `center`

- **Player indicator**:
  - Border-left for X: `3px solid #e94560`
  - Border-left for O: `3px solid #00adb5`
  - Player label: Font-weight `600`, respective player color

- **Move number**:
  - Font-size: `0.75rem` (12px)
  - Color: `#a8a8a8` (Secondary Text)
  - Position: Start of entry
  - Format: `#5` or `Move 5`

- **Position**:
  - Format: `(row, col)` or `Row 1, Col 2`
  - Font-size: `0.9rem` (14.4px)
  - Color: `#eaeaea` (Primary Text)
  - Font-family: Monospace for coordinates

- **Timestamp**:
  - Format: `10:30:45` or `2.3s ago`
  - Font-size: `0.75rem` (12px)
  - Color: `#a8a8a8` (Secondary Text)
  - Position: End of entry (right-aligned)

**Expandable Details:**
- **Expansion indicator**:
  - Icon: Chevron (▼ or ▶)
  - Size: `14px`
  - Color: `#a8a8a8` (Secondary Text)
  - Rotation: `0deg` (collapsed), `180deg` (expanded)
  - Transition: `transform 0.2s ease`
  - Position: Right side of entry

- **Expanded state**:
  - Background change: `#16213e` (Surface - slightly darker)
  - Border-left width: `4px` (thicker)
  - Padding increase: `15px`
  - Animation: `slideDown 0.2s ease-out`
  - Max-height transition for smooth expansion

- **Agent reasoning section**:
  - Margin-top: `10px`
  - Padding-left: `15px`
  - Border-left: `2px solid #533483` (Grid Lines)
  - Font-size: `0.875rem` (14px)
  - Color: `#a8a8a8` (Secondary Text)
  - Line-height: `1.5` (Normal)
  - Font-style: `italic` (optional)

- **Agent details**:
  - Scout analysis: Color `#4361ee` (Agent Activity)
  - Strategy: Color `#533483` (Strategist)
  - Execution details: Color `#00adb5` (Executor)
  - Label font-weight: `600` (Semibold)
  - Font-family: Monospace for technical details

**Scrollbar Styling:**
- Width: `8px`
- Track background: `#0f3460` (Card)
- Thumb background: `#533483` (Grid Lines)
- Thumb hover: `#6847a0` (Lighter purple)
- Border-radius: `4px`

### Agent Insights and Metrics Panel

**User Stories:** US-008 through US-018

**Visual Design:** `docs/ui/frames/metrics-panel.png` (combined panel for insights and metrics)

**Layout:**
- Combined panel showing agent insights during game and post-game metrics
- Adapts based on game state (in progress vs completed)

#### Agent Insights Section (US-008 through US-012)

**During Game:**
- Background: `#16213e` (Surface)
- Border-radius: `12px`
- Padding: `20px`
- Border: `1px solid #533483` (Grid Lines)
- Three agent sections (Scout, Strategist, Executor)
- Agent section min-height: `120px`
- Spacing between sections: `15px`

**Agent Status Indicators:**
- **Idle**:
  - Icon: Circle outline (○), size `8px`
  - Color: `#6c757d` (Gray/Disabled)

- **Running**:
  - Icon: Filled circle with pulse (●), size `8px`
  - Color: `#4361ee` (Agent Activity)
  - Animation: `blink 1.5s infinite`

- **Success**:
  - Icon: Checkmark (✓), size `16px`
  - Color: `#06d6a0` (Success)

- **Failed**:
  - Icon: X mark (✗), size `16px`
  - Color: `#e94560` (Error)

**Agent Name Display:**
- Font-size: `1rem` (16px)
- Font-weight: `600` (Semibold)
- Scout color: `#4361ee`
- Strategist color: `#533483`
- Executor color: `#00adb5`
- Status indicator inline before name

**Processing Status (US-010):**
- **0-2s: Basic spinner**
  - Type: Circular spinner
  - Size: `24px`
  - Color: `#4361ee` (Agent Activity)
  - Border-width: `3px`
  - Animation: `spin 0.8s linear infinite`

- **2-5s: Processing message**
  - Spinner + text below
  - Text: "Analyzing..." or "Processing..."
  - Font-size: `0.875rem` (14px)
  - Color: `#a8a8a8` (Secondary Text)

- **5-10s: Progress bar**
  - Height: `6px`
  - Background: `#0f3460` (Card)
  - Fill color: `#4361ee` (Agent Activity)
  - Border-radius: `3px`
  - Indeterminate animation
  - Elapsed time display: `0.75rem` (12px), right-aligned

- **10-15s: Warning indicator**
  - Border color changes to: `#ffd166` (Warning)
  - Warning icon (⚠): `16px`, `#ffd166`
  - Message: "Taking longer than expected..."
  - Countdown timer: Monospace, `0.875rem`

- **15s+: Fallback message**
  - Background: `rgba(255, 209, 102, 0.1)` (Warning tint)
  - Border: `2px solid #ffd166`
  - Message: "Agent not responding. Fallback will be used."
  - Font-size: `0.875rem` (14px)

**Agent Output Display:**
- **Analysis text**:
  - Font-size: `0.875rem` (14px)
  - Color: `#a8a8a8` (Secondary Text)
  - Line-height: `1.5` (Normal)
  - Max-lines: `5` with ellipsis
  - Background: `#0f3460` (Card)
  - Padding: `12px`
  - Border-radius: `6px`
  - Margin-top: `10px`

- **Threats/Opportunities**:
  - List style: Bullets with icons
  - Threat icon: ⚠ (Warning triangle), `#e94560`
  - Opportunity icon: ★ (Star), `#06d6a0`
  - Font-size: `0.875rem` (14px)
  - Line-height: `1.75` (Relaxed)
  - Max visible: 3 items, "Show more" link

- **Recommended move**:
  - Background: `rgba(0, 173, 181, 0.15)` (Primary tint)
  - Border-left: `3px solid #00adb5`
  - Padding: `12px`
  - Border-radius: `6px`
  - Font-weight: `600` (Semibold)
  - Position format: Monospace
  - Confidence score: `0.75rem`, right-aligned

**Action Buttons:**
- **Force Fallback button (after 10s)**:
  - Background: `#533483` (Secondary)
  - Color: `#eaeaea` (Primary Text)
  - Padding: `8px 16px`
  - Border-radius: `6px`
  - Font-size: `0.875rem` (14px)
  - Font-weight: `600`
  - Position: Below agent section
  - Hover: Background `#6847a0`, transform `translateY(-2px)`

- **Retry button (on failure)**:
  - Background: `#00adb5` (Primary)
  - Color: `#1a1a2e` (Dark text for contrast)
  - Padding: `8px 16px`
  - Border-radius: `6px`
  - Font-size: `0.875rem` (14px)
  - Font-weight: `600`
  - Hover: Background `#00c4cf`, transform `translateY(-2px)`

#### Post-Game Metrics Section (US-013 through US-018)

**User Stories:** US-013, US-014, US-015, US-016, US-017, US-018

**Visibility:**
- Hidden during game
- Visible only when `is_game_over = true`
- Replaces or overlays Agent Insights Section

**Layout:**
- Tabbed interface: Agent Communication | LLM Interactions | Performance | Game Summary
- Background: `#16213e` (Surface)
- Border-radius: `12px`
- Border: `1px solid #533483` (Grid Lines)
- Tab container background: `#0f3460` (Card)
- Tab height: `48px`
- Content padding: `20px`

**Tab Navigation:**
- Inactive tab background: `transparent`
- Active tab background: `#16213e` (Surface)
- Active tab border-bottom: `3px solid #00adb5` (Primary)
- Tab font-size: `0.9rem` (14.4px)
- Tab font-weight: `600` (Semibold)
- Tab padding: `12px 20px`
- Tab color (inactive): `#a8a8a8` (Secondary Text)
- Tab color (active): `#eaeaea` (Primary Text)
- Tab hover: Background `rgba(0, 173, 181, 0.1)`

**Agent Communication Tab (US-014):**
- **Request/Response pairs**:
  - Collapsible sections with chevron icon
  - Section background: `#0f3460` (Card)
  - Section padding: `15px`
  - Section margin-bottom: `12px`
  - Section border-radius: `8px`

- **JSON syntax highlighting**:
  - Background: `#1a1a2e` (Background - darker)
  - Font-family: Monospace
  - Font-size: `0.875rem` (14px)
  - Padding: `15px`
  - Border-radius: `6px`
  - String values: `#06d6a0` (Success)
  - Numbers: `#00adb5` (Primary)
  - Booleans: `#ffd166` (Warning)
  - Keys: `#f72585` (Highlight)
  - Null: `#6c757d` (Disabled)
  - Max-height: `300px` with scroll

**LLM Interactions Tab (US-015):**
- **Per-agent call logs**:
  - Agent sections collapsible
  - Agent header with color-coded indicator
  - Section spacing: `15px`

- **Prompt text**:
  - Background: `#0f3460` (Card)
  - Font-family: Monospace
  - Font-size: `0.875rem` (14px)
  - Padding: `15px`
  - Border-radius: `6px`
  - Border-left: `3px solid #4361ee` (Agent Activity)
  - Max-height: `200px` with scroll
  - Color: `#eaeaea` (Primary Text)

- **Response text**:
  - Background: `#0f3460` (Card)
  - Font-family: Monospace
  - Font-size: `0.875rem` (14px)
  - Padding: `15px`
  - Border-radius: `6px`
  - Border-left: `3px solid #06d6a0` (Success)
  - Max-height: `200px` with scroll
  - Color: `#eaeaea` (Primary Text)

- **Metadata display**:
  - Token usage: Badge style, `#00adb5` background
  - Latency: Badge style, `#533483` background
  - Model/provider: Badge style, `#6c757d` background
  - Badge padding: `4px 8px`
  - Badge border-radius: `4px`
  - Badge font-size: `0.75rem` (12px)
  - Badge font-weight: `600`
  - Display: Inline-flex with `8px` gap

**Performance Summary (US-017):**
- **Metrics table**:
  - Border: `1px solid #533483` (Grid Lines)
  - Border-radius: `8px`
  - Cell padding: `12px 16px`
  - Text alignment: Left for labels, right for numbers

- **Table header**:
  - Background: `#0f3460` (Card)
  - Font-weight: `600` (Semibold)
  - Color: `#ffffff` (Heading)
  - Border-bottom: `2px solid #533483`

- **Per-agent rows**:
  - Min-height: `48px`
  - Alternating backgrounds: `#16213e` and `transparent`
  - Border-bottom: `1px solid rgba(83, 52, 131, 0.3)`
  - Hover: Background `rgba(0, 173, 181, 0.1)`

- **Numeric values**:
  - Alignment: Right
  - Font-family: Monospace
  - Precision: 2 decimal places for times, whole numbers for counts
  - Color: `#00adb5` (Primary) for values

**Game Summary (US-018):**
- **Layout**: Grid layout, 2 columns
- Grid gap: `16px`
- Margin-bottom: `24px`

- **Summary cards**:
  - Background: `#0f3460` (Card)
  - Padding: `20px`
  - Border-radius: `12px`
  - Text-align: Center
  - Min-height: `120px`
  - Box-shadow: Elevation 1

- **Card icons**:
  - Size: `32px`
  - Margin-bottom: `12px`
  - Color: Varies by metric type

- **Outcome display** (Win/Loss/Draw):
  - Font-size: `2rem` (32px)
  - Font-weight: `700` (Bold)
  - Margin-bottom: `24px`
  - Text-align: Center
  - Padding: `20px`
  - Border-radius: `12px`
  - Win: Background `#06d6a0`, Color `#1a1a2e`
  - Loss: Background `#e94560`, Color `#ffffff`
  - Draw: Background `#533483`, Color `#ffffff`

### Configuration Panel

**User Stories:** US-019, US-020, US-021

**Visual Design:** `docs/ui/frames/config-panel.png`

**Layout:**
- Background: `#16213e` (Surface)
- Border-radius: `12px`
- Padding: `24px`
- Border: `1px solid #533483` (Grid Lines)
- Form layout with sections
- Section spacing: `24px`
- Max-width: `500px`

**Section Headers:**
- Font-size: `1.25rem` (20px)
- Font-weight: `600` (Semibold)
- Color: `#ffffff` (Heading)
- Margin-bottom: `16px`
- Border-bottom: `2px solid #533483`
- Padding-bottom: `8px`

**LLM Provider Selection (US-019):**
- **Dropdown (select)**:
  - Height: `44px`
  - Background: `#0f3460` (Card)
  - Border: `2px solid #533483` (Grid Lines)
  - Border-radius: `6px`
  - Padding: `12px 16px`
  - Font-size: `1rem` (16px)
  - Color: `#eaeaea` (Primary Text)
  - Cursor: `pointer`
  - Focus: Border-color `#00adb5` (Primary)
  - Options: OpenAI, Anthropic, Google Gemini, Ollama

- **Model name input**:
  - Height: `44px`
  - Background: `#0f3460` (Card)
  - Border: `2px solid #533483` (Grid Lines)
  - Border-radius: `6px`
  - Padding: `12px 16px`
  - Font-size: `1rem` (16px)
  - Color: `#eaeaea` (Primary Text)
  - Placeholder color: `#6c757d` (Disabled)
  - Focus: Border-color `#00adb5`, box-shadow `0 0 0 3px rgba(0, 173, 181, 0.2)`
  - Margin-top: `12px`

- **Save button**:
  - Background: `#00adb5` (Primary)
  - Color: `#1a1a2e` (Dark for contrast)
  - Padding: `12px 24px`
  - Border-radius: `6px`
  - Font-size: `1rem` (16px)
  - Font-weight: `600` (Semibold)
  - Border: `none`
  - Cursor: `pointer`
  - Margin-top: `16px`
  - Hover: Background `#00c4cf`, transform `translateY(-2px)`, box-shadow Elevation 2
  - Disabled: Background `#6c757d`, cursor `not-allowed`, opacity `0.6`

**Agent Mode Selection (US-020):**
- **Radio buttons**:
  - Size: `20px`
  - Color (unchecked): `#533483` (Grid Lines)
  - Color (checked): `#00adb5` (Primary)
  - Label font-size: `1rem` (16px)
  - Label margin-left: `10px`
  - Spacing between options: `16px`
  - Options: Local Mode, Distributed MCP Mode

- **Framework dropdown** (conditional):
  - Same style as LLM provider dropdown
  - Visible only when Distributed MCP Mode selected
  - Margin-top: `12px`
  - Padding-left: `24px` (indent)

**Game Settings (US-021):**
- **Reset button**:
  - Background: `#e94560` (Error)
  - Color: `#ffffff` (White)
  - Padding: `12px 24px`
  - Border-radius: `6px`
  - Font-size: `1rem` (16px)
  - Font-weight: `600` (Semibold)
  - Border: `none`
  - Cursor: `pointer`
  - Hover: Background `#ff5a75`, transform `translateY(-2px)`
  - Confirmation modal required before reset

- **Symbol selection** (X or O):
  - Toggle button group style
  - Each option width: `80px`, height: `44px`
  - Background (inactive): `#0f3460` (Card)
  - Background (active): `#00adb5` (Primary)
  - Color (inactive): `#a8a8a8` (Secondary Text)
  - Color (active): `#1a1a2e` (Dark)
  - Border-radius: `6px` (outer group)
  - Font-size: `1.5rem` (24px)
  - Font-weight: `700` (Bold)
  - Transition: `all 0.2s ease`

- **Difficulty slider** (optional):
  - Track height: `6px`
  - Track background: `#0f3460` (Card)
  - Track border-radius: `3px`
  - Thumb size: `20px`
  - Thumb background: `#00adb5` (Primary)
  - Thumb border: `2px solid #ffffff`
  - Range: Easy (1) to Hard (5)
  - Labels at min/max/mid
  - Label font-size: `0.875rem` (14px)
  - Label color: `#a8a8a8` (Secondary Text)

### Error States

**User Stories:** US-024, US-025

**Visual Design:** Error states are demonstrated across all frames as inline indicators

**Error UI Indications** (per spec.md Section 12 Failure Matrix):

**Critical Errors (Red Modal):**
- Modal width: `500px`, max-width: `90vw`
- Modal max-height: `80vh`
- Background: `#16213e` (Surface)
- Border: `2px solid #e94560` (Error)
- Border-radius: `16px`
- Padding: `32px`
- Box-shadow: Elevation 4
- Z-index: `1000`

- **Backdrop**:
  - Background: `rgba(26, 26, 46, 0.85)`
  - Backdrop-filter: `blur(4px)`
  - Z-index: `999`

- **Title**:
  - Font-size: `1.5rem` (24px)
  - Font-weight: `700` (Bold)
  - Color: `#e94560` (Error)
  - Margin-bottom: `16px`
  - Icon: ⛔ or ✗, size `32px`, inline before text

- **Message**:
  - Font-size: `1rem` (16px)
  - Color: `#eaeaea` (Primary Text)
  - Line-height: `1.5` (Normal)
  - Margin-bottom: `24px`

- **Acknowledge button**:
  - Background: `#e94560` (Error)
  - Color: `#ffffff` (White)
  - Padding: `12px 32px`
  - Border-radius: `6px`
  - Font-size: `1rem` (16px)
  - Font-weight: `600` (Semibold)
  - Width: `100%`
  - Hover: Background `#ff5a75`

**Error Banners (Red):**
- Position: Top of viewport (fixed)
- Width: `100%`
- Min-height: `60px`
- Background: `#e94560` (Error)
- Color: `#ffffff` (White)
- Padding: `16px 24px`
- Display: `flex`, align-items: `center`
- Box-shadow: Elevation 2
- Z-index: `900`

- **Close button**:
  - Position: Absolute right (`16px`)
  - Size: `32px`
  - Background: `transparent`
  - Color: `#ffffff`
  - Border: `none`
  - Font-size: `1.5rem` (24px)
  - Cursor: `pointer`
  - Hover: Background `rgba(255, 255, 255, 0.2)`

- **Icon**:
  - Size: `24px`
  - Position: Left, margin-right `12px`
  - Icon: ⚠ or ⛔

**Warning Indicators (Orange/Yellow):**
- Icon size: `20px`
- Icon: ⚠ (warning triangle)
- Color: `#ffd166` (Warning)

- **Badge style**:
  - Background: `rgba(255, 209, 102, 0.15)`
  - Border: `1px solid #ffd166`
  - Border-radius: `4px`
  - Padding: `4px 8px`
  - Font-size: `0.75rem` (12px)
  - Font-weight: `600`
  - Position: Inline or absolute top-right of component

**Info Notifications (Blue):**
- Toast position: Bottom-right corner
- Toast width: `320px`
- Toast min-height: `80px`
- Background: `#4361ee` (Agent Activity)
- Color: `#ffffff` (White)
- Padding: `16px`
- Border-radius: `8px`
- Box-shadow: Elevation 3
- Margin: `16px` from edges
- Auto-dismiss duration: 7 seconds
- Animation: `slideInRight 0.3s ease-out`, `fadeOut 0.3s ease-in` on dismiss
- Z-index: `800`

- **Icon**:
  - Size: `24px`
  - Position: Left, margin-right `12px`
  - Icon: ℹ (info circle)

**Cell-Level Errors:**
- **Shake animation**:
  - Duration: `400ms`
  - Amplitude: `10px` (translateX)
  - Keyframes: `0% (0), 25% (-10px), 50% (10px), 75% (-10px), 100% (0)`
  - Easing: `ease-in-out`
  - Iterations: 1

- **Pulse animation**:
  - Duration: `300ms`
  - Scale: `0.95` to `1.05` to `1.0`
  - Easing: `ease-in-out`

- **Red highlight**:
  - Border-color: `#e94560` (Error)
  - Box-shadow: `0 0 12px rgba(233, 69, 96, 0.6)`
  - Duration: `500ms` then fade back to normal

**Retry/Fallback Indicators:**
- **Countdown timer**:
  - Font-family: Monospace
  - Font-size: `0.875rem` (14px)
  - Color: `#ffd166` (Warning)
  - Font-weight: `600`
  - Position: Inline after message
  - Format: `(15s remaining)`

- **Progress bar**:
  - Height: `4px`
  - Background: `#0f3460` (Card)
  - Fill color: `#ffd166` (Warning)
  - Border-radius: `2px`
  - Animation: Countdown (100% to 0%)
  - Duration: Matches timeout period
  - Position: Below message

- **Fallback message**:
  - Background: `rgba(255, 209, 102, 0.15)`
  - Border-left: `3px solid #ffd166`
  - Padding: `12px`
  - Border-radius: `6px`
  - Font-size: `0.875rem` (14px)
  - Icon: ⚠, size `16px`, color `#ffd166`

## Animations

### Move Animations

**Player Move:**
- **Symbol appearance**:
  - Animation: `scaleIn` (scale from 0 to 1)
  - Duration: `200ms`
  - Easing: `cubic-bezier(0.34, 1.56, 0.64, 1)` (slight bounce)
  - Transform-origin: `center`

- **Cell state change**:
  - Transition: `all 0.2s ease`
  - Background color transition
  - Border color transition

**AI Move:**
- **Move execution**:
  - Pre-animation: Cell pulses with `#00adb5` glow for `300ms`
  - Symbol appearance: Same as player move but with `250ms` duration
  - Post-animation: Brief highlight fade over `400ms`

- **Board update**:
  - Transition timing: `0.3s ease-out`
  - Stagger effect: Each cell updates with `50ms` delay

**Last Move Indicator:**
- **Highlight effect**:
  - Animation: `pulse` (opacity and scale)
  - Duration: `1.5s`
  - Keyframes: `0% (opacity 1, scale 1) → 50% (opacity 0.7, scale 1.02) → 100% (opacity 1, scale 1)`
  - Easing: `ease-in-out`
  - Iterations: `infinite`
  - Box-shadow pulses between normal and glow state

### Loading Animations

**Agent Thinking:**
- **Spinner**:
  - Type: Circular border spinner
  - Size: `24px`
  - Border-width: `3px`
  - Color: `#4361ee` (Agent Activity)
  - Animation: `spin 0.8s linear infinite`
  - Keyframes: `0% (rotate 0deg) → 100% (rotate 360deg)`

- **Pulse effect**:
  - Duration: `1.5s`
  - Opacity: `1.0` to `0.4` to `1.0`
  - Easing: `ease-in-out`
  - Iterations: `infinite`
  - Applied to status indicator dot

- **Progress bar**:
  - Animation: Indeterminate slide
  - Duration: `1.5s`
  - Width: `40%` of container
  - Movement: Slides left to right continuously
  - Easing: `cubic-bezier(0.65, 0.815, 0.735, 0.395)`

**Processing States:**
- **0-2s**: Simple spinner (details above)
- **2-5s**: Spinner + text with fade-in (`0.3s`)
- **5-10s**: Progress bar with elapsed time counter (updates every `100ms`)
- **10-15s**: Warning pulse animation on border (`1s` cycle) + countdown

### Error Animations

**Invalid Move:**
- **Shake**:
  - Amplitude: `10px` horizontal
  - Duration: `400ms`
  - Keyframes: `0% (0), 10% (-10px), 20% (10px), 30% (-10px), 40% (10px), 50% (-5px), 60% (5px), 100% (0)`
  - Easing: `ease-in-out`
  - Iterations: 1

- **Flash**:
  - Border-color: `#e94560` (Error)
  - Background: `rgba(233, 69, 96, 0.2)`
  - Duration: `300ms`
  - Keyframes: `0% (normal) → 50% (error colors) → 100% (normal)`
  - Easing: `ease-in-out`

**Agent Failure:**
- **Error icon bounce**:
  - Duration: `500ms`
  - Keyframes: `0% (translateY 0) → 30% (translateY -8px) → 50% (translateY 0) → 70% (translateY -4px) → 100% (translateY 0)`
  - Easing: `cubic-bezier(0.36, 0, 0.66, -0.56)`
  - Iterations: 1

- **Fade to fallback state**:
  - Duration: `600ms`
  - Opacity transition: `1.0` to `0.5` to `1.0`
  - Background change: Animate to fallback colors
  - Easing: `ease-in-out`

### State Transitions

**Game Over:**
- **Board fade/lock**:
  - Duration: `400ms`
  - Opacity: `1.0` to `0.6`
  - Pointer-events: `none`
  - Easing: `ease-out`

- **Winner announcement**:
  - Animation: `slideDown` from top
  - Duration: `500ms`
  - Distance: `20px` translateY
  - Easing: `cubic-bezier(0.34, 1.56, 0.64, 1)` (bounce)
  - Opacity: `0` to `1` simultaneously

- **Metrics panel reveal**:
  - Animation: `fadeIn` and `slideUp`
  - Duration: `600ms`
  - Distance: `30px` translateY
  - Easing: `ease-out`
  - Delay: `200ms` after game over

**Mode Switch:**
- **Configuration change**:
  - Fade duration: `300ms`
  - Cross-fade old and new content
  - Easing: `ease-in-out`

- **Agent reinitialization**:
  - Loading indicator: Same as agent thinking spinner
  - Overlay: `rgba(26, 26, 46, 0.7)` with backdrop-filter `blur(2px)`
  - Duration: While agents initialize
  - Text: "Reinitializing agents..." with fade-in after `2s`

## Responsive Behavior

**Breakpoints:**
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Layout Adjustments:**
- Mobile: Single column, stacked panels
- Tablet: Two columns, side-by-side panels
- Desktop: Three columns, full metrics panel

## Accessibility

**Color Contrast:**
- All text must meet WCAG AA standards (4.5:1 for normal text)

**Keyboard Navigation:**
- Tab order: Board cells → Action buttons → Configuration
- Enter/Space to select cell
- Escape to close modals

**Screen Reader Support:**
- ARIA labels for all interactive elements
- Live regions for game state changes
- Alt text for all icons

**Focus Indicators:**
- **Visible focus ring**:
  - Color: `#00adb5` (Primary)
  - Width: `3px`
  - Offset: `2px` (outline-offset)
  - Style: `solid`
  - Border-radius: Matches element

- **Focus animation**:
  - Type: Fade-in pulse
  - Duration: `200ms`
  - Easing: `ease-out`
  - Pulse effect: Slight scale (`1.02`) on focus

## Implementation Notes

**CSS Framework:**
- Recommended: CSS Modules or Vanilla CSS with CSS Variables
- Alternative: Styled Components for React-based implementations
- Avoid: Tailwind (prefer semantic styling for this design system)
- CSS Variables defined for all color, spacing, and typography values in `:root`

**Icon Library:**
- Recommended: Custom SVG icons for primary UI elements
- Alternative: Lucide Icons or Heroicons for clean, modern appearance
- Avoid: Font Awesome (licensing and weight concerns)
- Icon format: SVG with `currentColor` for flexible theming
- Icon sizes: `16px`, `20px`, `24px`, `32px` (consistent scale)

**Animation Library:**
- Recommended: CSS animations and transitions (sufficient for all specs)
- Alternative: Framer Motion for React (if complex gesture interactions needed)
- Avoid: GSAP (overkill for this application)
- All animations defined with `@keyframes` in CSS
- Use `prefers-reduced-motion` media query to respect user preferences:
  ```css
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```

**Performance Considerations:**
- Use `transform` and `opacity` for animations (GPU-accelerated)
- Avoid animating `width`, `height`, `top`, `left` properties
- Use `will-change` sparingly for critical animations
- Debounce resize handlers for responsive behavior
- Lazy load post-game metrics components

**Browser Support:**
- Target: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- CSS Grid and Flexbox for layouts
- CSS Custom Properties (Variables) for theming
- No IE11 support required

**Code Organization:**
- Separate CSS files for: Reset, Variables, Typography, Components, Animations, Utilities
- BEM naming convention recommended: `.component__element--modifier`
- Component-scoped styles preferred over global styles

## Design Reference

An interactive HTML preview demonstrating the complete design system is available at [game-board-preview.html](./game-board-preview.html).

**Preview Features:**
- Complete color palette application
- Typography hierarchy with SF Pro Display
- Component layouts and interactions
- Hover states and animations
- Agent status indicators with live states
- Expandable move history
- Interactive game board

This preview serves as the visual design reference for implementation and can be opened directly in any browser.

**Optional PNG Frames:**
If static design frames are needed, they can be exported from Figma and placed in `docs/ui/frames/`:
- ⬜ `game-board.png` - Game board and move history panel
- ⬜ `metrics-panel.png` - Agent insights and post-game metrics panel
- ⬜ `config-panel.png` - Configuration panel

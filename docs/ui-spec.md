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
- [To be extracted from Figma frames]

**Status Colors:**
- Success: [Color]
- Warning: [Color]
- Error: [Color]
- Info: [Color]

**Game Colors:**
- Player X: [Color]
- Player O: [Color]
- Empty Cell: [Color]
- Board Background: [Color]

**Agent Status Colors:**
- Scout: [Color]
- Strategist: [Color]
- Executor: [Color]
- Idle: [Color]
- Running: [Color]
- Success: [Color]
- Failed: [Color]

### Typography

**Font Family:**
- Primary: [Font name]
- Monospace (for metrics): [Font name]

**Font Sizes:**
- Heading 1: [Size]
- Heading 2: [Size]
- Body: [Size]
- Caption: [Size]
- Code/Metrics: [Size]

**Font Weights:**
- Regular: [Weight]
- Medium: [Weight]
- Bold: [Weight]

### Spacing

**Grid System:**
- Base unit: [Pixels]
- Gutter: [Pixels]

**Component Spacing:**
- Small: [Pixels]
- Medium: [Pixels]
- Large: [Pixels]

### Border Radius

- Small (buttons, inputs): [Pixels]
- Medium (cards, panels): [Pixels]
- Large (modals): [Pixels]
- Board cells: [Pixels]

### Shadows

- Card shadow: [CSS shadow value]
- Button shadow: [CSS shadow value]
- Modal shadow: [CSS shadow value]

## Component Specifications

### Game Board Panel

**User Stories:** US-001, US-002, US-003, US-004, US-005

**Visual Design:** `docs/ui/frames/game-board.png`

**Layout:**
- 3x3 grid with equal cell sizes
- Cell dimensions: [Width x Height]
- Gap between cells: [Pixels]
- Board container padding: [Pixels]

**Cell States:**
- Empty: [Background color, border style]
- Occupied (X): [Symbol style, color]
- Occupied (O): [Symbol style, color]
- Hover (empty cell): [Background color, cursor]
- Disabled (AI turn): [Opacity, cursor]
- Last move: [Border/highlight style]

**Game Status Display:**
- Current turn indicator: [Position, style]
- Move count: [Position, style]
- Game over message: [Position, style, animation]
- Winner announcement: [Position, style, animation]

**Interactions:**
- Click empty cell: [Visual feedback]
- Invalid click: [Shake animation, error feedback]
- Disabled board: [Overlay or opacity change]

### Move History Panel

**User Stories:** US-006, US-007

**Visual Design:** `docs/ui/frames/game-board.png` (included in same panel as game board)

**Layout:**
- Scrollable list adjacent to or below game board
- Move entry height: [Pixels]
- Max visible entries: [Number]

**Move Entry:**
- Player indicator: [Icon, color]
- Move number: [Style, position]
- Position: [Format, e.g., "row 1, col 2"]
- Timestamp: [Format, e.g., "10:30:45"]

**Expandable Details:**
- Expansion indicator: [Icon, e.g., chevron]
- Expanded state: [Background change, animation]
- Agent reasoning: [Text style, indentation]

### Agent Insights and Metrics Panel

**User Stories:** US-008 through US-018

**Visual Design:** `docs/ui/frames/metrics-panel.png` (combined panel for insights and metrics)

**Layout:**
- Combined panel showing agent insights during game and post-game metrics
- Adapts based on game state (in progress vs completed)

#### Agent Insights Section (US-008 through US-012)

**During Game:**
- Three agent sections (Scout, Strategist, Executor)
- Agent section height: [Pixels]
- Spacing between sections: [Pixels]

**Agent Status Indicators:**
- Idle: [Icon, color]
- Running: [Icon, color, animation]
- Success: [Icon, color]
- Failed: [Icon, color]

**Processing Status (US-010):**
- 0-2s: Basic spinner [Style, size, color]
- 2-5s: Processing message [Style]
- 5-10s: Progress bar [Style, color]
- 10-15s: Warning indicator [Style, color]
- 15s+: Fallback message [Style, color]

**Agent Output Display:**
- Analysis text: [Style, max lines, truncation]
- Threats/Opportunities: [List style, icons]
- Recommended move: [Highlight style]

**Action Buttons:**
- Force Fallback button (after 10s): [Style, position]
- Retry button (on failure): [Style, position]

#### Post-Game Metrics Section (US-013 through US-018)

**User Stories:** US-013, US-014, US-015, US-016, US-017, US-018

**Visibility:**
- Hidden during game
- Visible only when `is_game_over = true`

**Layout:**
- Tabbed interface: Agent Communication | LLM Interactions | Performance | Configuration
- Tab height: [Pixels]
- Content padding: [Pixels]

**Agent Communication Tab (US-014):**
- Request/Response pairs
- Collapsible sections
- JSON syntax highlighting: [Color scheme]

**LLM Interactions Tab (US-015):**
- Per-agent LLM call logs
- Prompt text: [Style, max height, scroll]
- Response text: [Style, max height, scroll]
- Token usage: [Display format]
- Latency: [Display format]
- Model/provider: [Display format]

**Performance Summary (US-017):**
- Metrics table: [Border, padding, alignment]
- Per-agent rows: [Height, alternating colors]
- Numeric values: [Alignment, precision]

**Game Summary (US-018):**
- Summary cards: [Layout, size]
- Icons for metrics: [Size, color]
- Large outcome display (Win/Loss/Draw): [Style]

### Configuration Panel

**User Stories:** US-019, US-020, US-021

**Visual Design:** `docs/ui/frames/config-panel.png`

**Layout:**
- Form layout with sections
- Section spacing: [Pixels]

**LLM Provider Selection (US-019):**
- Dropdown style: [Height, border, padding]
- Provider options: OpenAI, Anthropic, Google Gemini, Ollama
- Model name input: [Style]
- Save button: [Style, position]

**Agent Mode Selection (US-020):**
- Radio buttons or toggle: [Style]
- Options: Local Mode, Distributed MCP Mode
- Framework selection: [Dropdown style]

**Game Settings (US-021):**
- Reset button: [Style, color]
- Symbol selection: [Radio or toggle style]
- Difficulty slider (optional): [Style, range]

### Error States

**User Stories:** US-024, US-025

**Visual Design:** Error states are demonstrated across all frames as inline indicators

**Error UI Indications** (per spec.md Section 12 Failure Matrix):

**Critical Errors (Red Modal):**
- Modal dimensions: [Width, height]
- Backdrop: [Color, opacity]
- Title: [Style, icon]
- Message: [Style]
- Acknowledge button: [Style]

**Error Banners (Red):**
- Position: [Top/bottom]
- Height: [Pixels]
- Close button: [Position, style]
- Icon: [Size, position]

**Warning Indicators (Orange/Yellow):**
- Icon size: [Pixels]
- Badge style: [Background, border]
- Position: [Relative to component]

**Info Notifications (Blue):**
- Toast position: [Corner]
- Toast dimensions: [Width, height]
- Auto-dismiss duration: 5-10 seconds
- Animation: [Fade in/out]

**Cell-Level Errors:**
- Shake animation: [Duration, amplitude]
- Pulse animation: [Duration, scale]
- Red highlight: [Color, duration]

**Retry/Fallback Indicators:**
- Countdown timer: [Style, position]
- Progress bar: [Style, color, animation]
- Fallback message: [Style, icon]

## Animations

### Move Animations

**Player Move:**
- Symbol appearance: [Animation type, duration]
- Cell state change: [Transition duration]

**AI Move:**
- Move execution: [Animation type, duration]
- Board update: [Transition timing]

**Last Move Indicator:**
- Highlight effect: [Animation type, duration, loop]

### Loading Animations

**Agent Thinking:**
- Spinner: [Type, size, speed]
- Pulse effect: [Duration, intensity]
- Progress bar: [Animation type, speed]

**Processing States:**
- 0-2s: Simple spinner
- 2-5s: Spinner + text
- 5-10s: Progress bar + elapsed time
- 10-15s: Warning pulse + countdown

### Error Animations

**Invalid Move:**
- Shake: [Amplitude, duration, easing]
- Flash: [Color, duration]

**Agent Failure:**
- Error icon bounce: [Duration, easing]
- Fade to fallback state: [Duration]

### State Transitions

**Game Over:**
- Board fade/lock: [Duration, opacity]
- Winner announcement: [Slide/fade in, duration]
- Metrics panel reveal: [Animation type, duration]

**Mode Switch:**
- Configuration change: [Fade duration]
- Agent reinitialization: [Loading indicator]

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
- Visible focus ring: [Color, width, offset]
- Focus animation: [Type, duration]

## Implementation Notes

**CSS Framework:**
- [To be determined: Tailwind, CSS Modules, Styled Components, etc.]

**Icon Library:**
- [To be determined: Font Awesome, Material Icons, custom SVG, etc.]

**Animation Library:**
- [To be determined: CSS animations, Framer Motion, GSAP, etc.]

## Frame Files

The following PNG frames have been exported from Figma and placed in `docs/ui/frames/`:
- ✅ `game-board.png` - Game board and move history panel
- ✅ `metrics-panel.png` - Agent insights and post-game metrics panel
- ✅ `config-panel.png` - Configuration panel

**Next Steps:**
Update this document with extracted design specifications:
1. Color values from frames (primary, status, game, agent colors)
2. Font specifications (family, sizes, weights)
3. Spacing and sizing measurements (grid, padding, component dimensions)
4. Border radius values
5. Shadow specifications
6. Animation parameters
7. Any additional visual details visible in frames

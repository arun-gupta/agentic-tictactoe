# UI Visual Design Specification

## Overview

This document defines the visual design for the Tic-Tac-Toe Multi-Agent Game UI. It complements the functional requirements in [spec.md Section 6](./spec.md#6-web-ui-functional-requirements) by providing visual specifications, layouts, styling, and animations.

## Figma Design Integration

### Figma File Reference

**Primary Figma File**: [Tic-Tac-Toe Multi-Agent Game Design](https://www.figma.com/design/mhNp0FKIqT0mSBP8qKKvbi/Tic-Tac-Toe?node-id=2-510)

**Key Design Frames**:
- **Board** (node-id: 1:2770) - Game board with 3x3 grid, menu bar with tabs, status text, and New Game button
- **Board Win** (node-id: 1:2463) - Win state with highlighted winning cells (green background)
- **Board Lost** (node-id: 1:2639) - Loss state display
- **Config** (node-id: 1:2239) - Configuration panel with agent LLM selection and API key inputs
- **Metrics** (node-id: 1:2259) - Post-game metrics display (cost, tokens, latency, duration, moves)
- **Components** (section: 2:507) - shadcn component library (Tabs, Button, Select, Input, Field states)

**Component Library (shadcn/ui)**:
This implementation **requires shadcn/ui** as the component library. All UI components are based on shadcn:
- **Tabs**: https://ui.shadcn.com/docs/components/tabs
- **Button**: https://ui.shadcn.com/docs/components/button
- **Select**: https://ui.shadcn.com/docs/components/select
- **Input**: https://ui.shadcn.com/docs/components/input

**Access Requirements**:
- Designers: Full edit access
- Developers: View-only access (comment permissions recommended)
- Stakeholders: View-only access via share link

**File Organization**:
- **Section: Second Variation Design + UI Kit** (node-id: 2:510) - Main design section
- **Components Shadcn+UPD** (section: 2:507) - Reusable shadcn-based UI components
- **Field States**: Default, Win, Lost, Hover, Focus variants for game cells

### Design Frames

Visual designs are provided as exported PNG frames from Figma, located in `docs/ui/frames/`.

**Frame Index:**
- `game-board.png` - Game board and move history panel (US-001 through US-007)
  - **Figma Frame**: `US-001-Game-Board` (Page: Game Board)
  - Game board: 3x3 grid with cell states and game status (US-001, US-002, US-003, US-004, US-005)
  - Move history: Chronological move list in same panel (US-006, US-007)
- `metrics-panel.png` - Agent insights and post-game metrics panel (US-008 through US-018)
  - **Figma Frame**: `US-008-Metrics-Panel` (Page: Metrics)
  - Agent insights: Real-time agent status and analysis (US-008, US-009, US-010, US-011, US-012)
  - Post-game metrics: Performance data and LLM interactions (US-013, US-014, US-015, US-016, US-017, US-018)
- `config-panel.png` - Configuration panel (US-019, US-020, US-021)
  - **Figma Frame**: `US-019-Config-Panel` (Page: Configuration)
  - LLM provider and model selection (US-019)
  - Agent mode configuration (US-020)
  - Game settings (US-021)

**Frame Export Requirements**:
- Format: PNG @2x resolution (for high-DPI displays)
- Export settings: Include "id" in filename (e.g., `game-board-US-001.png`)
- Export location: `docs/ui/frames/` directory
- Naming convention: `{component-name}-{user-story-id}.png`

### Design Tokens Export

**Figma Variables/Design Tokens**:
Design tokens (colors, typography, spacing, shadows, etc.) MUST be exported from Figma and synchronized with code.

**Export Methods**:

1. **Figma Tokens Plugin** (Recommended):
   - Install [Figma Tokens](https://www.figma.com/community/plugin/843461159747178946/Figma-Tokens) plugin
   - Export tokens as JSON: `docs/ui/design-tokens.json`
   - Generate CSS variables: `docs/ui/tokens.css`
   - Auto-sync with codebase on design updates

2. **Style Dictionary**:
   - Use [Style Dictionary](https://amzn.github.io/style-dictionary/) to transform Figma tokens
   - Generate platform-specific outputs (CSS, SCSS, JavaScript, etc.)
   - Output location: `src/styles/tokens/`

3. **Manual Export**:
   - Export color palette, typography, spacing from Figma Variables
   - Document in `docs/ui/design-tokens.md`
   - Update CSS variables in code manually

**Token Categories**:
- **Colors**: Primary, secondary, semantic (success, error, warning), game-specific (X, O)
- **Typography**: Font families, sizes, weights, line heights
- **Spacing**: Base unit (4px or 8px), scale (0.5x, 1x, 2x, 3x, 4x)
- **Shadows**: Elevation levels (0-5)
- **Border Radius**: Component-specific radius values
- **Animations**: Duration, easing functions, keyframes

**Token Sync Workflow**:
1. Designer updates tokens in Figma Variables
2. Export tokens using Figma Tokens plugin
3. Commit `design-tokens.json` to repository
4. CI/CD pipeline generates CSS/SCSS from tokens
5. Developers pull updated tokens automatically

### Component Specifications

**Figma Component Links**:
Each UI component in Figma MUST be linked to its specification in this document.

**Component Mapping**:
- **Game Board Cell**: Figma component `Cell` → [Component Specifications: Game Board Panel](#component-specifications)
- **Agent Status Indicator**: Figma component `AgentStatus` → [Component Specifications: Agent Insights Panel](#component-specifications)
- **Move History Item**: Figma component `MoveHistoryItem` → [Component Specifications: Move History](#component-specifications)
- **Configuration Panel**: Figma component `ConfigPanel` → [Component Specifications: Configuration Panel](#component-specifications)

**Component Properties**:
- **Variants**: Document all component variants (states: default, hover, active, disabled, error)
- **Auto Layout**: Use Figma Auto Layout for responsive behavior
- **Constraints**: Document responsive constraints (left, right, top, bottom, center, scale)
- **Component Properties**: Document all Figma component properties (boolean, text, instance swap)

### Design-to-Code Workflow

**1. Design Handoff Process**:
- Designer marks frames as "Ready for Development" in Figma
- Designer adds comments with implementation notes
- Designer exports assets (icons, images) to `docs/ui/assets/`
- Developer reviews Figma file and comments
- Developer implements component matching Figma specifications

**2. Design Review Process**:
- Developer implements component based on Figma
- Developer creates PR with screenshots comparing implementation vs Figma
- Designer reviews PR and approves or requests changes
- Designer can use Figma Dev Mode to inspect implementation

**3. Design Updates**:
- Designer updates Figma file
- Designer exports updated frames to `docs/ui/frames/`
- Designer updates design tokens if changed
- Designer notifies team via issue/PR comment
- Developer updates implementation to match new design

**4. Version Control**:
- **Figma File Versions**: Use Figma version history for design iterations
- **Code Versions**: Git commits reference Figma file version/URL
- **Design Tokens**: Versioned in `design-tokens.json` with changelog
- **Frame Exports**: Commit PNG frames to repository for historical reference

### Figma Dev Mode Integration

**For Developers**:
- Use Figma Dev Mode to inspect spacing, colors, typography, and CSS properties
- Copy CSS/React code snippets directly from Figma
- View component specifications and constraints
- Access design tokens and variables

**Best Practices**:
- Always reference Figma frame when implementing new components
- Use Figma measurements for spacing and sizing (avoid guessing)
- Verify color values match Figma (use color picker tool)
- Check responsive behavior matches Figma constraints

### Design System Maintenance

**Design System Updates**:
- Changes to design system MUST be documented in Figma file changelog
- Design system updates MUST trigger design token export
- Breaking changes MUST be communicated to development team
- Design system version MUST be tracked (e.g., `v1.0.0`)

**Design System Components**:
- All reusable components MUST be in Figma component library
- Component variants MUST cover all states (default, hover, active, disabled, error, loading)
- Component documentation MUST include usage guidelines and code examples

## Design System

**IMPORTANT**: This design uses **shadcn/ui** components with their default zinc color palette and styling. The design follows a clean, light theme aesthetic.

### Color Palette (Zinc-based Light Theme)

**Base Colors (shadcn CSS Variables):**
- `--background`: `#f4f4f5` (zinc-100) - Main background
- `--foreground`: `#09090b` (zinc-950) - Primary text
- `--accent`: `#f4f4f5` (zinc-100) - Accent background / `#27272a` (zinc-800) - Active tab text
- `--muted-foreground`: `#a1a1aa` (zinc-400) - Placeholder text, muted content
- `--secondary-foreground`: `#3f3f46` (zinc-700) - Secondary text, labels
- `--border`: `#d4d4d8` (zinc-300) - Component borders
- `--ring`: `#a1a1aa` (zinc-400) - Focus rings, inactive elements / `#71717a` (zinc-500) - Inactive tabs
- `--sidebar-accent-foreground`: `#fafafa` (zinc-50) - Active tab background
- `--ring-offset`: `#ffffff` (white) - Button backgrounds

**Game State Colors:**
- Win Cell Background: `#bbf7d0` (green-200) - Winning cells highlight
- Loss Cell Background: `#fecaca` (red-200) - Losing cells highlight (if needed)
- Player X Text: `#3f3f46` (zinc-700) - X symbol color
- Player O Text: `#3f3f46` (zinc-700) - O symbol color

**Shadows:**
- `shadow-xs`: `0px 1px 2px rgba(0,0,0,0.05)` - Inputs, selects
- `shadow-sm`: `0px 1px 3px rgba(0,0,0,0.1), 0px 1px 2px rgba(0,0,0,0.1)` - Active tabs
- Board shadow: `0px 4px 4px rgba(0,0,0,0.25)` - Main board container

### Typography

**Font Family:**
- Primary: `'JetBrains Mono Quattro', monospace` - All UI text (monospace aesthetic)
- Fallback: `'JetBrains Mono', 'SF Mono', 'Monaco', 'Menlo', monospace`

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

## Application Layout

The UI is organized into three main tabs using the shadcn Tabs component. The entire application fits within a 640x640px container.

### Main Tab Navigation (shadcn Tabs)

**Three-Tab Structure:**

1. **Board Tab** (Default view)
   - 3x3 game grid centered in the container (298x298px play area)
   - Menu bar at top with: Tabs, Status text, "New Game" button
   - Move history text at bottom of container
   - Status text shows: "Game Started", "Win", "Lost", etc.

2. **Config Tab**
   - Agent LLM selection: Three Select dropdowns for Scout, Strategist, Executor
   - API key inputs for each provider:
     - OpenAI (model: GPT-5 mini) - API key input
     - Anthropic (model: Claude Opus 4.5) - API key input
     - Gemini (model: Gemini 3 Flash) - API key input
   - Clean form layout with labels and model names displayed

3. **Metrics Tab**
   - Read-only metric inputs showing post-game data:
     - Total cost ($)
     - Tokens (count)
     - Latency (ms)
     - Duration (ms)
     - Total moves

**Tab Bar Specifications (shadcn Tabs):**
- Component: `shadcn/ui Tabs` (https://ui.shadcn.com/docs/components/tabs)
- Position: Top-left of container (20px from edges)
- Tab container: Border `1px solid #d4d4d8`, border-radius `4px`
- Tab button padding: `16px horizontal, 8px vertical`
- Tab font-size: `12px` (text-xs in shadcn)
- Tab font-family: `JetBrains Mono Quattro`
- Inactive tab: Text color `#71717a` (zinc-500) or `#a1a1aa` (zinc-400)
- Active tab: Background `#fafafa`, text color `#27272a`, shadow-sm
- Tab trigger border-radius: `4px`

**Menu Bar Layout (Board Tab):**
- Height: `32px`
- Width: `600px` (within 640px container, 20px padding each side)
- Position: `top: 20px, left: 20px`
- Layout: `display: flex, justify-content: space-between, align-items: center`
- Elements (left to right):
  - Tabs component (Board | Config | Metrics)
  - Status text (e.g., "Status: Game Started")
  - "New Game" button (shadcn Button, secondary variant)

**Container Specifications:**
- Board container: `640px × 640px`
- Background: `#f4f4f5` (zinc-100)
- Shadow: `0px 4px 4px rgba(0,0,0,0.25)`

**Layout Behavior:**
- Board tab shows game grid centered with move history at bottom
- Config tab shows form fields for LLM configuration
- Metrics tab shows read-only metric displays
- Switching tabs preserves game state

## Component Specifications

### Game Board Panel

**User Stories:** US-001, US-002, US-003, US-004, US-005

**Visual Design:** Figma node-id: 1:2770 (Board), 1:2463 (Board Win), 1:2639 (Board Lost)

**Layout:**
- 3x3 grid centered in container (Play Area)
- Cell dimensions: `100px × 100px`
- Play Area dimensions: `298px × 298px` (centered in 640px container)
- Gap between cells: `-1px` (cells share borders, creating grid lines)
- Container background: `#f4f4f5` (zinc-100)
- Container dimensions: `640px × 640px`
- Container shadow: `0px 4px 4px rgba(0,0,0,0.25)`

**Cell States (Field Component):**
- **Empty/Default**:
  - Background: transparent (inherits container background)
  - Border: `1px solid #3f3f46` (zinc-700)
  - Border-radius: `8px` on corners (tl for top-left, tr for top-right, bl for bottom-left, br for bottom-right)
  - Cursor: `pointer`
  - Font-size: Large (symbols fill cell)

- **Occupied (X)**:
  - Text: "x" (lowercase in design)
  - Color: `#3f3f46` (zinc-700)
  - Font-family: `JetBrains Mono Quattro`
  - Font-size: `98px` (fills cell)
  - Text-align: center
  - Cursor: `default`

- **Occupied (O)**:
  - Text: "o" (lowercase in design)
  - Color: `#3f3f46` (zinc-700)
  - Font-family: `JetBrains Mono Quattro`
  - Font-size: `98px` (fills cell)
  - Text-align: center
  - Cursor: `default`

- **Hover (empty cell)**:
  - Border-color: Slightly darker
  - Cursor: `pointer`
  - Transition: `all 0.2s ease`

- **Focus**:
  - Outline for accessibility
  - Cursor: `pointer`

- **Disabled (AI turn)**:
  - Opacity: `0.6`
  - Cursor: `not-allowed`
  - Pointer-events: `none`

- **Win state (winning cells)**:
  - Background: `#bbf7d0` (green-200) - Light green highlight
  - Border: maintains original border
  - Animation: subtle highlight

- **Lost state (losing indicator)**:
  - Background: `#fecaca` (red-200) - Light red highlight (if needed)

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

**Visual Design:** Figma node-id: 1:2239 (Config)

**Layout:**
- Container: `640px × 640px` (same as board)
- Background: `#f4f4f5` (zinc-100)
- Shadow: `0px 4px 4px rgba(0,0,0,0.25)`
- Content padding: `20px` from edges
- Form layout with vertical sections

**Tab Navigation:**
- Same Tabs component as Board tab (Board | Config | Metrics)
- "Config" tab is active (highlighted)

**Agent LLM Selection (shadcn Select):**

Three Select dropdowns in a row for assigning LLMs to each agent:

- **Scout Select**:
  - Label: "Scout"
  - Label color: `#3f3f46` (zinc-700)
  - Label font-size: `14px`
  - Component: shadcn Select (https://ui.shadcn.com/docs/components/select)
  - Trigger height: `36px`
  - Trigger border: `1px solid #a1a1aa` (zinc-400)
  - Trigger border-radius: `4px`
  - Trigger padding: `12px horizontal, 8px vertical`
  - Trigger shadow: `shadow-xs`
  - Default value: "LLMs"
  - Dropdown icon: Chevron down

- **Strategist Select**: Same styling as Scout

- **Executor Select**: Same styling as Scout

- Layout: `display: flex, gap: 20px`
- Position: `top: 112px, left: 20px`
- Total width: `601px`

**API Key Inputs (shadcn Input):**

Three Input sections for API keys, each with provider label and model name:

- **OpenAI Input**:
  - Position: `top: 236px`
  - Label row: "OpenAI" (zinc-700) + "GPT-5 mini" (zinc-400)
  - Component: shadcn Input (https://ui.shadcn.com/docs/components/input)
  - Input height: `36px`
  - Input width: `600px`
  - Input background: `#f4f4f5` (zinc-100)
  - Input border: `1px solid #a1a1aa` (zinc-400)
  - Input border-radius: `4px`
  - Input shadow: `shadow-xs`
  - Placeholder: "OpenAI Key"
  - Placeholder color: `#a1a1aa` (zinc-400)

- **Anthropic Input**:
  - Position: `top: 320px`
  - Label row: "Anthropic" (zinc-700) + "Claude Opus 4.5" (zinc-400)
  - Placeholder: "Anthropic Key"

- **Gemini Input**:
  - Position: `top: 404px`
  - Label row: "Gemini" (zinc-700) + "Gemini 3 Flash" (zinc-400)
  - Placeholder: "Gemini Key"

**Input Label Styling:**
- Layout: `display: flex, gap: 4px, align-items: center`
- Provider name: Font-size `14px`, color `#3f3f46` (zinc-700)
- Model name: Font-size `14px`, color `#a1a1aa` (zinc-400)
- Gap between label and input: `8px`

**Game Settings (US-021):**
- "New Game" button on Board tab handles game reset
- Symbol selection and difficulty can be added as additional Select components if needed

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

**UI Component Library (REQUIRED):**
- **Required**: [shadcn/ui](https://ui.shadcn.com/) - This design is built on shadcn components
- **Setup**: `npx shadcn@latest init` then add required components
- **Required components**:
  - `npx shadcn@latest add tabs` - Main navigation
  - `npx shadcn@latest add button` - New Game button
  - `npx shadcn@latest add select` - Agent LLM selection
  - `npx shadcn@latest add input` - API key inputs

**CSS Framework:**
- Recommended: Tailwind CSS (comes with shadcn/ui)
- shadcn/ui uses CSS Variables for theming (zinc color palette)
- All design tokens accessible via shadcn CSS variables (--background, --foreground, etc.)
- Custom CSS for game board cells (not covered by shadcn components)

**Font Setup:**
- Primary: JetBrains Mono Quattro (monospace)
- Include via Google Fonts or local font files
- Example: `@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap')`

**Icon Library:**
- Recommended: Lucide Icons (included with shadcn/ui)
- Chevron icons for Select dropdowns (built into shadcn Select)
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

---
name: Cognitive Lead Console
colors:
  background: "#0B0E14"
  surface: "#141A23"
  surfaceRaised: "#1B2430"
  border: "#263141"
  text: "#E6EBF2"
  textMuted: "#8C99AB"
  accent: "#5EEAD4"
  accentInk: "#04211D"
  success: "#34D399"
  warning: "#FBBF24"
  danger: "#F87171"
  info: "#7DD3FC"
---

# Design System: Cognitive Lead Console

## 1. Visual Theme & Atmosphere

A quiet instrument panel. The interface is dark, flat, and deliberately low-chroma: near-black slate surfaces, hairline borders, and a single mint accent that only appears where action or state lives. Nothing glows, nothing floats; depth comes from one step of surface lightness, never from stacked shadows. The mood is a terminal that learned typography — precise, calm, and dense enough to show 330 tasks without the page turning into a wall.

Density is a feature, not an accident. Rows are 32px, the grid is 8px, and vertical rhythm is tight because the reader is scanning status, not reading prose. Mono type carries every identifier, path, byte count, and diff line, so machine data is visually separable from human text at a glance. The result should feel like a tool built by someone who reads their own logs.

## 2. Color Palette & Roles

Semantic tokens only. Components never hard-code hex; they reference these names.

### Primary Foundation

- **Void** `#0B0E14` (`--bg`) — page background, input backgrounds, code blocks.
- **Panel** `#141A23` (`--surface`) — cards, lanes, modal body, table headers.
- **Panel Raised** `#1B2430` (`--surface-raised`) — hover, sticky headers over scroll, secondary buttons.
- **Hairline** `#263141` (`--border`) — every 1px border and divider. No other border color exists.

### Accent & Interactive

- **Signal Mint** `#5EEAD4` (`--accent`) — primary action, focus ring, active tab underline, selected state. One accent, used sparingly.
- **Ink on Mint** `#04211D` (`--accent-ink`) — text and icons sitting on the accent fill.

### Typography & Text Hierarchy

- **Chalk** `#E6EBF2` (`--text`) — primary text.
- **Ash** `#8C99AB` (`--text-muted`) — labels, metadata, counts, placeholders.

### Functional States

- **Pass** `#34D399` (`--success`) — QA passed, closed, healthy.
- **Hold** `#FBBF24` (`--warning`) — pending review, quota near, truncated output.
- **Break** `#F87171` (`--danger`) — rejected, forbidden, destructive.
- **Note** `#7DD3FC` (`--info`) — in-progress, neutral notice.

State colors appear as text and 1px borders on a 10% tint of themselves, never as a saturated fill.

## 3. Typography Rules

### Hierarchy & Weights

- **UI family:** `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.
- **Data family:** `"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` — ids, paths, diffs, counts, timestamps, code.
- **Display 28px / 700 / -0.02em** — page title only (`Planner`, `Prompt Composer`).
- **Section 20px / 600 / -0.01em** — section headers.
- **Body 14px / 400 / 1.45** — default text.
- **Body Small 13px / 400** — table cells, lane rows.
- **Label 11px / 600 / 0.06em uppercase** — table headers, lane headers, field labels.
- **Mono 12.5px / 400** — identifiers, hashes, diff lines.

Weights are 400, 500, 600, 700 only. No 800+, no italics except empty-state copy.

### Spacing Principles

Line-height is 1.2 for ≥20px headings and 1.45 for body, never both on the same element. Letter-spacing tightens with size (negative above 20px) and opens on 11px labels. Paragraphs inside task bodies get 6px above and below; list items 2px. Text never sits closer than 4px to a border.

## 4. Component Stylings

### Implementation baseline — Bootstrap 5.3 (vendored)

Both surfaces load `vendor/bootstrap.min.css` and `theme.css` from their own directory. No CDN, no build step, no node toolchain. `theme.css` maps the palette above onto Bootstrap's variables (`--bs-body-bg`, `--bs-border-color`, `--bs-primary`, `--bs-border-radius*`, `--bs-focus-ring-color`, `--bs-font-monospace`) and adds the few primitives Bootstrap lacks: `.chip`, `.page`, `.label`, `.gd-dialog`, `.mono`. Components below therefore name the Bootstrap class where one exists; only what Bootstrap has no equivalent for is a thin custom layer on the same tokens. A screen that needs a class outside this set is a design change, not an implementation detail.

### Buttons

- `btn btn-primary` — accent fill, ink text, radius 6, height 32 (`btn-sm` inside cards).
- `btn btn-outline-secondary` — hairline border, transparent fill, hover raises the surface.
- `btn btn-outline-danger` — danger text and border, 12% danger fill on hover only.
- Ghost actions are `btn btn-outline-secondary` without a fill; text links carry no underline until hover.
- Transitions 120ms `ease-out` on background, border, color; `btn` never transforms.

### Cards & Lanes

- Radius 8px, 1px `--border`, `--surface` fill, 16px padding, no shadow.
- Lane card header: 11px uppercase label, count in mono inside a radius-4 chip on `--surface-raised`.
- Lane body scrolls internally: `max-height: calc(100vh - 280px)`, sticky header painted on `--surface` (opaque, never translucent) with 1px bottom border.
- Task row: 32px, 13px, hover `--surface-raised`, focus ring 2px `--accent` offset 1px, border-bottom `--border`. Identifier in mono, weight 600.

### Navigation

- Top bar: `--bg`, 1px bottom border, 56px tall, title 20px/600, status chip right-aligned.
- Tabs: 32px, 13px/500, active = `--text` with 2px `--accent` underline; inactive `--text-muted`, hover `--text`.
- Project switcher: select styled as a secondary button; never a native-looking control.

### Inputs & Forms

- `form-control` / `form-select` on the page background, 1px border, radius 6px, 13px mono for long-text surfaces and 14px sans for short fields.
- Focus: 3px accent ring at 35% (`--bs-focus-ring-color`), no layout shift.
- Labels use `.form-label` (12px muted); placeholders are muted. Errors are 12px danger text under the field.
- Textareas are resizable vertically only.

### Domain-Specific Components

- **Preset chips (Composer):** radius 6px, 1px `--border`, `--surface-raised`; each preset may carry its semantic tint at 10% background with matching text, but chips never use rainbow pastels — at most four tints (info, success, warning, danger) plus neutral.
- **Diff block (Planner modal):** `--bg` panel, 1px `--border`, mono 12.5px, `+` lines `--success` at 12% background, `-` lines `--danger` at 12%, hunk headers `--info`. Horizontal scroll, never wrap.
- **Status chip:** 11px/600 uppercase, 1px border, text color = state, background = 10% of state.
- **Task modal:** radius 12px, `--surface`, max width 1000px, 92vh ceiling, overlay `rgba(4,7,12,0.72)`, sticky header with title 16px/600 and a mono id·lane meta line.

## 5. Layout Principles

### Grid & Structure

- 8px base grid; 4px allowed only for icon-to-text gaps.
- Planner content width 1200px, Composer 960px, both centered with 24px page padding (16px under 640px).
- Lane grid: `repeat(auto-fit, minmax(240px, 1fr))`, gap 16px.
- Sections separated by 24px, subsections by 12px. Dividers are 1px `--border`, never shadows.

### Whitespace Strategy

Dense but breathable: 16px card padding, 8px between rows, 12px between a label and its control. Page top padding 24px, bottom 32px. Empty states get 20px vertical padding and italic `--text-muted` text.

### Alignment & Visual Balance

Text is left-aligned; numeric columns are right-aligned with tabular figures. Labels sit above controls, never beside them on narrow widths. Icons are 16px, stroke 1.5, optically centered — no decorative illustration.

### Responsive Behavior & Touch

Collapse lane grid to a single column under 720px; lane max-height becomes 60vh there. Minimum touch target 44px on coarse pointers (buttons grow, row height stays 40px). Focus rings must remain visible on dark and light OS themes. Honor `prefers-reduced-motion`: transitions off, state changes instant.

## 6. Design System Notes for Stitch Generation

### Language to Use

"Dark slate instrument panel, near-black background, flat surfaces separated by hairline borders, one mint accent used only for action and focus, mono type for identifiers and diffs, dense 32px rows, no shadows except the modal, no gradients, no rainbow chips."

### Color References

- Background: Void `#0B0E14`; panels: `#141A23`; raised: `#1B2430`; borders: `#263141`.
- Text: `#E6EBF2`; muted `#8C99AB`; accent `#5EEAD4` with ink `#04211D`.
- States: success `#34D399`, warning `#FBBF24`, danger `#F87171`, info `#7DD3FC`.

### Component Prompts

- "A kanban lane card on near-black slate: 8px radius, 1px #263141 border, uppercase 11px label with a mono count chip, sticky opaque header, 32px task rows with mono ids, hover lifting the surface one step, no shadow."
- "A full-screen task modal: 12px radius, #141A23 surface, dimmed #04070C overlay, mono meta line id·lane, rendered markdown body, diff lines tinted green and red at low opacity, close button as ghost."
- "A composer form: stacked labelled textareas with 6px radius, one mint primary button, neutral chips with at most four semantic tints, generated markdown pane in mono on the darkest surface."

### Incremental Iteration

Change one token at a time and re-render both surfaces. If a screen needs a color that is not in the palette, the screen is wrong, not the palette. Keep the accent for a single purpose per screen; when two actions compete, the secondary becomes ghost.

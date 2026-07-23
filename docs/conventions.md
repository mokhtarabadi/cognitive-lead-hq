# Conventions

This document defines syntax rules, naming conventions, file boundaries, and automation patterns for the Cognitive Lead AI multi-agent system HQ.

## GitHub CLI Automation

All `gh` commands that send body content MUST use `--body-file` with a temp Markdown file, never inline `--body`.

### Rationale

Inline `--body "..."` in `gh issue create` is fragile:

| Problem             | Example                                               |
| ------------------- | ----------------------------------------------------- |
| Shell escaping      | Backticks, `$`, `"` inside the body break the command |
| Truncation          | Long bodies get silently cut off                      |
| Markdown corruption | Newlines, `#`, `---` can break shell parsing          |
| No preview          | You can't verify what will actually be sent           |

Using `--body-file /tmp/gh-issue-body.md` guarantees precise, verbatim delivery of the full Markdown content.

### Standard Pattern

```bash
cat > /tmp/gh-issue-body.md << 'EOF'
## Title
Full Markdown content here — safe from shell escaping.
EOF

gh issue create \
  --title "Issue Title" \
  --body-file /tmp/gh-issue-body.md \
  --label "some-label"

rm -f /tmp/gh-issue-body.md
```

### Rules

- Use single-quoted `'EOF'` delimiter to prevent shell variable expansion.
- Always include `rm -f /tmp/gh-issue-body.md` cleanup after the `gh` command.
- This applies to all files: SKILL.md templates, task files, and scripts.

## Universal DateTime Standard

All projects in this ecosystem MUST follow these datetime rules:

1. **UTC at Rest** — All databases and caches store datetimes in UTC with `TIMESTAMP WITH TIME ZONE`. Banned: naive or local-time storage.
2. **ISO-8601 with Offset / Epoch ms at API Boundaries** — APIs transmit datetimes as Unix Epoch milliseconds (int64) or ISO-8601 with offset (e.g., `2026-07-23T14:30:00+00:00`). Banned: timezone-naive strings.
3. **Clock Injection** — All current-time access must go through an injectable `Clock` abstraction. Banned: direct `new Date()`, `datetime.now()`, `time.Now()` in business logic.
4. **Dual-Representation for Future Events** — Calendar events expose both `event_start_local` (with timezone) and `event_start_epoch_ms` (absolute).
5. **`TZ=UTC` Infrastructure** — All environments run with `TZ=UTC`. Timezone display is a client-layer responsibility only.

## SOLID Programming Guidelines

Enforce these SOLID principles and pragmatic guardrails in every implementation:

1. **SRP** — One reason to change per module. Split merged concerns.
2. **OCP** — Open for extension, closed for modification. Use composition over inheritance.
3. **LSP** — Subtypes must be substitutable. Ban `NotImplementedError` overrides.
4. **ISP** — Small role-specific interfaces. Ban monolithic god-interfaces.
5. **DIP** — Depend on abstractions, not concretions. Core layer must not import adapters.

**Pragmatic Guardrails:** No abstraction for <3 trivial operations. Only extract interfaces with 2+ implementations. Apply YAGNI strictly. Prefer simpler designs unless a measurable requirement forces complexity.

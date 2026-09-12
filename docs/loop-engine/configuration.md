# Loop Engine Configuration — Token Optimization Evidence

> Verified spike measurements (token-optimization R&D spike).
> Date: 2026-09-12. Tool: RTK 0.49.0 (x86_64-unknown-linux-musl, local eval
> binary in `/tmp`; no global install, no `rtk init -g`).
> Byte/line counts are the hard evidence; token equivalents assume ~4 chars/token.

## Verified savings (this repo, decision-server suite, 232 tests at measure time)

| Command | Raw | Via RTK | Reduction | Exit code | Source |
| ------- | --- | ------- | --------- | --------- | ------ |
| `pytest tests/ -q` (232 passed) | 1801 bytes / 21 lines | 44 bytes / 3 lines | **97.6% bytes** | preserved (0) | local measurement, passing suite |
| `git status --short` (32 lines) | 1589 bytes | 1621 bytes | −2% (overhead) | n/a | local measurement |
| `git log --oneline -15` | 1218 bytes | 1696 bytes | −39% (overhead) | n/a | local measurement |
| `git diff --stat HEAD` | 1952 bytes | 1951 bytes | ~0% | n/a | local measurement |
| `rtk git diff` (2-file sample) | 5297 bytes / 48 lines | 5204 bytes / 51 lines | ~2% (reformat) | n/a | local measurement |

`rtk gain` self-report for the eval session: 11 commands, 1.9K tokens saved
(41.0% blended — dominated by the test-runner wins; tool self-report, not
independently verified).

## Recommendation

- **Adopt Option A (RTK wrapper) for passing-suite/test output** in agent
  guidance (see `docs/opencode-shell-strategy.md` §8). Zero repo code changes.
  Scope warning: failing-suite output is UNMEASURED — collapsing failures
  could hide tracebacks, so keep full output on any failure.
- **Defer Option B (Headroom proxy):** `headroom-ai` 0.37.0 verified present
  on PyPI, but proxy eval requires localhost proxy + provider URL rewiring
  in `loop-engine/loop-engine.jsonc` — follow-up task, needs manager approval.
- **Defer Caveman Pixel Mode:** `@caveman-ai/cli` 1.3.3 verified on npm;
  image-based skill loading needs multimodal-provider validation — follow-up.
- **Do NOT run `rtk init -g --opencode`** without explicit manager approval
  (rewrites global OpenCode command routing).

## Caveats discovered

1. `rtk diff` shells out to `/usr/bin/diff` — it is file comparison, not git.
   Use `rtk git diff` for condensed git diffs.
2. `rtk test` joins args into an unquoted shell string: version specs with
   `<` (e.g. `--with "mcp<2"`) break as input redirection. Exact-pin
   (`--with mcp==1.30.0`) works. Known-good pin for this repo's suite:
   `mcp==1.30.0` + `pathspec` + `pyyaml` (older 1.9.4 breaks brain-bridge
   FastMCP registration at collection).

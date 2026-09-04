# Task 148: Production Daemon Deployment (Systemd & Docker Compose)

**File:** `tasks/backlog/148-production-deployment-and-systemd.md`
**Source:** orchestrator
**Type:** feature
**Status:** open

## Goal

Create production deployment configurations including a hardened `Dockerfile`, `docker-compose.yml`, and `cognitive-loop.service` systemd unit file with automatic restart, healthcheck probes, and log rotation for running the loop engine 24/7 on remote servers.

## Local TODOs

- [ ] Initial codebase exploration (daemon entry point, dependencies, environment variables)
- [ ] Create deploy/Dockerfile with multi-stage build
- [ ] Create deploy/docker-compose.yml with healthcheck
- [ ] Create deploy/cognitive-loop.service systemd template with log rotation
- [ ] Implement healthcheck probe endpoint / CLI verification
- [ ] Document in docs/loop-engine/deployment.md
- [ ] Verify full test suite passes

## Acceptance Criteria

- [ ] `deploy/docker-compose.yml` and `Dockerfile` with multi-stage build.
- [ ] `deploy/cognitive-loop.service` systemd service template.
- [ ] Healthcheck probe endpoint / CLI verification.
- [ ] Documentation in `docs/loop-engine/deployment.md`.
- [ ] Full test suite passes with 0 failures.

## Verification Evidence

- **Test command:** `python -m pytest loop-engine/ -q` and `docker compose -f deploy/docker-compose.yml config`
- **Expected result:** all tests pass, 0 failures; compose file validates
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Systemd/Docker configs may reference environment variables that differ per host.
- **Rollback plan:** Document all required env vars and provide a `.env.example`; keep the daemon runnable without containers.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
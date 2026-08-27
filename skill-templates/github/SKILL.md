---
name: github
description: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
---

# GitHub CLI (gh) Workflow SOP

## Purpose

Standardizes GitHub operations through the official GitHub CLI (`gh`). This skill is the canonical reference for all GitHub CLI workflows in the Cognitive Lead AI multi-agent system — pull request triage, issue management, CI/CD run analysis, and API queries.

## Prerequisites

Verify the `gh` CLI is installed and authenticated before any GitHub operation:

```bash
gh --version
gh auth status
```

If `gh` is not installed, install via the official method (see `docs/setup.md`). If not authenticated, run `gh auth login`.

## Issue Management

### List Issues

```bash
gh issue list --repo owner/repo
gh issue list --repo owner/repo --state open --limit 20
gh issue list --repo owner/repo --label "bug" --json number,title,labels
```

### View an Issue

```bash
gh issue view 123 --repo owner/repo
gh issue view 123 --repo owner/repo --comments
```

### Create an Issue (MANDATORY `--body-file`)

**CRITICAL:** Always use `--body-file` with a temp Markdown file — NEVER inline `--body "..."`. Inline bodies are fragile (shell escaping, truncation, Markdown corruption). See `docs/conventions.md` for the full rationale.

```bash
cat > /tmp/gh-issue-body.md << 'EOF'
## Title
Full Markdown content here — safe from shell escaping.
EOF

gh issue create \
  --title "Issue Title" \
  --body-file /tmp/gh-issue-body.md \
  --label "bug"

rm -f /tmp/gh-issue-body.md
```

## Pull Request Review & Status

```bash
gh pr view 55 --repo owner/repo
gh pr diff 55 --repo owner/repo
gh pr checks 55 --repo owner/repo
gh pr comments 55 --repo owner/repo
gh pr list --repo owner/repo --state open
```

## CI/CD Workflow & Log Triage

```bash
gh run list --repo owner/repo --limit 10
gh run view <run-id> --repo owner/repo
gh run view <run-id> --repo owner/repo --log-failed
```

### Debugging a CI Failure

1. **Check PR status** — identify which checks are failing: `gh pr checks 55 --repo owner/repo`
2. **List recent runs** — find the relevant run ID: `gh run list --repo owner/repo --limit 10`
3. **View the failed run** — see which jobs and steps failed: `gh run view <run-id> --repo owner/repo`
4. **Fetch failure logs** — get the detailed output for failed steps: `gh run view <run-id> --repo owner/repo --log-failed`

## GitHub API & Structured Output

The `gh api` command accesses data not available through other subcommands:

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

Most commands support `--json` for structured output, filterable with `--jq`:

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

## ZAC Guardrails (STRICTLY FORBIDDEN for Autonomous Agents)

The following operations are **STRICTLY FORBIDDEN** for autonomous agent execution and remain **Manager-owned**:

- `gh release create` — creating GitHub releases
- `git push` — pushing to remote
- `git tag` — creating tags

These operations are denied at the permission layer (Zero-Autonomous-Commit / ZAC). The agent MUST NOT execute them. If a release or tag is required, the Manager executes it manually after task closure.

## Self-Management with `gh skill`

The `gh skill` command (GitHub CLI v2.98.0+) manages Agent Skills:

```bash
gh skill search <query>
gh skill preview <owner>/<repo> <skill-name>
gh skill install <owner>/<repo> <skill-name> --agent <host> --pin <ref>
gh skill update --all
```

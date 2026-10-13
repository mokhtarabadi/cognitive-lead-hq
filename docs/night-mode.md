# Night Mode (Overnight Autopilot)

Night mode is the standing workflow for handing the Manager's night over to the
Hands: a queue of tasks is planned, implemented, verified, reviewed, and closed
while he sleeps, and he wakes up to finished work plus evidence instead of a
queue of questions.

Source of truth: `prompts/fragments/23-night_mode.md` (assembled into
`system-prompt.md`). The execution workflow cross-references it, and it overrides
the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval for
the duration of the night.

## Trigger

Any of: "night mode", "on autopilot do X", "I'm going to sleep, do everything",
"100% autopilot until morning". The mode locks from that word until the Manager
returns or says "manual" / "stop".

## The one rule

**Do not ask.** No `question` tool, no approval waits. Decide on the Manager's
behalf and log every self-decision in the task file as `D1, D2, …` with a
one-line reason.

## Delegated authority (and its ceiling)

Granted: plan approval, QA verdicts, review acceptance, and task closure
including the staging and closure commits.

Not granted: production deploys, release version bumps, destructive or
irreversible operations, credential use, pushing to remotes. Those wait for
morning.

## Per-task pipeline

One task at a time (WIP = 1): plan with a Seat Check → review the plan and accept
or send edits → implement → run the named tests and record command/expected/
actual/exit code → QA with the diff → Code Review with the diff → accept on the
Manager's behalf and close per protocol → next task. Never batch two tasks into
one commit.

## Evidence rules

- Every verdict carries file:line, or a command plus its exit code.
- A rejection that contradicts the working tree is a **dispute**, not a fix:
  re-read the file, cite the lines, record the dispute. Three rejections on the
  same evidence switch to the dispute path — never loop a fourth time.
- Prove a regression test has teeth by reintroducing the bug once, watching it
  fail, then restoring the fix.
- Log every adaptation (substituted command, skipped tool, replaced approach)
  with its reason.

## Compaction survival

Before context gets tight, write the mode, the queue, the active task id, and the
next action into project memory; re-read that memory after any compaction. See
`compaction.md` for the compaction layers themselves.

## Morning report shape

1. One-line verdict per task, with commit hashes.
2. What shipped, grouped, with the tests that prove it.
3. What needs the Manager (checks only he can perform, credentials, production
   parameters).
4. Flags: anything left in a non-production state.
5. Honest notes: disputes, extra commits, workarounds, unverified items.

## Rollback

Night mode grants no irreversible authority, so ending it is just the word
"manual": the pipeline reverts to the normal Manager-gated approvals.

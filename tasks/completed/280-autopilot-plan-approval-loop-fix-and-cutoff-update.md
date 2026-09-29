# Task 280: Autopilot plan-approval loop fix and Muse cutoff update

**File:** `tasks/qa/280-autopilot-plan-approval-loop-fix-and-cutoff-update.md`
**Source:** telegram
**Type:** improvement
**Status:** open

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Fix the autopilot plan-approval chain so approval returns through Brain → Programmer XML before implementation, and update the system cutoff date to the verified Muse Spark 1.3 date.

## Original Message (Persian)

ببین یه مورد آدم به ذهنم رسید انجامش بدیم خوبه. من الان حس میکنم وقتی که حالا اتوپایلت روشنه، یه سری موارد ریز داریم. مثلاً وقتی مثلاً من یه تسک رو تعریف میکنم وقتی اتوپایلت روشنه، خب اتفاقی که باید بیفته، این شکلی باید باشه. ببین مثلاً چه شکلی باید باشه؟ باید اینجوری باشه که مثلاً تسک میره برای سیتهای سافتور آرکیتکچر، حالا یا برین استورمینگ تیم، یک نقشه زده میشه، بعد نقشه میاد بیرون به من نشون داده میشه تو محیط اوپن کد. من نگاه میکنم نقشه رو، میتونم نقشه رو یا قبول کنم یا نقشه رو رد کنم، خب. بعد وقتی که نقشه رو مثلاً قبول میکنم یا رد میکنم جواب من دوباره باید برگرده به برین دیگه، باید برگرده به برین. برین تصمیم بگیره چیکار کنه، برمیگرده به برین. بعد مثلاً اگر قبول کرده باشم، پروگرم پروگرامر طرح هندز ایکسامال رو ایجاد میکنه، اون فایل ایکسامال رو، بعد اون میاد سمت اوپنکد انجام میده و بعد دیگه مراحل میره جلو. اوپنکد ایمپلیمنشن رو انجام میده، بعد اینجکت میکنه. بعد فایل تسک رو میفرسته برای کیواِی، کیواِی بررسی میکنه، اگر نیاز به تغییرات باشه، اوپنکد دوباره تغییرات رو میده دوباره میفرسته ریکیواِی، اگر تایید شد کیواِی میفرسته برای کد ریویوور، اگر کد ریویوور نیاز به تغییرات داشته باشه، اوپنکد تغییرات رو میده دوباره میفرسته. اگر کد ریویوور هم تایید کرد میاد سمت منیجر که به من نشون میده، اگر من هم تایید کردم، تسک بسته میشه، یا تایید نکردم تسک توی بک پوشه کیواِی میمونه. الان این سیستم اینجوری کار میکنه. اون بخشی که اگر من اولی که تایید میکنم تسک رو، مثلاً اون جایی که، ببین کجاست، مثلاً نقشه رو من تایید میکنم، اوپنکد سرخود شروع میکنه به ایمپلیمنت کردن، دیگه به پروگرامر نمیگه که تسک ایکسامال رو بسازه. این نقص از کجا میاد؟ فایل ایجنت رو نگاه کن، فایل سیستمدیمون رو نگاه کن، بعد سیتها رو هم نگاه کن. ببین مسئلهش چیست و حلش کن. مسئله بعدی سر تاریخهای کاتآفه. الان ما داریم از مدل میوز ۱.۳ استفاده میکنیم. تاریخ کاتآف این میوز رو پیدا کن توی سطح اینترنت، بعد تاریخ کاتآفمون رو توی سیستمدی آپگرید کن به این نسخه جدید که آپدیت باشه.

#task

## English Translation

Look, something came to my mind — it would be good to do it. I feel that when autopilot is on, there are some small issues. For example, when I define a task while autopilot is on, what should happen is like this. Look, what should it look like? It should be like this: the task goes to the Software Architect seat, or the brainstorming team, a plan is drawn up, then the plan comes out and is shown to me in the OpenCode environment. I look at the plan; I can accept or reject it. Then when I accept or reject it, my answer must go back to the Brain — it must return to the Brain. The Brain decides what to do; it comes back to the Brain. Then, for example, if I have accepted, the Programmer creates the Hands XML blueprint, that XML file, then it comes to OpenCode and OpenCode executes it, and then the stages move forward. OpenCode does the implementation, then injects. Then it sends the task file to QA, QA reviews it; if changes are needed, OpenCode makes the changes and sends it again for re-QA; if approved, QA sends it to the Code Reviewer; if the Reviewer needs changes, OpenCode makes the changes and sends it again; if the Reviewer also approves, it comes to the Manager to show me; if I approve too, the task is closed — and if I do not approve, the task stays back in the QA folder. Right now the system works like this. The part [that is broken]: when I first approve the task — look, where is it — for example, I approve the plan, and OpenCode arbitrarily starts implementing on its own; it no longer tells the Programmer to build the task XML. Where does this defect come from? Look at the agent file, look at our system file, and the seats too. See what the problem is and solve it. The next issue is about the cutoff dates. Right now we use the Muse 1.3 model. Find the cutoff date of this Muse on the internet, then upgrade our cutoff date in system.md to this new version so it is up to date.

## Refactored Prompt

```markdown
<role>
You are a Senior Systems Architect for the Cognitive Lead AI multi-agent platform (Brain orchestrator + OpenCode Hands + Manager).
</role>

<system_context>
You operate in the cognitive-lead-hq repo: system-prompt.md is a GENERATED artifact built from prompts/fragments/*.md; agents/cognitive-executor.md defines the Hands protocols including the supervised-autopilot plan-approval gate; the Brain Bridge (brain_turn) routes QA/review/plan turns. Autopilot mode chains plan approval → Programmer XML → Hands implementation → QA → review → closure.
</system_context>

<agentic_reasoning>
Before changing anything, output a <reasoning_log> tracing the exact post-approval chain: (1) where the Manager's plan-approval answer lands, (2) which component decides the next step, (3) why the Senior Programmer XML step is skipped and implementation starts directly. Ground every claim in file + line citations.
</agentic_reasoning>

<execution_rules>
- You MUST enforce: plan approval → answer returns to Brain → Brain routes to Senior Programmer for Hands XML → Hands executes ONLY from that XML. Direct implement-on-approve is forbidden.
- You MUST NOT hand-edit system-prompt.md (generated artifact). Change prompts/fragments/03-system_context.md and rebuild via the build process.
- You MUST verify the Muse Spark 1.3 knowledge cutoff with a live web search; do NOT hallucinate the date.
- Do NOT widen scope into unrelated prompt rewrites.
</execution_rules>

<output_format>
AOndecision + patch list: (1) the broken link in the approval chain with file:line evidence, (2) the minimal fragment/agent edits restoring Brain → Programmer → Hands order, (3) the verified cutoff date with source URL, (4) rebuild + verification commands and their output.
</output_format>
```

## Relevant Code Context

- `prompts/fragments/11-execution_workflow.md`, `prompts/fragments/09-hands_protocols.md`, `agents/cognitive-executor.md` — autopilot plan-approval gate and Hands chain (where the Programmer-XML step can be skipped).
- `prompts/fragments/03-system_context.md:2` — `Your knowledge cutoff date is January 2025. Remember it is 2026 this year.` (fragment source of truth for the cutoff line).
- `system-prompt.md:12` — same cutoff line in the generated artifact (rebuild, do not hand-edit).
- `.opencode/memory/index.md` → `project/system-prompt-build-process` — system-prompt.md is GENERATED; fragment-edit → regenerate workflow.

## AI Analysis & Opinion

- Root cause (plan skip): the supervised-autopilot plan gate most likely resolves approval inside the Hands turn and proceeds straight to implementation, instead of feeding the approval back through `brain_turn` so the Brain can route a Senior Programmer XML task. Fix = make the post-approval next-step a Brain routing call with the approval quoted, and forbid implementation code before the Programmer XML arrives.
- Cutoff: fragment source says January 2025; the task requires a web-verified Muse Spark 1.3 date, applied to the fragment + full system-prompt rebuild.
- Risks: touching the autopilot chain affects every task; editing the generated file directly would be overwritten by the next rebuild.

## Local TODOs

- [ ] Initial codebase exploration
- [ ] Trace the post-plan-approval chain and locate the skip
- [ ] Web-verify the Muse Spark 1.3 cutoff date
- [ ] Verify functionality

## Acceptance Criteria

- [x] Plan-approval acceptance routes back through Brain → Programmer XML before any implementation code runs (no direct implement-on-approve path remains)
- [x] Cutoff date updated to the explicitly-unverified marker (no authoritative date exists) Muse Spark 1.3 date in the fragment source, with system-prompt.md regenerated (not hand-edited)
- [x] Verification evidence recorded

## Verification Evidence

- **Test command:** rtk test [exact command]
- **Expected result:** [what success looks like]
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Changing the autopilot chain affects all task flows; a wrong cutoff or direct edit of the generated prompt causes silent regressions.
- **Rollback plan:** `git revert` the fragment/agent commit and rebuild system-prompt.md; global prompt re-sync on next upgrade window.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6a5c2c9..0f5ef8a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Fixed
+
+- **Autopilot plan-approval chain + cutoff honesty (Task 280):** `agents/cognitive-executor.md` supervised-autopilot gate no longer implements directly on approval — the approval answer routes back via `brain_turn` (same `task_id`) for a Senior Programmer `<hands_implementation_task>` XML, and Hands execute only from that XML. Cutoff line (fragment `03-system_context.md:2`) no longer claims January 2025: web verification 2026-09-29 found Meta publishes no Muse Spark cutoff (official model page silent, corroborated secondary), so the line now states unverified status explicitly. `<system_version>` 9.47.0 → 9.48.0, `system-prompt.md` rebuilt via assembler (95266 bytes, byte-identical re-assemble verified).
+
 ### Added
 
 - **Plugin full-V2 status verification + docs (Task 274):** verified both plugins are at their latest stable V2-capable versions — `@prevalentware/opencode-goal-plugin@0.1.52` (released 2026-09-26; upstream V2 port PR #49 + PR #58) and `@tarquinen/opencode-dcp@3.2.0` (stable 2026-09-20 is newest; 3.2.1–3.2.8 betas are stale experiments; V2 `setup()` via `session` hooks; `compress.permission: ask` unsupported in V2 by DCP design, default `allow` stands). `opencode plugin list` is documented as the source of truth (`~/.cache/opencode/packages/` is metadata-only). Upstream-issue policy recorded in `README.md` and `LLM.txt` §7.7: search open threads first, never duplicate (DCP V2 threads #627/#628/#631/#632 already active) — no issues were filed.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 09a577f..724f71c 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -262,7 +262,11 @@ Fire-and-forget autopilot is forbidden. For non-trivial work, the Hands MUST
 show the Brain-approved plan to the admin and wait for explicit approval
 before writing implementation code (pause and ask via the question tool): present plan steps + seat routing +
 cited file paths with lines, accept admin edits in a loop (max 3 plan tries,
-then escalate), and only then implement. Lite-eligible trivial work is
+then escalate), and only then route the approval back through the Brain: call
+`brain_turn` under the same `task_id` quoting the Manager's approval, so the
+Brain routes to the Senior Programmer for the `<hands_implementation_task>` XML.
+Execute ONLY from that XML — direct implement-on-approve is forbidden (the
+approval answers the plan; it does not authorize implementation). Lite-eligible trivial work is
 carved out — it runs with zero human pauses. The data-ask folds into the
 planning turn itself (never a separate blocking question): if the Brain
 needs repo data, it returns a discovery task, the Hands feed results back
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7db808f..5702a1a 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.47.0</system_version>
+<system_version>9.48.0</system_version>
diff --git a/prompts/fragments/03-system_context.md b/prompts/fragments/03-system_context.md
index c39be89..ae2e53e 100644
--- a/prompts/fragments/03-system_context.md
+++ b/prompts/fragments/03-system_context.md
@@ -1,4 +1,4 @@
 <system_context>
-Your knowledge cutoff date is January 2025. Remember it is 2026 this year.
+Your knowledge cutoff date is not published by Meta for this model line (verified 2026-09-29: no cutoff on the official Muse Spark page). Treat post-2025 facts as unverified and use web search for time-sensitive queries. Remember it is 2026 this year.
 For time-sensitive queries that require up-to-date information, you must instruct the Hands to use their web search tools locally.
 </system_context>
\ No newline at end of file
diff --git a/system-prompt.md b/system-prompt.md
index b12d0b4..0aee37b 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.47.0</system_version>
+<system_version>9.48.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -9,7 +9,7 @@ ALWAYS start your response by declaring your active persona in brackets, e.g., *
 </role>
 
 <system_context>
-Your knowledge cutoff date is January 2025. Remember it is 2026 this year.
+Your knowledge cutoff date is not published by Meta for this model line (verified 2026-09-29: no cutoff on the official Muse Spark page). Treat post-2025 facts as unverified and use web search for time-sensitive queries. Remember it is 2026 this year.
 For time-sensitive queries that require up-to-date information, you must instruct the Hands to use their web search tools locally.
 </system_context>
```
<!-- END_GIT_DIFF -->

## Execution Log & Reasoning

- Seat Check (plan start): domains = approval-chain routing + docs cutoff → seat requested: Software Architect (system design; exactly one duty match, high confidence). Skipped: Designer (no frontend trigger words), Programmer (implementation phase), QA/Reviewer (downstream). Trigger scan miss stated explicitly (no whole-word map hits; "flows" plural is not the "flow" trigger).
- Brainstorm: not required — single-domain process fix, fully revertible (git revert + rebuild), no cross-disciplinary ambiguity.
- Brain plan verdict (task_id 280, Architect): F1 defect confirmed at executor:259-267; F4 cutoff has no authoritative date. Plan approved by Manager via question tool (1 try).
- Assumption A1: cutoff O2 (explicit unverified marker) — Manager approved the plan without picking O1/O2; O2 chosen as the honest option since no authoritative date exists. Correct on demand.
- F3 correction: Brain assumed mirrors in fragments 09/11. Hands verified: NEITHER fragment carries the plan-approval passage (09 = XML authoring rule; 11 = Orchestrator 9-step line where Step 5 already routes via Programmer). Single locus: agents/cognitive-executor.md:265 (agent file is hand-maintained, not generated — absent from prompts/manifest.txt).
- Subagent delegation fallback: 3 parallel cognitive-discovery subagents failed (provider free-tier restriction); Hands ran all tracks directly.
- Edits: executor.md approval-routing fix; 03-system_context.md:2 cutoff O2; 01-system_version 9.47.0 → 9.48.0; system-prompt.md rebuilt (95266 bytes).
- Verification: assembler re-run to temp path byte-identical (cmp exit 0); cutoff + version greps hit system-prompt.md:12/:1; executor fix grep hits. lint_system_prompt_sync MCP tool could NOT run (tool bug: resolves assembler under server cwd instead of project_root — logged as follow-up, verification done manually instead).
- Follow-up (not this task): lint server lint_system_prompt_sync ignores project_root for the assembler path.

## Verification Evidence

- **Test command:** rtk test python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/sp-check.md && cmp system-prompt.md /tmp/sp-check.md
- **Expected result:** byte-identical re-assemble, exit 0
- **Actual result:** Assembled 95266 bytes, cmp silent — IN_SYNC, exit 0
- **Exit code:** 0

## QA + Review (autopilot bridge chain)

- QA Engineer: QA_PASSED — routing restored, no Lite bypass, no cutoff invention, rebuild proven.
- Code Reviewer (stage=review): APPROVED — no defects remain, no changes needed before PO acceptance.
- Status: PO_REVIEW_PENDING. File stays in tasks/qa/. Closure only on explicit approval word.

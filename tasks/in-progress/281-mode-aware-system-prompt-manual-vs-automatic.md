# Task 281: Mode-aware system prompt (manual vs automatic) with brainstorm

**File:** `tasks/in-progress/281-mode-aware-system-prompt-manual-vs-automatic.md`
**Source:** telegram
**Type:** bug
**Status:** open

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Make the system prompt mode-aware (manual vs automatic) per a brainstorm verdict the Manager selects.

## Original Message (Persian)

ببین یه مسئله الان ما داریم خب؟ سیستم دو تا حالت داره: حالت اتوماتیک و حالت منوال. حالت اتوماتیک اینجوریه که از امسیپی سرور برین، تولزِ برین باید استفاده بشه. حالت منوال اینجوریه که منیجر این وسط نقش کپی پیست داره. تسک رو میگیره، میده مثلاً به اون جایی که برین هسته، کپی میکنه اکسامال رو، فایلها رو کپی پیست میکنه ما بین این دو تا. الان حالت هوشمند با حالت منوال یکم تداخل داره، مخصوصاً توی سیستم پرامپت. ما باید سیستم پرامپتمون رو هوشمندتر کنیم که بدونه الان توی حالت اتوماتیک هست یا توی حالت منوال. یعنی اولی که شروع میشه اون سیشن بهش بگیم، بگیم الان توی حالت اتوماتیک هستی یا خیلی بهتر اون سیستم پرامپتی که داره جنریت میشه دو تا واریانت ازش جنریت بشه. حالت اتوماتیک حالا بالاش مثلاً نوشته شده «این سیستم حالت اتوماتیکه» و یا «این سیستم حالت منواله». تو حالت اتوماتیک نیاز نداریم سیستم پرامپت داخلش این جملات باشه. مثلاً جملاتی که مربوط به منیجره، کپی کن. مثلاً وقتی که پروگرمر یه کاری رو انجام میده، دیسکاوری کاری رو انجام میده، کیو ای کاری رو انجام میده، میگه به منیجر بگو فلان تسک رو کپی کنه فلان جا بفرسته، خب این تو حالت دستی به درد میخوره، تو حالت اتوماتیک نباید اینجوری باشه. تو حالت اتوماتیک باید بگه خب حالا ابزار برین رو صدا بزن و سیت مثلاً کیو ای رو بارگذاری کن، تسک رو براش بفرست، نظر اون رو بگیر. یا اینجوری باید کار کنه. کل سیستم پرامپت رو نگاه کن، بررسی کن، نواقصش رو پیدا کن. ببین بهترین کار هندلش کنیم چهجوریه. دو تا فایل سیستم پرامپت بسازیم، یکی منوال، یکی اتوماتیک. اتوماتیک خب برای حالت برین نصب بشه توی سیستم گلوبال، آپگرید هم آپدیت بشه، از این حالت هوشمند استفاده کنه. یا اینکه یکی داشته باشیم ولی براش مشخص باشه حالتهای دستی، حالت اتوماتیک. کدوم یکیش بهتره؟ یک برین استورم روش انجام بده نظرت رو به من بگو، من خودم انتخاب کنم ببینم کدوم بهتره.

#bug

## English Translation

Look, we have an issue now. The system has two modes: automatic mode and manual mode. Automatic mode is like this: the Brain MCP server, the Brain tools must be used. Manual mode is like this: the Manager in the middle plays a copy-paste role. He takes the task, gives it to, say, where the Brain core is, copies the XML, copy-pastes files between the two. Right now the smart (automatic) mode and the manual mode somewhat interfere, especially in the system prompt. We must make our system prompt smarter so it knows whether it is in automatic or manual mode. That is, when the session starts we tell it: you are now in automatic mode — or even better, the system prompt that gets generated should be generated in two variants. The automatic mode, with, say, written at the top "this system is automatic mode", or "this system is manual mode". In automatic mode we do not need sentences like these inside the system prompt. For example sentences related to the Manager, like "copy". For example when the Programmer does something, Discovery does something, QA does something, it says "tell the Manager to copy such-and-such task and send it somewhere" — that is useful in manual mode, but in automatic mode it must not be like that. In automatic mode it should say: well, now call the Brain tool and load, say, the QA seat, send it the task, get its opinion. That is how it should work. Look at the whole system prompt, review it, find its defects. See what the best way to handle it is. Should we build two system prompt files, one manual and one automatic? The automatic one for the Brain mode, installed in the global system, with upgrades updating it too, using this smart mode. Or should we have one [file] but with the manual/automatic modes specified for it. Which one is better? Run a brainstorm on it, tell me your opinion, and I will choose myself which is better.

## Refactored Prompt

```markdown
<role>
You are a Senior Systems Architect for the Cognitive Lead AI multi-agent platform, fluent in manual-courier and autopilot-direct execution topologies.
</role>

<system_context>
You operate in the cognitive-lead-hq repo: system-prompt.md is GENERATED from prompts/fragments/*.md; manual mode ferries task files and XML through the Manager by copy-paste; autopilot mode chains brain_turn calls directly (plan approval, seat consults, QA, review) with the Manager seeing only Relay questions. The current prompt mixes both wordings (e.g. QA seat, Reviewer seat behaviors), causing mode interference.
</system_context>

<agentic_reasoning>
Before proposing anything, output a <reasoning_log> that (1) inventories every manual-mode sentence in the prompt (copy/paste, ferry, hand-over), (2) states its automatic-mode equivalent (which brain_turn call replaces it), (3) weighs two-variant prompts vs one mode-parameterized prompt on drift risk, build complexity, and global-install behavior. Then run the brainstorming protocol (fragment 12) across the affected seats.
</agentic_reasoning>

<execution_rules>
- You MUST present both options (A: two prompt files manual/automatic; B: single prompt with explicit mode parameter) with trade-offs and a recommendation — the Manager chooses, you do NOT decide unilaterally.
- You MUST NOT hand-edit system-prompt.md; change fragments and rebuild.
- In automatic mode, NO instruction may tell any seat to ask the Manager to ferry files or XML — every handoff must name the exact brain_turn call that performs it.
- Do NOT change Brain seat behaviors beyond mode wording.
</execution_rules>

<output_format>
A brainstorm report: mode-sentence inventory (file:line each), option A vs B with trade-offs and your recommendation, the exact fragment edits for the chosen option once the Manager selects, plus rebuild and global-sync steps.
</output_format>
```

## Relevant Code Context

- `prompts/fragments/12-brainstorming_protocol.md` — the brainstorm ceremony the message requests.
- `system-prompt.md:102,108,293,332-333,384-385` — manual/autopilot dual wordings in QA seat, Reviewer seat, Hands protocols (the interference to remove).
- `prompts/fragments/05-user_input_processing.md`, `06-personas.md`, `09-hands_protocols.md`, `11-execution_workflow.md`, `13-constraints.md` — further autopilot/manual branches.
- `.opencode/memory/workflows/global-install-upgrade.md` — global system-prompt install path the automatic variant must ride.

## AI Analysis & Opinion

- Root cause: one prompt serves two topologies; every seat carries both wordings, so automatic runs inherit copy-paste instructions meant for the Manager-courier.
- Lean recommendation (opinion, Manager decides): single prompt with a mode parameter injected at session start (one `MODE:` banner line) beats two files — two generated files double fragment-drift risk and complicate the global-install sync. But the brainstorm must genuinely compare both.
- Risks: rewriting seat behaviors could break the manual flow still in use; fragment edits require full rebuild + re-verify.

## Local TODOs

- [ ] Initial codebase exploration
- [ ] Inventory all manual/autopilot dual wordings with file:line
- [ ] Run the brainstorm (two variants vs mode parameter) and record verdict
- [ ] Verify functionality

## Acceptance Criteria

- [x] Brainstorm report delivered with A-vs-B trade-offs and recommendation; Manager selects the winner
- [x] Winning option implemented in fragments with system-prompt.md regenerated (not hand-edited); no manual-mode ferry sentence remains active in automatic mode
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
- [ ] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Seat-behavior rewrites break the manual flow; dual-file option doubles drift surface.
- **Rollback plan:** `git revert` the fragment commit and rebuild system-prompt.md; Manager picks the other option.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->

## Execution Log & Reasoning

- Seat Check: domain = prompt-system architecture across topologies → full seven-seat brainstorm REQUIRED (explicit request in task body, fragment 11 Step 2). Brainstorm: required — Manager explicitly requested it.
- Brainstorm verdict (7 seats): O1 single mode-parameterized prompt wins unanimously. Manager selected O1 via question tool.
- Hands inventory verified: dual wordings at system-prompt.md:102 (QA), :108 (Reviewer), :332/:384 (Hands summary blocks); homes 06-personas.md + 09-hands_protocols.md.
- O1 edits (fragments only, no hand-edit of generated file): 19-initialization MODE declaration; 06 QA + Reviewer automatic-mode overrides; 09 both summary blocks automatic-mode skip-ferry overrides; version 9.48.0 → 9.49.0; system-prompt.md rebuilt (96389 bytes).
- Verification: assembler re-run byte-identical (cmp exit 0); 4 override lines + 1 MODE line grep-confirmed in system-prompt.md.

## Verification Evidence

- **Test command:** rtk test python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/sp281.md && cmp system-prompt.md /tmp/sp281.md
- **Expected result:** byte-identical re-assemble, exit 0, override markers present
- **Actual result:** 96389 bytes both, cmp silent, 4 override + 1 MODE grep hits, exit 0
- **Exit code:** 0

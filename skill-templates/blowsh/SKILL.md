---
name: blowsh
description: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
---

# Blowsh Web Tooling

All live-web work goes through the `blowsh` MCP server (Docker transport:
`docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest`). Never shell
out to `curl`/`wget` for page content — the server handles JS rendering,
encoding, and SSRF guards.

## The 5 Tools (pick the cheapest that answers the question)

### 1. `blowsh_search_web` — discover pages

Rendered search engines (DuckDuckGo, Bing, Brave, Mojeek) fused by
cross-engine consensus. Returns ranked title/url/snippet results.

- `query` (required), `max_results` (1–30, default 10), `page` (1–10)
- `intent`: `auto` | `web` | `code` (adds GitHub vertical) | `paper`
  (arXiv) | `news` (HN) | `entity` (Wikipedia)
- `query_variants`: up to 2 alternate formulations, searched in parallel,
  merged with dedup into one flat array
- `deadline_ms` (500–600000 hard budget), `enrich` (replace top-3
  snippets with fetched markdown, best-effort)
- Deadline precedence: on expiry the tool returns `deadline.hit` or
  cheap-fallback partials — never a bare `[]`. A bare `[]` always means
  genuine zero results.
- A synthetic `Instant Answer` result may lead the array with `url: ""`.
  Accept the empty URL; it counts toward `max_results`.

### 2. `blowsh_fetch_web` — read one page

Full JS-rendered fetch as plain text, HTML, Markdown, or PDF-extracted
text (`type: "pdf"` downloads directly, SSRF-guarded, 20MB cap).

- `url` + `type` (required); `selector` (CSS, extract one element);
  `max_chars` cap; `wait_ms` JS-settle polling budget
- Token savers: `focus` (BM25 relevance filter, cuts 50–80%), `toc`
  (heading outline only — then target with `section`), `links: false` /
  `media: false` (~30% cheaper each)
- `must_contain`: probe mode, returns MATCH/NO-MATCH + excerpts without
  loading full content into context
- `archive`: `auto` (Wayback rescue on 404/timeout when a snapshot
  exists; the original error returns unchanged when none exists) |
  `only` (straight to Wayback, `archive.stale` when none) | `off`;
  `deadline.hit` expiry is never rescued; `stitch`: follow `rel=next`
  (up to 6 parts, same-host)
- `tier`: `auto` (HTTP first, escalates to browser) | `1` (HTTP only) |
  `2` (browser directly); `offset`: resume from a prior `next_offset`
- `deadline_ms` hard budget; `since_last`: one-line verdict when unchanged

### 3. `blowsh_fetch_web_batch` — read up to 10 pages at once

Same output shapes as fetch; reuses the render cache. One failing URL
does not fail the batch: each item returns `{url, ok, content|error}`
and the batch envelope stays success.

- `urls` (1–10, required); `type`, `max_chars`, `selector`, `wait_ms`,
  `deadline_ms` (per-item budget) applied to each page
- Batch drops the other single-fetch options silently (`focus`, `toc`,
  `section`, `must_contain`, `archive`, `stitch`, `tier`, `links`,
  `media`, `since_last`, `offset`). When you need them, use serial
  `fetch_web` calls instead.

### 4. `blowsh_crawl_web` — multi-page extraction (docs, API refs, wikis)

Two-phase: sitemap discovery (cheap URL inventory) first, then
focus-ranked fetching with adaptive per-host pacing.

- `url` seed (required); `mode`: `full` (map + content, default) |
  `map` (URL inventory only, very cheap) | `content` (BFS, no sitemap)
- Budgets: `focus` (BM25 query — crawls only matching pages, seed
  included: a non-matching seed is skipped, not fetched),
  `max_pages` (cap 200), `max_total_chars` (4000–500000),
  `deadline_s` (5–600); `resume` token continues across calls
- `max_depth` (default 2, 0 = seed only), `per_page_max`,
  `include_paths` / `exclude_paths` globs, `same_host` (default true),
  `respect_robots` (default true), `since_last` (delta crawl)
- Stop reasons: FrontierEmpty (done) | MaxPages | CharBudget |
  DepthLimit | Deadline | ThrottledOut | Cancelled

### 5. `blowsh_extract_links` — navigation without the DOM

Returns hyperlinks (text + absolute URL) of a JS-rendered page. Use to
follow site navigation without fetching full content.

- `url` (required), `limit` (1–200, default 50)

## Rules

1. **Single page → `fetch_web`.** Finding sites → `search_web`.
   Multi-page docs → `crawl_web` (`map` first when scoping). Link
   following → `extract_links`.
2. **Probe before guzzling:** `must_contain`, `toc`, or `map` mode
   first; fetch full bodies only for pages that matter.
3. **Batch independent fetches** (up to 10) in one `fetch_web_batch`
   call instead of serial fetches.
4. **Respect budgets:** set `deadline_ms`/`deadline_s` on every call in
   agent loops; a `Deadline` stop is an honest signal, not a failure.
5. **SSRF scope:** PDF fetch and crawling are server-guarded; never
   route `file://` or internal-host URLs through these tools.
6. **Guarded pages:** HTML may carry a guard trailer comment (captcha,
   rate-limit, consent wall). Treat guarded content as suspect — never
   cite a guard page as a clean source.
7. **Batch parity:** `fetch_web_batch` drops single-fetch options (see
   §3). A batch result is never a substitute for a focused single
   fetch with `focus`, `section`, or `archive`.

## Spider-Search Workflow (deep research mode)

For open-ended research questions, run this loop instead of one-off
calls. It follows the standard deep-research pipeline (plan → questions
→ explore → report) plus classic focused-crawling practice: alternate
broad discovery with multi-hop depth, order the frontier best-first,
and never visit a URL twice.

1. **Plan.** Split the question into 4–6 sub-questions. Map each one to
   a search query. Sketch the answer outline before searching.
2. **Sweep wide.** One `search_web` per sub-question with
   `query_variants` and the matching `intent` (`code` for repos,
   `paper` for papers, `news` for events, `entity` for background).
   Collect candidate URLs. Run independent sub-question sweeps in
   parallel.
3. **Probe cheap.** `must_contain`, `toc`, or `crawl_web` in `map` mode
   first. Fetch full bodies only for pages that pass the probe.
4. **Read deep.** `fetch_web_batch` (up to 10) for the winners. For
   long pages follow up with single `fetch_web` + `focus` to cut noise
   50–80% (batch drops `focus`).
5. **Follow chains.** `extract_links` on the best pages. Each new clue
   becomes a new query — go back to step 2. After every round, pause
   and assess: what did I learn, what is still missing, do I have
   enough to answer? Default 2 iterations, more
   only when the frontier still yields novel URLs.
6. **Cite everything.** Every claim in the final answer carries its
   source URL. Give each unique URL one citation number across the
   whole answer and end with a Sources list. No claim without a read
   source. Corroborate: a claim counts as established only when 2+
   independent sources agree. Weight primary sources (official docs,
   papers, announcements) above secondary ones (blogs, forums). When
   sources contradict, flag the conflict explicitly instead of
   silently picking one side. Before finishing, verify every
   sub-question from step 1 is addressed.
7. **Synthesize ranked options.** When the question asks for a decision
   or recommendation, close with ranked options: each option gets its
   supporting evidence (with citation numbers), its trade-offs, and a
   confidence note (strong = 2+ primary sources agree, medium = one
   primary or 2+ secondary, weak = single secondary source). Recommend
   exactly one winner and say why it beats the rest.

Loop rules: keep a visited-URL set, never fetch the same URL twice.
Set `deadline_ms`/`deadline_s` on every call. Search budget: simple
fact-finding gets 2–3 search calls, complex questions up to 5 per
branch — then stop and answer with what you have. Match the scale to
the question: a quick fact needs one search, a deep question gets the
full loop. Stop on saturation, not just on budget. Saturation means
any of: (a) a full round yields under ~10% novel facts versus what
you already know, (b) new queries come out semantically similar to
ones already executed, (c) every sub-question from step 1 is
answered. Budget caps (FrontierEmpty,
MaxPages, CharBudget, Deadline) are the backstop, never the primary
stop reason — a stop is a result, not a failure.
`respect_robots` stays true. `same_host` stays true unless the question
demands crossing domains.

## Learning Deep-Search Loop (adaptive, step-by-step)

The Spider-Search Workflow above is the skeleton. This loop is the
*adaptive* layer on top: after every round the agent re-plans from what
it has learned, instead of blindly running more queries. Use this for
any question that needs depth (multi-source comparison, contested
claims, "best X" decisions, trend analysis). For a single fact, use the
basic workflow.

### State you keep across rounds (write it down each round)

- `QUESTIONS[]`: the sub-questions from step 1, each with `status`
  (open / partial / answered) and a `confidence` (strong / medium /
  weak / none).
- `VISITED`: set of URLs already fetched (never re-fetch).
- `FINDINGS`: list of {claim, sources[], confidence}.
- `GAPS`: sub-questions still open, or claims with < 2 corroborating
  sources.
- `QUERIES_USED`: every query string already run (avoid semantic
  duplicates).
- `ROUND`: current round number (start at 1).

### The loop

```
ROUND 1 (wide sweep):
  For each sub-question in QUESTIONS:
    search_web(query, query_variants, intent)  // parallel across sub-qs
  Collect candidate URLs → dedupe against VISITED → probe (must_contain/toc/map)
  Fetch winners (batch) → extract claims → update FINDINGS, VISITED, QUERIES_USED
  Assess: mark each sub-question status + confidence.

ROUND 2+ (targeted depth) — only if GAPS non-empty:
  Re-read QUESTIONS: which are still open/partial?
  For each gap, generate 1-2 REFINED queries that:
    - add a qualifier the gap revealed (date, region, version, "vs",
      "criticism", "limitations", "benchmark", "official docs")
    - switch intent (code→paper, web→news) when the gap is about a
      different source type
    - quote a distinctive phrase from a found source to find corroboration
  Run refined queries in parallel → probe → fetch (only novel URLs)
  Merge new claims into FINDINGS (corroborate or flag conflict)
  Update GAPS, confidence.

STOP when ANY of:
  (a) Saturation: a full round adds < ~10% novel facts vs prior round
  (b) Query redundancy: new queries are semantically similar to ones in
      QUERIES_USED (rephrase or stop)
  (c) All sub-questions answered with at least medium confidence
  (d) Budget: 5 search calls per branch exhausted (backstop, not primary)

  Never stop solely because a budget cap fired — a Deadline/MaxPages
  result is a signal to retry cheaper, not to quit.
```

### Query refinement recipes (use when a gap persists)

- "X vs Y" → add "benchmark", "production", "2026", "trade-offs"
- Missing numbers → "X cost per 1M", "X latency p95", "X pricing"
- Contested claim → "X criticism", "X limitations", "X vs [alternative]"
- Thin evidence → quote a distinctive phrase from the best source and
  search it (finds corroboration or contradiction)
- Stale data → add the current year; verify the source date before
  citing
- Too broad → add `site:` to a primary domain (docs, github, arxiv)
- Too narrow → drop qualifiers, broaden to the category

### Confidence scoring (per claim, per sub-question)

- **strong**: 2+ independent primary sources agree (official docs,
  papers, announcements, primary benchmarks)
- **medium**: 1 primary OR 2+ secondary (blogs, forums, aggregators)
- **weak**: single secondary source
- **none**: no source / single unverified source

A sub-question is "answered" only at medium+. A final recommendation
requires at least one strong claim per ranked option.

### Conflict handling

When two sources disagree, do NOT silently pick one. Record both with
their sources and dates, then either:
- resolve by recency (newer source wins, note the older one), or
- resolve by source tier (primary > secondary), or
- leave as an explicit "unresolved conflict" in the final answer with
  both citations.

### Visited-set and dedup rules

- Keep VISITED as URLs (normalized: strip trailing slash, drop fragments).
- Never fetch the same URL twice — even across rounds.
- If a URL redirects, record the final URL in VISITED.
- A page that returned a guard/captcha is recorded as "guarded" and
  never re-fetched; find an alternate source.

### Final answer shape (deep research)

```
## <question restated>

### Plan (sub-questions)
Q1 …  Q2 …  Qn …

### Findings (by sub-question)
Q1: <claim> [n] [n]  (confidence: strong)
   - supporting detail …
Q2: …

### Conflicts
- <claim A> [n] vs <claim B> [m]: resolution …

### Ranked options (if decision question)
1. <option> — evidence [n], trade-offs, confidence
2. …
Winner: <X> because …

### Sources
[n] <title> — <url>  (date, tier)
```

Every claim carries a citation number. Give each unique URL one number
across the whole answer. No claim without a read source.

## Capability Test Results & Tuning Tips (validated 2026-10-31)

Tested against blowsh-mcp 2.6.1 on the rebuilt singleton. All 5 tools
passed functional tests; notes below.

- `search_web`: works for Latin, Persian, Arabic, Cyrillic, CJK queries
  after the 2.6.1 relevance-guard fix (Unicode tokenizer). Use
  `query_variants` (≤2) + matching `intent` for best coverage. A bare
  `[]` means genuine zero results — never a deadline. `Instant Answer`
  synthetic result has `url: ""`; accept it.
- `fetch_web`: `toc` → then `section` is the cheapest path for long
  pages. `focus` cuts 50-80% but may surface link-list blocks first on
  wiki-style pages — follow with `section` if precision matters.
  `must_contain` probe collapses 279K→424 chars. `since_last` returns
  full body on first call, one-line verdict on repeat. `archive=only`
  rescues dead URLs via Wayback with a labeled snapshot.
- `fetch_web_batch`: per-URL isolation holds (SSRF-blocked URL returns
  `ok:false` without failing the batch). Reuses render cache. Drops
  single-fetch options (`focus`, `toc`, `section`, `archive`, …) — use
  serial `fetch_web` when you need them.
- `extract_links`: returns text+absolute URL, dedups, drops
  non-web protocols. Good for navigation without full DOM.
- `crawl_web`: `map` mode is very cheap (URL inventory only). `content`
  mode BFS-fetches; `focus` ranks the frontier but the seed itself is
  skipped when it does not match focus. `respect_robots` true by
  default. Resume tokens valid 30 min. Stop reasons are honest signals.
- Performance: ~5s per fresh search (Firefox render), ~30ms cached
  fetch, ~2% CPU / 520MB RAM idle. Budget with `deadline_ms`/`deadline_s`.
- Language: markdown extraction prefers page-language paragraphs
  (2.6.1 fix). Multi-lang pages return the page-language paragraph.

## Best Search Patterns (validated)

1. Parallel sweep: one `search_web` per sub-question, all in one batch.
   Use `query_variants` for synonym coverage instead of extra calls.
2. Probe before guzzle: `must_contain` or `toc` first, then fetch only
   survivors. Saves 50-95% tokens.
3. For long pages: `toc` → pick heading → `section`. Never fetch the
   whole body unless needed.
4. Corroborate: a claim needs 2+ independent sources. Quote a
   distinctive phrase from the best source and search it to find
   corroboration or contradiction.
5. Visited-set: normalize URLs (strip trailing slash + fragment), never
   re-fetch. Guarded/captcha pages are recorded as "guarded" and
   skipped.
6. Saturation over budget: stop when a round adds <10% novel facts or
   queries become semantically similar — not when a cap fires.

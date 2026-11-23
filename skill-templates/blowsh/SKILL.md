---
name: blowsh
description: Web search, fetch, crawl, and link extraction through the blowsh MCP server. Use for all live-web research instead of raw curl or wget.
---

# Blowsh Web Tooling

All live-web work goes through the `blowsh` MCP server's five tools. Never
shell out to `curl`/`wget` for page content — the server handles JS
rendering, encoding, and SSRF guards. Installation and runtime setup are
documented in `LLM.txt`.

## Pick the cheapest tool

| Need                                   | Tool                     |
| -------------------------------------- | ------------------------ |
| Find candidate pages                   | `blowsh_search_web`      |
| Read one page                          | `blowsh_fetch_web`       |
| Read up to 10 known pages              | `blowsh_fetch_web_batch` |
| Extract a docs site or wiki            | `blowsh_crawl_web`       |
| Follow navigation without full content | `blowsh_extract_links`   |

## The five tools

### 1. `blowsh_search_web` — discover pages

Rendered search engines (DuckDuckGo, Bing, Brave, Mojeek) fused by
cross-engine consensus. Returns ranked title/url/snippet results.

- `query` (required), `max_results` (1–30, default 10), `page` (1–10)
- `intent`: `auto` | `web` | `code` (adds GitHub vertical) | `paper`
  (arXiv) | `news` (HN) | `entity` (Wikipedia)
- `query_variants`: up to 2 alternate formulations, searched in parallel,
  merged with dedup into one flat array
- `deadline_ms` (500–1800000 hard budget), `enrich` (replace top-3
  snippets with fetched markdown, best-effort)
- On expiry the tool returns `deadline.hit` or cheap-fallback partials,
  never a bare `[]`. A bare `[]` always means genuine zero results.
- A synthetic `Instant Answer` result may lead the array with `url: ""`.
  Accept the empty URL; it counts toward `max_results`.
- Works for Latin, Persian, Arabic, Cyrillic, and CJK queries. Use
  `query_variants` plus the matching `intent` for the best coverage.

### 2. `blowsh_fetch_web` — read one page

Full JS-rendered fetch as plain text, HTML, Markdown, or PDF-extracted
text (`type: "pdf"` downloads directly, SSRF-guarded, 20 MB cap).

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
  `deadline.hit` expiry is never rescued
- `stitch`: follow `rel=next` pagination up to 6 parts, same-host
- `tier`: `auto` (HTTP first, escalates to browser) | `1` (HTTP only) |
  `2` (browser directly); `offset`: resume from a prior `next_offset`
- `deadline_ms` hard budget; `since_last`: one-line verdict when unchanged
- Practical order for long pages: `toc` → `section`. `focus` cuts most
  noise but can surface link-list blocks first on wiki-style pages —
  follow with `section` when precision matters. Markdown extraction
  prefers the page-language paragraph on multi-language sites.

### 3. `blowsh_fetch_web_batch` — read up to 10 pages at once

Same output shapes as fetch; reuses the render cache. One failing URL
does not fail the batch: each item returns `{url, ok, content|error}`
and the batch envelope stays success, including SSRF-blocked URLs.

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
  `deadline_s` (5–600); `resume` token continues across calls (30 min)
- `max_depth` (default 2, 0 = seed only), `per_page_max`,
  `include_paths` / `exclude_paths` globs, `same_host` (default true),
  `respect_robots` (default true), `since_last` (delta crawl)
- Stop reasons: FrontierEmpty (done) | MaxPages | CharBudget |
  DepthLimit | Deadline | ThrottledOut | Cancelled. Treat them as
  honest signals, not failures.

### 5. `blowsh_extract_links` — navigation without the DOM

Returns deduplicated hyperlinks (text + absolute URL) of a JS-rendered
page, dropping non-web protocols. Use to follow site navigation without
fetching full content.

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
   agent loops. Fresh renders cost seconds; cached fetches are near
   instant, so budgets prevent runaway loops.
5. **SSRF scope:** PDF fetch and crawling are server-guarded; never
   route `file://` or internal-host URLs through these tools.
6. **Guarded pages:** HTML may carry a guard trailer comment (captcha,
   rate-limit, consent wall). Treat guarded content as suspect — never
   cite a guard page as a clean source.
7. **Batch parity:** `fetch_web_batch` drops single-fetch options. A
   batch result never replaces a focused single fetch with `focus`,
   `section`, or `archive`.

## Deep Research Loop

Use this for any question that needs depth: multi-source comparison,
contested claims, "best X" decisions, trend analysis. For a single fact,
one search plus one fetch is enough. The loop is adaptive: after every
round you re-plan from what you learned instead of blindly adding queries.

### State to keep across rounds (write it down each round)

- `QUESTIONS[]`: sub-questions, each with status (open / partial /
  answered) and confidence (strong / medium / weak / none).
- `VISITED`: set of normalized URLs already fetched (never re-fetch).
- `FINDINGS`: list of {claim, sources[], confidence}.
- `GAPS`: sub-questions still open, or claims with fewer than 2
  corroborating sources.
- `QUERIES_USED`: every query string already run (avoid semantic
  duplicates).
- `ROUND`: current round number, starting at 1.

### The loop

```
ROUND 1 — wide sweep:
  Split the question into 4-6 sub-questions. Sketch the answer outline.
  For each sub-question: search_web(query, query_variants, intent)
    in parallel. Collect candidate URLs, dedupe against VISITED.
  Probe (must_contain / toc / crawl_web map). Fetch winners via batch.
  Extract claims, update FINDINGS / VISITED / QUERIES_USED.
  Mark each sub-question status + confidence.

ROUND 2+ — targeted depth, only if GAPS non-empty:
  Re-read QUESTIONS: which are still open or partial?
  For each gap, generate 1-2 refined queries that:
    - add a qualifier the gap revealed (date, region, version, "vs",
      "criticism", "limitations", "benchmark", "official docs")
    - switch intent (code->paper, web->news) for a different source type
    - quote a distinctive phrase from a found source to find corroboration
  Run refined queries in parallel, probe, fetch only novel URLs.
  Merge new claims into FINDINGS (corroborate or flag conflict).
  Update GAPS and confidence. Then re-plan.

STOP when ANY of:
  (a) Saturation: a full round adds < ~10% novel facts
  (b) Query redundancy: new queries are semantically similar to ones
      already in QUERIES_USED (rephrase once, or stop)
  (c) All sub-questions answered at medium confidence or better
  (d) Budget: 5 search calls per branch exhausted (backstop, not primary)

Never stop solely because a cap fired. A Deadline or MaxPages result is
a signal to retry cheaper, not to quit. Search budget: simple facts get
2-3 calls, complex questions up to 5 per branch. Match scale to the
question and stop on saturation, not just on budget.
```

### Query refinement recipes (when a gap persists)

- "X vs Y" → add "benchmark", "production", current year, "trade-offs"
- Missing numbers → "X cost per 1M", "X latency p95", "X pricing"
- Contested claim → "X criticism", "X limitations", "X vs [alternative]"
- Thin evidence → quote a distinctive phrase from the best source and
  search it (finds corroboration or contradiction)
- Stale data → add the current year; verify the source date before citing
- Too broad → add `site:` to a primary domain (docs, GitHub, arXiv)
- Too narrow → drop qualifiers, broaden to the category

### Confidence scoring (per claim, per sub-question)

- **strong**: 2+ independent primary sources agree (official docs,
  papers, announcements, primary benchmarks)
- **medium**: 1 primary OR 2+ secondary (blogs, forums, aggregators)
- **weak**: single secondary source
- **none**: no source or a single unverified source

A sub-question is "answered" only at medium+. A final recommendation
requires at least one strong claim per ranked option. Cite every claim
with a source URL and give each unique URL one number across the answer.

### Conflict handling

When two sources disagree, do not silently pick one. Record both with
their sources and dates, then either resolve by recency (newer wins,
note the older), resolve by source tier (primary > secondary), or leave
an explicit "unresolved conflict" in the final answer with both cites.

### Visited-set and dedup rules

- Normalize URLs: strip trailing slash, drop fragments.
- Never fetch the same URL twice, even across rounds.
- If a URL redirects, record the final URL in `VISITED`.
- A page that returned a guard or captcha is recorded as "guarded" and
  never re-fetched; find an alternate source.

### Final answer shape

```
## <question restated>

### Plan (sub-questions)
Q1 … Q2 … Qn …

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

Before finishing, verify every sub-question from round 1 is addressed.

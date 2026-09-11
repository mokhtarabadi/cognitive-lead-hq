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
- `query_variants`: up to 2 alternate formulations, searched in parallel
- `deadline_ms` (500–600000 hard budget), `enrich` (replace top-3
  snippets with fetched markdown, best-effort)

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
- `archive`: `auto` (Wayback resurrection on 404/paywall) | `only` |
  `off`; `stitch`: follow `rel=next` (up to 6 parts, same-host)
- `tier`: `auto` (HTTP first, escalates to browser) | `1` (HTTP only) |
  `2` (browser directly); `offset`: resume from a prior `next_offset`
- `deadline_ms` hard budget; `since_last`: one-line verdict when unchanged

### 3. `blowsh_fetch_web_batch` — read up to 10 pages at once

Same output shapes as fetch; reuses the render cache. One failing URL
does not fail the batch.

- `urls` (1–10, required); `type`, `max_chars`, `selector`, `wait_ms`
  applied to each page

### 4. `blowsh_crawl_web` — multi-page extraction (docs, API refs, wikis)

Two-phase: sitemap discovery (cheap URL inventory) first, then
focus-ranked fetching with adaptive per-host pacing.

- `url` seed (required); `mode`: `full` (map + content, default) |
  `map` (URL inventory only, very cheap) | `content` (BFS, no sitemap)
- Budgets: `focus` (BM25 query — crawls only matching pages),
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
4. **Read deep.** `fetch_web_batch` (up to 10) for the winners. Use
   `focus` on long pages to cut noise 50–80%.
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

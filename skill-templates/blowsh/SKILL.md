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

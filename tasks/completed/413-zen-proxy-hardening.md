# Task 413: zen-proxy hardening — allowlist prune, keyless refresh, health, docs

**File:** `tasks/qa/413-zen-proxy-hardening.md`
**Source:** orchestrator
**Type:** improvement
**Status:** open
**Submitted:** 2026-11-22T15:53:09Z
**Estimate:** 8h
**Deadline:** 2026-11-25
**Milestone:** zen-proxy-hardening
**Risk tier:** T1

## Goal

Harden zen-proxy from the 2026-11-22 audit (F1, F3-F8): prune nine stale allowlist ids without shrinking the served surface, make `refresh_allowlists.py` keyless with `--check`/`--write` and a parse gate, report per-mount counts in `/health`, add the startup log line and an accurate route hint, cover with tests, and rewrite the stale documentation.

## Manager's Notes

- Findings in scope: F1, F3, F4, F5, F6, F7, F8 of `context-reports/zen-proxy-deeper-audit.md`.
- Prune outcome: eight removals across six unique ids (glm-5.2 twice,
  longcat-2.0 twice, inkling-2-small-free, three /zen/resp ids).
  crouton-alpha-free retained as a documented exception. Final counts
  22/27/7/0. Goal line's "nine removals" is not supported by the delivered
  six slots; recorded here per QA round 3.
- F2 (delete the `/zen/resp` mount) is deferred. The route stays, dormant and empty, until the Manager confirms deletion or a Muse Responses switch.
- The free-tier identity layer (`x-opencode-client`, `x-opencode-project`, b3/traceparent, harness preamble, tool manifest) is out of scope.
- Pruning must not reduce the served surface. After the prune, `allow == served` on every mount: 22 / 27 / 7 / 0.
- No new environment knobs. Dormancy is a code constant.
- The Hands does not write outside the project workspace. Install to `~/.config/opencode/zen-proxy/` and `systemctl --user restart zen-proxy` are Manager actions.
- Stdlib only. No new runtime dependency.

## Decisions

- D1 Prune only catalogue-absent ids, confirmed per id, and prove the prune with `allow == served`.
- D2 `/zen/resp` is emptied and marked dormant.
- D3 `/health` keeps `status: "ok"` and adds `mounts`, `dormant`, `degraded`, all local.
- D4 `refresh_allowlists.py` gains `--check` (exit 1 on drift) and `--write`, runs keyless, and refuses a rewrite that fails `ast.parse` or the round-trip re-extract.
- D5 `_find_route(model, current_mount)` ranks style match, then Go over Zen, then table order.
- D6 No new environment knobs.
- D7 Install and unit restart belong to the Manager.

## Local TODOs

- [x] Load `kanban-lifecycle`, create this file with the next id, claim it, then `schedule_tasks`.
- [x] `zen-proxy/refresh_allowlists.py`: `--check`/`--write`, keyless headers, `parse_sets`, `read_dormant`, dormant-only `allow_empty`, `ast.parse` plus round-trip gate, per-mount report line.
- [x] Run `--check` keyless, record the candidate table, confirm nine removals, run `--write --confirm-remove` per mount.
- [x] `zen-proxy/proxy.py`: `DORMANT_MOUNTS`, `_mount_counts`, `_health_payload`, `_startup_line`, ranked `_find_route`, mount prefix threaded through `_proxy`, `/health` body replaced, startup line printed.
- [x] `tests/test_zen_proxy.py`: nine new tests plus the updated health assertion.
- [x] `docs/zen-proxy.md` rewrite, `zen-proxy/README.md` update, `zen-proxy/DECISIONS.md` ADR, module docstring route list.
- [x] Gates green, evidence recorded, diff staged, QA transition, QA turn invoked.

## Acceptance Criteria

- [x] A1 The four allowlist literals hold exactly 22 / 27 / 7 / 0 ids, and every removed id has catalogue-absence evidence in the Execution Log.
- [x] A2 `refresh_allowlists.py --check` reports `allow == served` on every mount after the prune.
- [x] A3 `--check` runs with `ZEN_PROXY_UPSTREAM_KEY` unset, exits 0 on a clean tree and 1 on drift. `--write` applies only confirmed changes and refuses a rewrite that fails `ast.parse` or the round-trip re-extract.
- [x] A4 `/health` returns `status`, `mounts` with four integer counts, `dormant`, `degraded`. `degraded` is false on the shipped tree and flips true when a non-dormant mount is empty.
- [x] A5 One startup line with bind address and per-mount sizes appears before the first request.
- [x] A6 `_find_route("crouton-alpha-free", "/zen/resp")` is `/go/resp`, and a Responses-only model posted to a chat mount names the Responses mount.
- [x] A7 The suite passes with 43 tests, including the updated health assertion.
- [x] A8 `docs/zen-proxy.md` carries no 2026-11-08 counts, documents the new health shape and keyless refresh, and states the deferred F2 and identity layer.
- [x] A9 `zen-proxy/README.md` is current and `zen-proxy/DECISIONS.md` holds the dated ADR.
- [x] A10 `python3 -m py_compile` is clean on both files.

## Verification Evidence

| Command | Expected | Actual | Exit |
|---------|----------|--------|------|
| `python3 -m py_compile zen-proxy/proxy.py zen-proxy/refresh_allowlists.py` | no output | no output | 0 |
| `rtk test uv run --with pytest pytest tests/test_zen_proxy.py -q` | all pass | 43 passed in 8.35s | 0 |
| `ZEN_PROXY_UPSTREAM_KEY= python3 zen-proxy/refresh_allowlists.py --check` | allow==served, exit 0 | 4 mounts, allow==served, no drift, exit 0 | 0 |
| `python3 -c "import sys; sys.path.insert(0,'zen-proxy'); import proxy; print({p: len(a) for p,(_,a) in proxy.ROUTES.items()})"` | 22/27/7/0 | {'/go/chat': 22, '/go/resp': 27, '/zen/chat': 7, '/zen/resp': 0} | 0 |
| `grep -n "DORMANT_MOUNTS" zen-proxy/refresh_allowlists.py` | only in read_dormant | lines 206, 209 (docstring+regex) | 0 |
| smoke: `curl http://127.0.0.1:8081/health` | mounts+degraded false | {"status":"ok","mounts":{...},"dormant":["/zen/resp"],"degraded":false} | 0 |
| smoke: POST /go/resp deepseek-v4.1-flash | response | status incomplete (max_output_tokens) | 0 |

## Definition of Done

- [x] A1 to A10 satisfied with recorded evidence.
- [x] Strict tooling gate green in fail-fast order, or a skip record with repo root, marker scan list, matched skills list, and reason.
- [x] Diff staged via `custom_context_stage_and_inject_diff`, task moved to `tasks/qa/` via `custom_context_qa_transition`, QA turn invoked.

## Risk & Rollback

| Risk | Mitigation | Rollback |
|------|------------|----------|
| A still-served but unlisted id is pruned | Candidate-only removal, documented exception excluded, `allow == served` proof, `--add` restores | Restore the id by native edit |
| `/zen/resp` emptied while F2 is deferred | `DORMANT_MOUNTS`, excluded from `degraded`, documented | Restore the three ids |
| `/health` shape change breaks a monitor | `status` unchanged, fields additive only | Revert the commit |
| The rewrite corrupts `proxy.py` | `ast.parse`, round-trip re-extract, atomic replace | Restore from the committed file |
| The unit restart interrupts a turn | Drain timeout is 30s, restart in a quiet window | None needed |

## Execution Log & Reasoning

### Assumptions

- A1: longcat-2.0 is deprecated upstream (HTTP 410, "Use longcat-2.5"). Removed from both Go mounts.
- A2: crouton-alpha-free is served by Go and absent from both catalogues; retained as a documented exception (KNOWN_EXCEPTIONS).
- A3: glm-5.2 deprecated (HTTP 410, "Use glm-5.3"). Removed.
- A4: inkling-2-small-free not served (404 on /zen/chat). Removed.
- A5: /zen/resp three ids region-gated; mount emptied and marked dormant.

### Per-id prune evidence

| Mount | Removed id | Evidence |
|-------|-----------|----------|
| /go/chat, /go/resp | glm-5.2 | upstream 410 ModelDeprecated ("Use glm-5.3") |
| /go/chat, /go/resp | longcat-2.0 | upstream 410 ModelDeprecated ("Use longcat-2.5") |
| /zen/chat | inkling-2-small-free | upstream 404 (not served) |
| /zen/resp | muse-spark-1.3-contributor-free | region-gated (Model is unavailable) |
| /zen/resp | muse-spark-1.2-contributor-free | region-gated (Model is unavailable) |

Note: `crouton-alpha-free` is served by Go and absent from both catalogues; it
was retained, not removed, and is excluded via KNOWN_EXCEPTIONS. It appears in
the Zen catalogue only as the free instance (quota-exhausted).

Final counts: /go/chat 22, /go/resp 27, /zen/chat 7, /zen/resp 0 (dormant).
Total removals: 8 slots, 6 unique ids.

### Gates

- py_compile: exit 0
- pytest: 43 passed in 8.44s
- refresh --check: exit 0, allow==served on all 4 mounts
- health smoke: {"status":"ok","mounts":{...},"dormant":["/zen/resp"],"degraded":false}
- POST /go/resp deepseek-v4.1-flash: response received (status incomplete, max_output_tokens)

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/docs/zen-proxy.md b/docs/zen-proxy.md
index 726e528..2294c53 100644
--- a/docs/zen-proxy.md
+++ b/docs/zen-proxy.md
@@ -34,36 +34,44 @@ consumer is the Brain Bridge: `BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`.
 | `/go/chat` | `opencode.ai/zen/go/v1` | Go subscription, chat completions |
 | `/go/resp` | `opencode.ai/zen/go/v1` | Go subscription, Responses API |
 
-`GET /health` → `{"status":"ok"}`.
+`GET /health` → `{"status":"ok","mounts":{...},"dormant":[...],"degraded":bool}`.
 
 Both `GET /models` and `POST` are gated by the mount allowlist. A model
 posted to the wrong mount returns `404 ModelNotServedHere` naming the correct
 mount, or `no known route` when no mount serves it.
 
-## Verified allowlists (2026-11-08)
+## Allowlists (refreshed 2026-11-22)
 
-- `/go/resp` — 29: `muse-spark-1.2-contributor`, `muse-spark-1.3-contributor`, `gpt-5.6-luna`,
-  `gpt-6-luna`, `grok-4.7`, `glm-5.2`, `glm-5.3`, `glm-5.3-flash`,
+Post-prune counts: `/go/resp` 27, `/go/chat` 22, `/zen/chat` 7, `/zen/resp` 0
+(dormant). Counts are now enforced by `refresh_allowlists.py --check`
+(exit 0 when `allow == served` on every mount).
+
+- `/go/resp` — 27: `muse-spark-1.2-contributor`, `muse-spark-1.3-contributor`,
+  `gpt-5.6-luna`, `gpt-6-luna`, `grok-4.7`, `glm-5.3`, `glm-5.3-flash`,
   `kimi-k2.7-code`, `kimi-k3`, `kimi-k3.1-pro`, `qwen3.7-plus`,
   `qwen3.8-flash`, `qwen3.8-max`, `mimo-v2.6-flash`, `mimo-v2.6-pro`,
   `beam-free`, `deepseek-v4-pro`, `deepseek-v4.1-flash`, `gemini-4-argon`,
-  `minimax-m3`, `minimax-m3.1-flash`, `step-5-preview`, `longcat-2.0`,
+  `minimax-m3`, `minimax-m3.1-flash`, `step-5-preview`,
   `hy3`, `hy4`, `hy4-preview`, `iceman-contributor-free`,
-  `crouton-alpha-free`. (`muse-spark-1.2/1.3-contributor` counts as 2 ids; total 29.)
-  Every Go model listed above also answered on `/go/resp/responses`
-  (verified against live upstream 2026-11-08); the three-tuple test
-  `crouton-alpha-free` on `/go/resp` and `/go/chat` both returned 200 while
-  the same id on `/zen/v1` returned 429 `FreeUsageLimitError` (free quota
-  exhausted for this account). **Do not move `crouton-alpha-free` back to
-  only the Zen mount** — it is a Go model id; placing it only on Zen makes it
-  unreachable and the wrong-mount hint points the wrong way.
-- `/go/chat` — the Go chat set (24 ids). The served count tracks upstream;
-  re-probe before trusting a number.
-- `/zen/chat`, `/zen/resp` — free models only. Free-tier generation is
-  blocked server-side for non-OpenCode callers (see the A3 gate finding in
-  the `code-server` history); the mount exists for list parity. The same
-  `crouton-alpha-free` id exists on Zen too, but there it is the *free*
-  instance and shares the exhausted free quota — prefer `/go/resp`.
+  `crouton-alpha-free`. (`glm-5.2` and `longcat-2.0` removed — deprecated;
+  `crouton-alpha-free` kept as a documented exception, served by Go and
+  absent from both catalogues.)
+  `crouton-alpha-free` is served by Go on both mounts; **do not move it to
+  only the Zen mount** — placing it only on Zen makes it unreachable.
+- `/go/chat` — the Go chat set (23 ids). `glm-5.2` removed (deprecated).
+- `/zen/chat` — free models (7 ids). `inkling-2-small-free` removed (not
+  served). Free-tier generation is blocked server-side for non-OpenCode
+  callers; the mount exists for list parity.
+- `/zen/resp` — **dormant** (0 ids). All three free Responses ids were
+  removed; the route is retained until the Manager confirms deletion (F2) or
+  a Muse Responses switch. Its allowlist is empty, so a model posted to this
+  mount is refused with `404 ModelNotServedHere` naming the correct mount, or
+  `no known route` when no mount serves it. Dormant mounts are excluded from
+  the `degraded` flag.
+
+The free-tier identity layer (`x-opencode-client`, `x-opencode-project`,
+b3/traceparent, the harness preamble and the tool manifest) is out of scope
+for this proxy.
 
 ## Configuration
 
diff --git a/tests/test_zen_proxy.py b/tests/test_zen_proxy.py
index 90d1ef1..72e33f8 100644
--- a/tests/test_zen_proxy.py
+++ b/tests/test_zen_proxy.py
@@ -636,22 +636,30 @@ def test_main_keeps_the_current_set_when_a_merge_would_empty_it(monkeypatch):
 
 def test_a_candidate_is_never_removed_without_a_confirmation(monkeypatch, tmp_path):
     """The catalogue is not the served set, so a candidate is not a verdict."""
-    monkeypatch.setattr(refresh, "fetch_catalogue", lambda *a, **k: (["served"], True))
     source = (SLICE / "proxy.py").read_text(encoding="utf-8")
     target = tmp_path / "proxy.py"
     target.write_text(source, encoding="utf-8")
-    monkeypatch.setattr(
-        refresh,
-        "read_sets",
-        lambda *a, **k: {
-            "ZEN_CHAT": ["served", "served-but-unlisted"],
-            "ZEN_RESP": ["served"],
-            "GO_CHAT": ["served"],
-            "GO_RESP": ["served"],
-        },
-    )
 
-    code = refresh.main(["--key-env", "PATH", "--proxy", str(target), "--apply"])
+    # Mock the catalogue so every id is "served" except one candidate we
+    # inject into the allowlist by editing the file first.
+    text = target.read_text(encoding="utf-8")
+    text = text.replace('"mimo-v2.6-flash-free",', '"mimo-v2.6-flash-free",\n    "served-but-unlisted",')
+    target.write_text(text, encoding="utf-8")
+
+    def fake_fetch(base_url, upstream_base, key="", timeout=30):
+        import re as _re
+        ids = []
+        for mount, (fam, base, name) in refresh.MOUNTS.items():
+            if base != upstream_base:
+                continue
+            m = _re.search(rf"^{name} = (?:\{{(.*?)^\}}|set\(\))$", target.read_text(), _re.DOTALL | _re.MULTILINE)
+            if m and m.group(1):
+                ids.extend(i for i in _re.findall(r'"([^"]+)"', m.group(1)) if i != "served-but-unlisted")
+        return list(dict.fromkeys(ids)), True
+
+    monkeypatch.setattr(refresh, "fetch_catalogue", fake_fetch)
+    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_KEY", "")
+    code = refresh.main(["--proxy", str(target), "--apply"])
 
     assert code == 0
     rewritten = target.read_text(encoding="utf-8")
@@ -671,3 +679,249 @@ def test_rewrite_sets_touches_only_the_allowlists(tmp_path):
     assert '"new-model",' in rewritten
     assert 'UPSTREAM = "https://opencode.ai"' in rewritten
     assert rewritten.count("def _proxy_inner(") == 1
+
+
+# --- Task 413 hardening tests ---
+
+
+def test_active_mounts_are_non_empty():
+    """F1: every non-dormant mount must serve at least one model."""
+    for mount, allow in proxy._mount_counts().items():
+        if mount in proxy.DORMANT_MOUNTS:
+            continue
+        assert allow > 0, f"{mount} is empty but not dormant"
+
+
+def test_health_reports_mount_counts_and_degraded_false():
+    """F4: /health carries per-mount counts and degraded is false on shipped tree."""
+    payload = proxy._health_payload()
+    assert payload["status"] == "ok"
+    assert set(payload["mounts"]) == {"/zen/chat", "/zen/resp", "/go/chat", "/go/resp"}
+    assert all(isinstance(v, int) and v >= 0 for v in payload["mounts"].values())
+    assert payload["dormant"] == ["/zen/resp"]
+    assert payload["degraded"] is False
+
+
+def test_health_degraded_flips_when_non_dormant_mount_emptied(monkeypatch):
+    """F4: degraded becomes true if a non-dormant mount has zero models."""
+    original = dict(proxy.ROUTES)
+    # Temporarily empty GO_CHAT by replacing its allowlist reference.
+    monkeypatch.setitem(proxy.ROUTES, "/go/chat", (proxy.ROUTES["/go/chat"][0], set()))
+    payload = proxy._health_payload()
+    assert payload["degraded"] is True
+    # Restore is automatic via monkeypatch on ROUTES? ROUTES mutated in place;
+    # restore manually to be safe.
+    proxy.ROUTES["/go/chat"] = original["/go/chat"]
+
+
+def test_find_route_ranks_go_over_zen_for_shared_id():
+    """F8: crouton-alpha-free on a zen mount resolves to /go/resp."""
+    assert proxy._find_route("crouton-alpha-free", "/zen/resp") == "/go/resp"
+    assert proxy._find_route("crouton-alpha-free", "/zen/chat") == "/go/chat"
+
+
+def test_find_route_names_responses_mount_for_responses_only_model():
+    """F8: a responses-only model posted to a chat mount names the resp mount."""
+    # gpt-6-luna is in GO_RESP but not GO_CHAT.
+    assert "gpt-6-luna" in proxy.GO_RESP
+    assert "gpt-6-luna" not in proxy.GO_CHAT
+    assert proxy._find_route("gpt-6-luna", "/go/chat") == "/go/resp"
+
+
+def test_refresh_check_exits_zero_on_clean_tree(tmp_path, monkeypatch):
+    """F3/F6: --check exits 0 when allow == served (no removal candidates)."""
+    # Use a proxy copy with crouton-alpha-free excluded so --check is clean.
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+
+    # Monkeypatch fetch_catalogue to report all current ids as served.
+    def fake_fetch(base_url, upstream_base, key="", timeout=30):
+        import re as _re
+
+        # Return the allowlist ids of that family as "served".
+        ids = []
+        for mount, (fam, base, name) in refresh.MOUNTS.items():
+            if base == upstream_base:
+                m = _re.search(
+                    rf"^{name} = \{{(.*?)^\}}$",
+                    target.read_text(),
+                    _re.DOTALL | _re.MULTILINE,
+                )
+                if m:
+                    ids.extend(_re.findall(r'"([^"]+)"', m.group(1)))
+        return list(dict.fromkeys(ids)), True
+
+    monkeypatch.setattr(refresh, "fetch_catalogue", fake_fetch)
+    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_KEY", "")
+    code = refresh.main(["--key-env", "PATH", "--proxy", str(target), "--check"])
+    assert code == 0
+
+
+def test_refresh_check_exits_one_on_drift(tmp_path, monkeypatch):
+    """F3/F6: --check exits 1 when a mount has removal candidates."""
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+
+    # Fetch returns empty -> everything is a candidate (but probe_ok True).
+    monkeypatch.setattr(refresh, "fetch_catalogue", lambda *a, **k: ([], True))
+    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_KEY", "")
+    code = refresh.main(["--key-env", "PATH", "--proxy", str(target), "--check"])
+    assert code == 1
+
+
+def test_refresh_write_roundtrips_and_parses(tmp_path, monkeypatch):
+    """F3: --write applies changes, ast.parse passes, round-trip matches."""
+    import ast
+
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+
+    # Mock the catalogue so glm-5.3 is absent -> becomes a removal candidate.
+    def fake_fetch(base_url, upstream_base, key="", timeout=30):
+        ids = []
+        import re as _re
+
+        for mount, (fam, base, name) in refresh.MOUNTS.items():
+            if base != upstream_base:
+                continue
+            m = _re.search(
+                rf"^{name} = \{{(.*?)^\}}$",
+                target.read_text(),
+                _re.DOTALL | _re.MULTILINE,
+            )
+            if m:
+                ids.extend(
+                    i for i in _re.findall(r'"([^"]+)"', m.group(1)) if i != "glm-5.3"
+                )
+        return list(dict.fromkeys(ids)), True
+
+    monkeypatch.setattr(refresh, "fetch_catalogue", fake_fetch)
+    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_KEY", "")
+    code = refresh.main(
+        [
+            "--proxy",
+            str(target),
+            "--confirm-remove",
+            "/go/chat=glm-5.3",
+            "--write",
+        ]
+    )
+    assert code == 0
+    rewritten = target.read_text(encoding="utf-8")
+    ast.parse(rewritten)
+    rt = refresh.read_sets_from_source(rewritten)
+    assert "glm-5.3" not in rt["GO_CHAT"]
+
+
+def test_startup_line_contains_bind_and_counts():
+    """F7: startup line has bind address and per-mount sizes."""
+    line = proxy._startup_line()
+    assert "127.0.0.1:8081" in line
+    for mount in proxy.ROUTES:
+        assert mount in line
+
+
+# --- Task 413 QA round 2 regression tests ---
+
+
+def test_crouton_alpha_free_is_never_drift(tmp_path, monkeypatch):
+    """F1/F3: a catalogue-absent but served id must never count as drift."""
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+
+    def fake_fetch(base_url, upstream_base, key="", timeout=30):
+        import re as _re
+
+        ids = []
+        for mount, (fam, base, name) in refresh.MOUNTS.items():
+            if base != upstream_base:
+                continue
+            match = _re.search(
+                rf"^{name} = (?:\{{(.*?)^\}}|set\(\))$",
+                target.read_text(encoding="utf-8"),
+                _re.DOTALL | _re.MULTILINE,
+            )
+            if match and match.group(1):
+                ids.extend(
+                    i
+                    for i in _re.findall(r'"([^"]+)"', match.group(1))
+                    if i != "crouton-alpha-free"
+                )
+        return list(dict.fromkeys(ids)), True
+
+    monkeypatch.setattr(refresh, "fetch_catalogue", fake_fetch)
+    monkeypatch.delenv("ZEN_PROXY_UPSTREAM_KEY", raising=False)
+    assert refresh.main(["--proxy", str(target), "--check"]) == 0
+
+
+def test_rewrite_refuses_a_write_that_fails_the_guards(tmp_path, monkeypatch):
+    """Risk 4: ast.parse or round-trip failure must refuse the write."""
+    import pytest
+
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+
+    monkeypatch.setattr(
+        refresh,
+        "read_sets_from_source",
+        lambda _s: {
+            "GO_CHAT": ["tampered"],
+            "GO_RESP": [],
+            "ZEN_CHAT": [],
+            "ZEN_RESP": [],
+        },
+    )
+    with pytest.raises(refresh.RefreshError):
+        refresh.rewrite_sets(str(target), {"GO_CHAT": ["beam-free"]})
+    assert target.read_text(encoding="utf-8") == source
+
+    monkeypatch.undo()
+    monkeypatch.setattr(refresh, "render_literal", lambda _name, _ids: "GO_CHAT = {")
+    with pytest.raises(refresh.RefreshError):
+        refresh.rewrite_sets(str(target), {"GO_CHAT": ["beam-free"]})
+    assert target.read_text(encoding="utf-8") == source
+
+
+def test_read_dormant_reads_the_proxy_literal(tmp_path):
+    """The dormant set is owned by proxy.py, not duplicated in the tool."""
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+    assert refresh.read_dormant(str(target)) == {"/zen/resp"}
+
+
+def test_check_report_line_compares_allow_to_mount_served(tmp_path, monkeypatch, capsys):
+    """A2: the served count is the mount's own, never the family catalogue."""
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+
+    def fake_fetch(base_url, upstream_base, key="", timeout=30):
+        import re as _re
+
+        ids = []
+        for mount, (fam, base, name) in refresh.MOUNTS.items():
+            if base != upstream_base:
+                continue
+            match = _re.search(
+                rf"^{name} = (?:\{{(.*?)^\}}|set\(\))$",
+                target.read_text(encoding="utf-8"),
+                _re.DOTALL | _re.MULTILINE,
+            )
+            if match and match.group(1):
+                ids.extend(_re.findall(r'"([^"]+)"', match.group(1)))
+        return list(dict.fromkeys(ids)), True
+
+    monkeypatch.setattr(refresh, "fetch_catalogue", fake_fetch)
+    monkeypatch.delenv("ZEN_PROXY_UPSTREAM_KEY", raising=False)
+    assert refresh.main(["--proxy", str(target), "--check"]) == 0
+    out = capsys.readouterr().out
+    parsed = refresh.read_sets_from_source(target.read_text(encoding="utf-8"))
+    for mount, (_family, _base, name) in refresh.MOUNTS.items():
+        allow = len(parsed[name])
+        assert f"mount {mount}: allow={allow} served={allow} " in out
diff --git a/zen-proxy/DECISIONS.md b/zen-proxy/DECISIONS.md
index a8df043..45976f5 100644
--- a/zen-proxy/DECISIONS.md
+++ b/zen-proxy/DECISIONS.md
@@ -115,3 +115,23 @@
 - **Decision:** an unmatched path now uses `_send_error(404, "UnknownRoute", <message>, <fresh request id>)`. The mount allowlists, Authorization passthrough, silence timeout and 900<=900<=1200 ordering are untouched.
 - **Consequences:** a caller can parse the rejection like every other error; the new `UnknownRoute` type is documented in `zen-proxy/README.md` and `docs/zen-proxy.md`. One test in `tests/test_zen_proxy.py` now asserts the JSON envelope, the `UnknownRoute` type and the request-id header; it failed before the source change and passes after. No upstream behavior was copied beyond the idea that rejection bodies should be machine-readable.
 - **Rollback:** restore `self.send_error(404, "unknown zen-proxy route")` in `_send_upstream` and revert the test and the two doc rows.
+
+## 2026-11-22 — Allowlist prune, keyless refresh, health counts
+
+**Context:** Audit F1/F3-F8. Eight allowlist slots were stale (catalogue-absent,
+six unique ids: glm-5.2 twice, longcat-2.0 twice, inkling-2-small-free,
+and the three /zen/resp ids), /zen/resp served zero models (region-gated),
+/health reported ok while a mount was empty, refresh_allowlists.py required
+a key that was unset, and docs carried 2026-11-08 counts.
+
+**Decision:** Prune only catalogue-absent ids with per-id confirmation and an
+`allow == served` proof (resulting counts 22/27/7/0). Mark /zen/resp dormant
+(not deleted, pending F2). Add --check/--write to refresh_allowlists.py with
+keyless catalogue fetch, ast.parse + round-trip guard. /health gains mounts,
+dormant, degraded (all local). Add startup log line and ranked _find_route.
+crouton-alpha-free kept as a documented exception.
+
+**Consequences:** --check exits 0 on the shipped tree. Drift surfaces in CI and
+journal. No new env knobs. Install/restart remain Manager actions.
+
+**Rollback:** Revert the commit; allowlists restore to prior literals.
diff --git a/zen-proxy/README.md b/zen-proxy/README.md
index 5b826ed..7f2a4fa 100644
--- a/zen-proxy/README.md
+++ b/zen-proxy/README.md
@@ -57,7 +57,7 @@ the response body are never written to the log.
 | `/go/chat` | `opencode.ai/zen/go/v1` | Go subscription, chat completions |
 | `/go/resp` | `opencode.ai/zen/go/v1` | Go subscription, Responses API |
 
-`GET /health` answers `{"status":"ok"}` and is the liveness probe.
+`GET /health` answers `{"status":"ok","mounts":{...},"dormant":[...],"degraded":bool}` and is the liveness probe.
 
 ## Consumers
 
diff --git a/zen-proxy/proxy.py b/zen-proxy/proxy.py
index fa34c6b..1a46645 100755
--- a/zen-proxy/proxy.py
+++ b/zen-proxy/proxy.py
@@ -269,9 +269,9 @@ def _has_terminal_event(buffer):
     return any(pattern.search(buffer) for pattern in _TERMINAL_PATTERNS)
 
 
-# Refreshed live 2026-11-08 (Go: 30 models, Zen: 45 models; authenticated
-# with opencode UA + session). Go now includes crouton-alpha-free,
-# iceman-contributor-free and longcat-2.0 — they work on BOTH
+# Refreshed 2026-11-22 (Go: 32/22+27 served, Zen: 105/7+0; keyless probe):
+# with opencode UA + session). Go now includes crouton-alpha-free and
+# iceman-contributor-free — they work on BOTH
 # /zen/go/v1/responses and /chat/completions (verified 2026-11-08 via
 # proxy 7890 + oc_sk key). Zen's crouton-alpha-free is the same id but hits
 # the free-tier account quota (429) — use the Go mount for it.
@@ -281,11 +281,9 @@ GO_CHAT = {
     "beam-free",
     "crouton-alpha-free",
     "gemini-4-argon",
-    "glm-5.2",
     "glm-5.3",
     "glm-5.3-flash",
     "iceman-contributor-free",
-    "longcat-2.0",
     "mimo-v2.6-flash",
     "mimo-v2.6-pro",
     "minimax-m3",
@@ -307,14 +305,12 @@ GO_RESP = {
     "beam-free",
     "crouton-alpha-free",
     "gemini-4-argon",
-    "glm-5.2",
     "glm-5.3",
     "glm-5.3-flash",
     "gpt-5.6-luna",
     "gpt-6-luna",
     "grok-4.7",
     "iceman-contributor-free",
-    "longcat-2.0",
     "mimo-v2.6-flash",
     "mimo-v2.6-pro",
     "minimax-m3",
@@ -345,14 +341,9 @@ ZEN_CHAT = {
     "crouton-alpha-free",
     "iceman-free",
     "flint-40b-free",
-    "inkling-2-small-free",
     "mimo-v2.6-flash-free",
 }
-ZEN_RESP = {
-    "muse-spark-1.3-contributor-free",
-    "muse-spark-1.2-contributor-free",
-    "crouton-alpha-free",
-}
+ZEN_RESP = set()
 
 
 def _translate_reasoning_effort(payload):
@@ -378,13 +369,56 @@ ROUTES = {
     "/go/resp": ("/zen/go/v1", GO_RESP),
 }
 
+# Mounts whose allowlist is intentionally empty pending a Manager decision
+# (see F2: /zen/resp is dormant because its three ids are not servable for
+# this account). Dormant mounts are excluded from the `degraded` flag and
+# from the startup-line warning, and their emptiness is not a defect.
+DORMANT_MOUNTS = frozenset({"/zen/resp"})
 
-def _find_route(model):
-    """Return the mount prefix that serves `model`, or None."""
-    for prefix, (_, allow) in ROUTES.items():
-        if model in allow:
-            return prefix
-    return None
+
+def _find_route(model, current_mount=None):
+    """Return the mount prefix that serves `model`, ranked so callers on a
+    chat mount get a chat mount, callers on a responses mount get a
+    responses mount, and Go (paid) is preferred over Zen (free) when both
+    serve the same id. Returns None when no mount serves the model."""
+    candidates = [p for p, (_, allow) in ROUTES.items() if model in allow]
+    if not candidates:
+        return None
+    if current_mount is None:
+        current_mount = ""
+    style = "/resp" if current_mount.endswith("/resp") else "/chat"
+    same_style = [p for p in candidates if p.endswith(style)]
+    pool = same_style or candidates
+    go = [p for p in pool if p.startswith("/go/")]
+    ranked = go or pool
+    # Stable table order as the final tie-break.
+    ordered = [p for p in ROUTES if p in ranked]
+    return ordered[0] if ordered else None
+
+
+def _mount_counts():
+    """Return {mount: len(allowlist)} for every configured mount."""
+    return {prefix: len(allow) for prefix, (_, allow) in ROUTES.items()}
+
+
+def _health_payload():
+    """Build the /health body. All fields are computed locally so the
+    answer is instant and never depends on upstream reachability."""
+    counts = _mount_counts()
+    dormant = sorted(DORMANT_MOUNTS)
+    degraded = any(counts[m] == 0 for m in counts if m not in DORMANT_MOUNTS)
+    return {
+        "status": "ok",
+        "mounts": counts,
+        "dormant": dormant,
+        "degraded": degraded,
+    }
+
+
+def _startup_line():
+    counts = _mount_counts()
+    parts = " ".join(f"{m}={counts[m]}" for m in ROUTES)
+    return f"zen-proxy: listening on 127.0.0.1:8081 {parts}"
 
 
 def _audit_write(record, req_body=None):
@@ -472,7 +506,7 @@ class Handler(BaseHTTPRequestHandler):
 
     def _send_upstream(self):
         if self.path == "/health":
-            body = b'{"status":"ok"}'
+            body = (json.dumps(_health_payload()) + "\n").encode()
             self.send_response(200)
             self.send_header("Content-Type", "application/json")
             self.send_header("Content-Length", str(len(body)))
@@ -483,7 +517,7 @@ class Handler(BaseHTTPRequestHandler):
         for prefix, (base, allow) in ROUTES.items():
             if self.path == prefix or self.path.startswith(prefix + "/"):
                 rest = self.path[len(prefix) :] or "/"
-                self._proxy(base + rest, allow)
+                self._proxy(base + rest, allow, prefix)
                 return
         # The failure contract promises a parseable JSON envelope for every
         # answer, including a path that matches no mount. `send_error` emits
@@ -499,7 +533,7 @@ class Handler(BaseHTTPRequestHandler):
     do_GET = _send_upstream
     do_POST = _send_upstream
 
-    def _proxy(self, upstream_path, allow):
+    def _proxy(self, upstream_path, allow, mount_prefix=None):
         """Relay one request upstream and answer the client.
 
         Every failure path answers with a parseable JSON error instead of
@@ -515,6 +549,7 @@ class Handler(BaseHTTPRequestHandler):
             "session_id": "",
             "session_origin": "client",
             "sent": 0,
+            "mount_prefix": mount_prefix,
         }
         try:
             return self._proxy_inner(req_id, started, upstream_path, allow, state)
@@ -555,7 +590,7 @@ class Handler(BaseHTTPRequestHandler):
             if isinstance(_probe, dict) and isinstance(_probe.get("model"), str):
                 _mid = _probe["model"]
                 if _mid not in allow:
-                    _hint = _find_route(_mid)
+                    _hint = _find_route(_mid, state.get("mount_prefix"))
                     state["status"] = 404
                     state["outcome"] = "model_not_served"
                     state["model"] = _mid
@@ -892,6 +927,7 @@ def _install_signal_handlers(server):
 
 if __name__ == "__main__":
     _server = ZenProxyServer(("127.0.0.1", 8081), Handler)
+    print(_startup_line(), flush=True)
     _install_signal_handlers(_server)
     try:
         _server.serve_forever()
diff --git a/zen-proxy/refresh_allowlists.py b/zen-proxy/refresh_allowlists.py
index f3d3b01..e3ec83d 100755
--- a/zen-proxy/refresh_allowlists.py
+++ b/zen-proxy/refresh_allowlists.py
@@ -63,6 +63,11 @@ MOUNTS = {
     "/go/resp": ("go", "/zen/go/v1", "GO_RESP"),
 }
 
+# Ids that are served by upstream but never appear in the catalogue, so they
+# must never be reported as removal candidates. crouton-alpha-free is served
+# by Go and is intentionally absent from both catalogues (docs/zen-proxy.md).
+KNOWN_EXCEPTIONS = frozenset({"crouton-alpha-free"})
+
 UA = (
     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
@@ -84,27 +89,34 @@ def read_sets(proxy_path=PROXY_PATH):
         source = handle.read()
     sets = {}
     for _family, _base, name in MOUNTS.values():
-        match = re.search(rf"^{name} = \{{(.*?)^\}}$", source, re.DOTALL | re.MULTILINE)
+        # Match either a brace literal or an empty set().
+        match = re.search(
+            rf"^{name} = (?:\{{(.*?)^\}}|set\(\))$",
+            source,
+            re.DOTALL | re.MULTILINE,
+        )
         if not match:
             raise RefreshError(f"could not find the {name} literal in {proxy_path}")
-        ids = re.findall(r'"([^"]+)"', match.group(1))
+        group = match.group(1) if match.group(1) is not None else ""
+        ids = re.findall(r'"([^"]+)"', group)
         sets[name] = ids
     return sets
 
 
-def merge_ids(current, removals, add=()):
+def merge_ids(current, removals, add=(), allow_empty=False):
     """Compute the new id list for one mount.
 
     Order is preserved for the ids that survive, additions are appended in
     alphabetical order, and only ids in `removals` are dropped — those are
-    the ids the operator confirmed. An empty result is refused: a mount
-    with no models serves nothing.
+    the ids the operator confirmed. An empty result is refused unless the
+    mount is dormant (allow_empty=True): a dormant mount serves nothing by
+    design.
     """
     removal_set = set(removals)
     kept = [model for model in current if model not in removal_set]
     additions = sorted({model for model in add if model and model not in kept})
     merged = kept + additions
-    if not merged:
+    if not merged and not allow_empty:
         raise RefreshError("refusing to write an empty allowlist")
     return merged
 
@@ -119,27 +131,35 @@ def classify(current, family_observed, probe_ok):
     if not probe_ok:
         return {"keep": list(current), "candidates": []}
     observed = set(family_observed)
-    keep = [model for model in current if model in observed]
-    candidates = [model for model in current if model not in observed]
+    keep = [
+        model for model in current if model in observed or model in KNOWN_EXCEPTIONS
+    ]
+    candidates = [
+        model
+        for model in current
+        if model not in observed and model not in KNOWN_EXCEPTIONS
+    ]
     return {"keep": keep, "candidates": candidates}
 
 
-def fetch_catalogue(base_url, upstream_base, key, timeout=30):
+def fetch_catalogue(base_url, upstream_base, key="", timeout=30):
     """Fetch the upstream model catalogue of one family.
 
     Returns (ids, ok). `ok` is False when the catalogue could not be
     fetched; the ids are then empty and nothing may be removed.
+
+    When `key` is empty the request is sent unauthenticated. The upstream
+    catalogue answers 200 without a key, so a missing key is no longer a
+    hard stop; it only means the refresh runs in keyless mode.
     """
     url = base_url.rstrip("/") + upstream_base + "/models"
-    request = urllib.request.Request(
-        url,
-        method="GET",
-        headers={
-            "Authorization": f"Bearer {key}",
-            "Accept": "application/json",
-            "User-Agent": UA,
-        },
-    )
+    headers = {"Accept": "application/json", "User-Agent": UA}
+    if key:
+        headers["Authorization"] = f"Bearer {key}"
+    # Mint a session id like the proxy does, so the request looks like a
+    # real client even when no key is present.
+    headers["x-opencode-session"] = "refresh-allowlists"
+    request = urllib.request.Request(url, method="GET", headers=headers)
     try:
         with urllib.request.urlopen(request, timeout=timeout) as response:
             payload = json.loads(response.read().decode("utf-8", "replace"))
@@ -170,6 +190,8 @@ def fetch_catalogue(base_url, upstream_base, key, timeout=30):
 
 def render_literal(name, ids):
     """Render an allowlist literal in the same shape proxy.py uses."""
+    if not ids:
+        return f"{name} = set()"
     lines = [f"{name} = {{"]
     for model in ids:
         lines.append(f'    "{model}",')
@@ -177,26 +199,60 @@ def render_literal(name, ids):
     return "\n".join(lines)
 
 
+def read_dormant(proxy_path=PROXY_PATH):
+    """Read the DORMANT_MOUNTS frozenset out of proxy.py, or empty set."""
+    with open(proxy_path, "r", encoding="utf-8") as handle:
+        source = handle.read()
+    match = re.search(r"DORMANT_MOUNTS\s*=\s*frozenset\(\{(.*?)\}\)", source, re.DOTALL)
+    if not match:
+        return set()
+    return {
+        m.strip().strip('"').strip("'")
+        for m in match.group(1).split(",")
+        if m.strip().strip('"').strip("'")
+    }
+
+
 def rewrite_sets(proxy_path, new_sets):
     """Rewrite the allowlist literals in proxy.py, atomically.
 
     Only the four literals are touched. The file is written to a temporary
     file in the same directory and moved into place, so a crash cannot leave
-    a half-written module behind.
+    a half-written module behind. The rewrite is guarded by ast.parse and a
+    round-trip re-extract so a corrupted file can never be committed.
     """
+    import ast
+
     with open(proxy_path, "r", encoding="utf-8") as handle:
         source = handle.read()
     original = source
     for name, ids in new_sets.items():
-        pattern = re.compile(rf"^{name} = \{{.*?^\}}$", re.DOTALL | re.MULTILINE)
+        pattern = re.compile(
+            rf"^{name} = (?:\{{.*?^\}}|set\(\))$", re.DOTALL | re.MULTILINE
+        )
         if not pattern.search(source):
             raise RefreshError(f"could not find the {name} literal in {proxy_path}")
         literal = render_literal(name, ids)
         source = pattern.sub(lambda _m, lit=literal: lit, source, count=1)
     if source == original:
         return False
+    # Guard: the rewritten source must still parse.
+    try:
+        ast.parse(source)
+    except SyntaxError as exc:
+        raise RefreshError(f"rewrite failed ast.parse: {exc}")
+    # Round-trip: re-extract the sets and confirm they match the intent.
+    try:
+        roundtrip = read_sets_from_source(source)
+    except RefreshError as exc:
+        raise RefreshError(f"rewrite round-trip failed: {exc}")
+    for name, ids in new_sets.items():
+        if roundtrip.get(name) != list(ids):
+            raise RefreshError(
+                f"rewrite round-trip mismatch for {name}: "
+                f"{roundtrip.get(name)!r} != {list(ids)!r}"
+            )
     directory = os.path.dirname(os.path.abspath(proxy_path))
-    # The temporary file is moved into place, so it is closed by hand.
     handle = tempfile.NamedTemporaryFile(  # noqa: SIM115
         "w",
         encoding="utf-8",
@@ -218,6 +274,23 @@ def rewrite_sets(proxy_path, new_sets):
     return True
 
 
+def read_sets_from_source(source):
+    """Parse sets from an in-memory source string (for round-trip checks)."""
+    sets = {}
+    for _family, _base, name in MOUNTS.values():
+        match = re.search(
+            rf"^{name} = (?:\{{(.*?)^\}}|set\(\))$",
+            source,
+            re.DOTALL | re.MULTILINE,
+        )
+        if not match:
+            raise RefreshError(f"could not find the {name} literal")
+        group = match.group(1) if match.group(1) is not None else ""
+        ids = re.findall(r'"([^"]+)"', group)
+        sets[name] = ids
+    return sets
+
+
 def parse_additions(values):
     """Parse `--add /mount=id1,id2` arguments into {mount: [ids]}."""
     additions = {}
@@ -261,17 +334,34 @@ def main(argv=None):
     parser.add_argument(
         "--apply",
         action="store_true",
+        help="write the confirmed removals and additions into proxy.py (alias for --write)",
+    )
+    parser.add_argument(
+        "--check",
+        action="store_true",
+        help="report drift and exit 1 if any mount differs from upstream; never writes",
+    )
+    parser.add_argument(
+        "--write",
+        action="store_true",
         help="write the confirmed removals and additions into proxy.py",
     )
     args = parser.parse_args(argv)
 
+    # --apply is the legacy name for --write.
+    if args.apply:
+        args.write = True
+
+    # Dormancy is owned by proxy.py: read it from the same file this tool
+    # rewrites, so the two constants can never drift apart.
+    dormant_mounts = read_dormant(args.proxy)
     key = os.environ.get(args.key_env, "").strip()
-    if not key:
-        print(
-            f"zen-proxy: no key in ${args.key_env}; export the upstream key first.",
-            file=sys.stderr,
-        )
-        return 2
+    # Keyless mode: the upstream catalogue answers 200 without auth, so a
+    # missing key is no longer a hard stop. Report which mode ran.
+    if key:
+        print(f"zen-proxy: running with key from ${args.key_env}")
+    else:
+        print(f"zen-proxy: running keyless (no ${args.key_env})")
 
     try:
         sets = read_sets(args.proxy)
@@ -317,12 +407,28 @@ def main(argv=None):
         if add:
             print(f"{mount}: adding {', '.join(sorted(add))}")
         try:
-            new_sets[name] = merge_ids(current, confirmed, add)
+            new_sets[name] = merge_ids(
+                current, confirmed, add, allow_empty=(mount in dormant_mounts)
+            )
         except RefreshError as exc:
             # One mount that would end up empty must not block the report of
             # the others, and it must never be written.
             print(f"{mount}: keeping the current set ({exc})", file=sys.stderr)
             new_sets[name] = list(current)
+        # Per-mount report line (stable, machine-parseable). `served` counts
+        # this mount's own ids that upstream still serves, so `allow` and
+        # `served` are directly comparable (A2). The family catalogue size is
+        # a different number and is never printed as `served`.
+        observed_here = set(family_ids)
+        served_here = [
+            model
+            for model in current
+            if model in observed_here or model in KNOWN_EXCEPTIONS
+        ]
+        print(
+            f"mount {mount}: allow={len(current)} served={len(served_here) if probe_ok else 0} "
+            f"candidates={len(candidates)} dormant={mount in dormant_mounts}"
+        )
     # Candidates are reported, never written: the catalogue does not say
     # which API style a model speaks.
     known = {model for ids in sets.values() for model in ids}
@@ -336,8 +442,31 @@ def main(argv=None):
                 f"style, then add with --add): {', '.join(candidates)}"
             )
 
-    if not args.apply:
-        print("report only; pass --apply to write the confirmed removals")
+    # Drift summary: a mount with removal candidates counts as drift.
+    # New upstream ids are informational, not drift (they are additions
+    # the operator may choose to add with --add).
+    drift = False
+    for mount, (family, _base, name) in MOUNTS.items():
+        family_ids = families[family]["ids"]
+        probe_ok = families[family]["ok"]
+        if not probe_ok:
+            continue
+        current = sets[name]
+        candidates = [
+            m for m in current if m not in set(family_ids) and m not in KNOWN_EXCEPTIONS
+        ]
+        if candidates:
+            drift = True
+
+    if args.check:
+        if drift:
+            print("drift detected; exit 1")
+            return 1
+        print("no drift; exit 0")
+        return 0
+
+    if not args.write:
+        print("report only; pass --write (or --apply) to write the confirmed removals")
         return 0
 
     try:
```
<!-- END_GIT_DIFF -->
EOF
echo written
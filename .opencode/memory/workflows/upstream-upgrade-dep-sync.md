---
created_at: '2026-10-15T05:38:49.927703+00:00'
status: active
tags: []
updated_at: '2026-10-15T05:38:49.927715+00:00'
---

# Upstream Upgrade Dependency Sync (Manager standing rule 2026-10-15)

After EVERY upstream git-pull upgrade of a deployed server (telegram-mcp, HQ MCP singletons), sync the venv dependencies BEFORE restarting the service. Upstream code often adds imports (incident: telegram-mcp pull added `from pypdf import PdfReader`; venv lacked pypdf and the service crash-looped 9000+ times).

Procedure: 1) `systemctl --user stop <service>` to halt the crash loop. 2) Diff new imports against the venv (`python -c import check` per top-level module, using correct import names: PIL not pillow, pythonjsonlogger not python-json-logger). 3) Install with `uv pip install --python <venv>/bin/python <pkgs>` covering pyproject `dependencies`. 4) Verify every declared import resolves. 5) Start the service and confirm NRestarts=0 plus a clean port response. Never run telegram's own pytest suite (live-network tests hang; memory rule).
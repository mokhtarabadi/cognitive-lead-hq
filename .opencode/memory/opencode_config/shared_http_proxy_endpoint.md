---
created_at: "2026-11-25T23:35:38.694312+00:00"
status: active
tags: []
updated_at: "2026-11-25T23:35:38.694385+00:00"
---

Use http://100.74.8.111:7890 as the shared HTTP/HTTPS egress proxy for OpenChamber, blowsh, and zen-bridge. OpenChamber reads it from ~/.config/openchamber/startup.env, zen reads it from ~/.config/opencode/.env, and blowsh receives PROXY_TYPE=http with PROXY_HOST=100.74.8.111 and PROXY_PORT=7890. Keep loopback addresses in NO_PROXY/PROXY_BYPASS so local service traffic remains direct.

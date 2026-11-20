---
tags: [blowsh, docker, images, opencode]
---

# Blowsh image policy: always pull the auto-built remote :latest image

Manager ruling 2026-11-20: blowsh always uses `ghcr.io/mokhtarabadi/blowsh-mcp:latest`, the auto-built image published by the GitHub image repo. That repo builds `:latest` automatically, so the remote tag is always current. Never build blowsh locally from a checkout, never pin a version tag, and do not run a blowsh rebuild step during upgrades — just pull the remote `:latest` image. The Cloudflare WARP proxy remains mandatory at deployment, wired through the PROXY_* env vars on blowsh-singleton (see `docs/blowsh-warp-proxy.md`). The running server needs that config; the agent-facing blowsh skill does not.

# Production Deployment Guide (Task 148)

Run the Cognitive Loop Engine 24/7 via Docker Compose or systemd.

## Docker Compose Setup

```bash
cp .env.example .env  # TELEGRAM_BOT_TOKEN, model API keys
docker compose -f deploy/docker-compose.yml config  # validate
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml logs -f cognitive-loop
```

## Systemd Unit Setup

```bash
sudo useradd -r -m cognitive || true
sudo mkdir -p /opt/cognitive-lead-hq /etc/cognitive-loop
sudo cp deploy/cognitive-loop.service /etc/systemd/system/
sudo cp .env /etc/cognitive-loop/env  # 0600, root:cognitive
sudo systemctl daemon-reload
sudo systemctl enable --now cognitive-loop.service
journalctl -u cognitive-loop.service -f
```

## Log Rotation

- Docker: json-file default rotation via daemon.json, plus `loop-engine/logs/` volume.
- Systemd: `StandardOutput=journal`; cap with `SystemMaxUse=500M` in journald.conf.

## Environment Variables

| Var | Required | Purpose |
| --- | -------- | ------- |
| TELEGRAM_BOT_TOKEN | yes | Telegram approval gateway |
| OPENROUTER_API_KEY / provider keys | yes | LLM routing |
| SENTRY_DSN | no | Error reporting (optional) |
| TZ | no | Defaults UTC |

Daemon runs without containers: `python3 loop-engine/daemon.py`.

## Healthchecks

- Compose: `python3 loop-engine/healthcheck.py` every 30s.
- Manual: `python3 loop-engine/healthcheck.py --dry-run` (exit 0) or full DB probe (exit 0 healthy, 1 error).

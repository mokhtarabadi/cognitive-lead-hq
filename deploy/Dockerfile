# syntax=docker/dockerfile:1
# Cognitive Loop Engine — hardened multi-stage build (Task 148)
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY loop-engine/pyproject.toml loop-engine/pyproject.toml
RUN python -m venv /opt/venv \
  && /opt/venv/bin/pip install --no-cache-dir -e ./loop-engine || /opt/venv/bin/pip install --no-cache-dir pydantic litellm watchdog python-telegram-bot pyyaml

FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 TZ=UTC PATH="/opt/venv/bin:$PATH"
RUN useradd -m -u 10001 appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY loop-engine/ loop-engine/
COPY system-prompt.md AGENTS.md ./
COPY tasks/ tasks/
USER appuser
CMD ["python", "loop-engine/daemon.py"]

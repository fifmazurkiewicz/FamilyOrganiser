#!/bin/sh
# API entrypoint (Hetzner / Docker Compose). Port z $PORT, domyślnie 8080.
set -eu

mkdir -p /data
chmod 775 /data || true

PORT="${PORT:-8080}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

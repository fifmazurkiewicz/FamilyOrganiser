#!/bin/sh
# API entrypoint (Render Docker / local Compose). Port from $PORT, default 8080.
# Alembic is not run here — set a Render start command or extend this script.
set -eu

mkdir -p /data
chmod 775 /data || true

PORT="${PORT:-8080}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

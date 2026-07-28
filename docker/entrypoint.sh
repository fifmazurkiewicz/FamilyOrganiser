#!/bin/sh
set -eu

mkdir -p /data
chmod 775 /data || true

PORT="${PORT:-8080}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

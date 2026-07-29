#!/usr/bin/env bash
# Deploy backendu na VPS (lokalnie albo przez GitHub Actions → SSH).
# Gdy DATABASE_URL jest w środowisku (z GitHub Secrets), zapisuje .env na dysku VPS.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.prod.yml --env-file .env)

sync_env_from_ci() {
  if [[ -z "${DATABASE_URL:-}" ]]; then
    return 0
  fi
  echo "==> zapis .env z GitHub Secrets"
  umask 077
  python3 - <<'PY'
import os
from pathlib import Path

keys = [
    "DATABASE_URL",
    "SUPABASE_URL",
    "SUPABASE_JWT_SECRET",
    "SUPABASE_JWT_AUDIENCE",
    "CORS_ORIGINS_STR",
    "SECRET_KEY",
    "ADMIN_EMAIL",
    "ADMIN_PASSWORD",
    "PORT",
]
lines = []
for key in keys:
    val = os.environ.get(key)
    if val is None or val == "":
        continue
    if key == "DATABASE_URL":
        val = val.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
            "postgres://", "postgresql+asyncpg://", 1
        )
    lines.append(f"{key}={val}")
if not os.environ.get("PORT"):
    lines.append("PORT=8080")
Path(".env").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote .env ({len(lines)} keys)")
PY
}

echo "==> git pull"
git fetch origin main
git checkout main
git pull --ff-only origin main

sync_env_from_ci

if [[ ! -f .env ]]; then
  echo "Brak .env — dodaj GitHub Secrets (m.in. DATABASE_URL) albo utwórz .env na VPS." >&2
  exit 1
fi

echo "==> docker compose up --build"
"${COMPOSE[@]}" up -d --build

echo "==> alembic upgrade"
"${COMPOSE[@]}" exec -T backend alembic upgrade head

echo "==> healthcheck"
"${COMPOSE[@]}" exec -T backend curl -fsS "http://127.0.0.1:8080/api/health"

echo "==> OK"

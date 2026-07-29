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

echo "==> git sync (origin/main)"
git fetch origin main
git checkout -f main
git reset --hard origin/main

sync_env_from_ci

if [[ ! -f .env ]]; then
  echo "Brak .env — dodaj GitHub Secrets (m.in. DATABASE_URL) albo utwórz .env na VPS." >&2
  exit 1
fi

echo "==> docker compose up --build"
"${COMPOSE[@]}" up -d --build

echo "==> sprawdzenie hosta bazy (preflight)"
python3 - <<'PY'
import socket
import sys
from urllib.parse import urlparse

from pathlib import Path

text = Path(".env").read_text(encoding="utf-8")
db_url = ""
for line in text.splitlines():
    if line.startswith("DATABASE_URL="):
        db_url = line.split("=", 1)[1].strip()
        break
if not db_url:
    sys.exit(0)

parsed = urlparse(db_url.replace("postgresql+asyncpg://", "postgresql://", 1))
host = parsed.hostname or ""
port = parsed.port or 5432
print(f"DB host: {host}:{port}")

if "pooler.supabase.com" in host and port == 6543:
    print(
        "UWAGA: transaction pooler (:6543) psuje alembic/asyncpg (prepared statements).",
        "Użyj session poolera (:5432) w DATABASE_URL — Supabase → Database → Session pooler.",
        sep="\n",
        file=sys.stderr,
    )
    sys.exit(1)

if host.startswith("db.") and host.endswith(".supabase.co"):
    print(
        "UWAGA: direct connection (db.*.supabase.co) często pada na VPS bez IPv6.",
        "Użyj poolera w GitHub Secret DATABASE_URL, np.",
        "postgresql+asyncpg://postgres.<ref>:<haslo>@aws-0-<region>.pooler.supabase.com:6543/postgres",
        sep="\n",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
except socket.gaierror as exc:
    print(f"Błąd DNS dla {host}: {exc}", file=sys.stderr)
    sys.exit(1)

families = sorted({info[0] for info in infos})
print(f"DNS: {', '.join('IPv6' if fam == socket.AF_INET6 else 'IPv4' for fam in families)}")

reachable = False
for info in infos:
    fam, _, _, _, sockaddr = info
    label = "IPv6" if fam == socket.AF_INET6 else "IPv4"
    addr = (sockaddr[0], sockaddr[1])
    try:
        with socket.create_connection(addr, timeout=5):
            print(f"Połączenie TCP ({label}): OK")
            reachable = True
            break
    except OSError as exc:
        print(f"Połączenie TCP ({label}): {exc}", file=sys.stderr)

if not reachable:
    print(
        "Brak trasy do bazy — zaktualizuj DATABASE_URL na pooler Supabase (:6543).",
        file=sys.stderr,
    )
    sys.exit(1)
PY

echo "==> alembic upgrade"
"${COMPOSE[@]}" exec -T backend alembic upgrade head

echo "==> healthcheck"
"${COMPOSE[@]}" exec -T backend curl -fsS "http://127.0.0.1:8080/api/health"

echo "==> OK"

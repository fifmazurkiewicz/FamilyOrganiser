#!/usr/bin/env bash
# Kopia Postgres (Supabase) — lokalnie lub w GitHub Actions.
# Wymaga: DATABASE_URL (connection string z hasłem, bez asyncpg).
# Przykład: DATABASE_URL='postgresql://...' ./scripts/backup-supabase.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$ROOT/backups}"
mkdir -p "$OUT_DIR"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 1
fi

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump not found — install postgresql-client" >&2
  exit 1
fi

# SQLAlchemy async URL → standardowy URL dla pg_dump
PGURL="${DATABASE_URL/postgresql+asyncpg/postgresql}"
PGURL="${PGURL/postgres:/postgresql:}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
FILE="$OUT_DIR/familyorganiser-${STAMP}.sql.gz"

echo "==> pg_dump → $FILE"
pg_dump "$PGURL" | gzip > "$FILE"
ls -lh "$FILE"
echo "==> done"

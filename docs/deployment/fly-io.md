# Deploy na Fly.io (archiwum historyczne)

**Status:** nie jest kierunkiem produkcyjnym — produkcja: Vercel FE + Hetzner (Docker + Caddy).  
Katalog `archive/fly/` został **usunięty** z repo (2026-07-30). Ten dokument zostaje jako notatka historyczna.

Zob. [platform-architecture.md](platform-architecture.md).

**Ostatnia aktualizacja:** 2026-07-30

---

## Kontekst

Wczesny PoC zakładał all-in-one obraz z SQLite na volume Fly.io. Obecny root `Dockerfile` to **API-only** (port 8080, Postgres przez Supabase). Odtworzenie deployu na Fly wymagałoby osobnego `fly.toml` i ewentualnie historycznego Dockerfile.

## Pliki nadal w repo (API)

| Plik | Rola |
|------|------|
| `Dockerfile` (root) | API-only, port 8080 |
| `docker/entrypoint.sh` | Start uvicorn w kontenerze |
| `.dockerignore` | Mniejszy kontekst builda |

## Lokalny test obrazu API

```bash
docker build -t familyorganiser:api .
docker run --rm -p 8080:8080 \
  -e SECRET_KEY=dev \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e CORS_ORIGINS_STR=http://localhost:3000 \
  familyorganiser:api
```

Health: http://localhost:8080/api/health

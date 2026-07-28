# Deploy na Fly.io

**Ostatnia aktualizacja:** 2026-07-28

Jeden kontener: build Vite + FastAPI (uvicorn). SQLite na volume `/data`. HTTPS daje Fly.

## Pliki

| Plik | Rola |
|------|------|
| `Dockerfile` (root) | Multi-stage: frontend → deps → runtime |
| `fly.toml` | Region `waw`, port 8080, volume, healthcheck |
| `docker/entrypoint-fly.sh` | Katalog `/data` + port z `$PORT` |
| `.dockerignore` | Mniejszy kontekst builda |

## Wymagania

- Konto [fly.io](https://fly.io) + CLI: `powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"` (Windows)
- Zalogowanie: `fly auth login`

## Pierwszy deploy

```bash
# Z katalogu głównego repo
fly apps create familyorganiser   # jeśli nazwa zajęta — zmień app w fly.toml

fly volumes create familyorg_data --region waw --size 1

fly secrets set \
  SECRET_KEY="$(openssl rand -hex 32)" \
  ADMIN_EMAIL="admin@twoja-domena.pl" \
  ADMIN_PASSWORD="mocne-haslo" \
  CORS_ORIGINS_STR="https://familyorganiser.fly.dev"

fly deploy
```

Po deployu:

```bash
fly open
fly logs
fly status
```

Health: `https://<app>.fly.dev/api/health`

## Lokalny test obrazu

```bash
docker build -t familyorganiser:fly .
docker run --rm -p 8080:8080 \
  -e SECRET_KEY=dev \
  -e ADMIN_PASSWORD=admin \
  -e CORS_ORIGINS_STR=http://localhost:8080 \
  -v familyorg_data:/data \
  familyorganiser:fly
```

Otwórz http://localhost:8080

## Uwagi

- **SQLite + auto_stop:** maszyna może się wyłączać (`min_machines_running = 0`) — OK dla hobby; przy większym ruchu ustaw `min_machines_running = 1`.
- **Backup:** volume nie jest magiczny — okresowo `fly ssh console` + skopiuj `/data/familyorg.db` albo przejdź na Fly Postgres.
- **Nazwa app / region:** edytuj `fly.toml` (`app`, `primary_region`). Volume musi być w tym samym regionie.
- **CORS:** ustaw `CORS_ORIGINS_STR` na dokładny URL aplikacji (i custom domenę, jeśli dodasz).
- Dev lokalnie bez `STATIC_DIR` działa jak dotychczas (tylko API).

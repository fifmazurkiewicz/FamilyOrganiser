# Najtańszy deploy FamilyOrganiser

**Ostatnia aktualizacja:** 2026-07-28  
**Cel:** uruchomić aplikację (FastAPI + React + PostgreSQL) tanio, stabilnie i z HTTPS.

> Obecny `docker-compose.yml` jest pod **development** (`--reload`, `npm run dev`, montowane volume). Na serwer produkcyjny potrzebujesz wariantu produkcyjnego (build frontendu do plików statycznych + uvicorn bez `--reload`). Poniżej jest opis ścieżki i checklist — pliki produkcyjne warto dodać przed pierwszym deployem.

---

## Co trzeba hostować

| Warstwa | Rola | Uwagi kosztowe |
|---------|------|----------------|
| Frontend | React (Vite) | Po buildzie to tylko pliki statyczne — nie potrzebuje osobnego Node na produkcji |
| Backend | FastAPI / uvicorn | Lekki; 1–2 GB RAM wystarczy na małą grupę użytkowników |
| Baza | PostgreSQL | Wymagana na produkcji (SQLite tylko na lokalne testy) |
| Redis | — | W README wspomniany, ale aplikacja **nie wymaga** Redis do działania — nie dokładaj go „na zapas” |
| Proxy | nginx + HTTPS | Certyfikat Let's Encrypt = 0 zł |

**Szacunek zasobów (1–2 rodziny, mały ruch):** 2 vCPU, **4 GB RAM**, 40 GB dysku.

---

## Porównanie opcji (od najtańszej)

Ceny orientacyjne (EU, bez VAT, stan ~połowa 2026). Sprawdź aktualny cennik przed zakupem.

| Opcja | Koszt / mies. | Dla kogo | Plusy | Minusy |
|-------|---------------|----------|-------|--------|
| **Oracle Cloud Always Free** (VM Ampere) | **0 €** | Eksperyment / hobby | Darmowe 4 OCPU / 24 GB (w limicie Always Free) | Kapryśna rejestracja, limity, więcej roboty z ARM |
| **Hetzner Cloud** (np. CX22 / CX23) | **~4–6 €** | **Rekomendowane** | Prosto, stabilnie, dużo transferu, EU (DE/FI) | Płatne (ale nadal bardzo tanio) |
| Contabo / podobne VPS | ~4–8 € | Budget | Dużo dysku | Często wolniejszy I/O, gorszy support |
| Railway / Render / Fly.io | ~5–20 €+ | Szybki PoC | Mało DevOps | Free tier śpi / limity; baza osobno drożeje; gorszy stosunek cena/jakość przy Postgres |
| VPS PL (np. home.pl, OVH Start) | zwykle drożej | Preferencja lokalnego billing | Faktura PL | Często drożej przy tych samych parametrach |

### Rekomendacja

1. **Na start / produkcja rodzinna:** jeden VPS **Hetzner** (~5 €/mies.) + Docker Compose + nginx + Let's Encrypt.  
2. **Jeśli chcesz 0 zł i masz czas:** Oracle Always Free — ta sama architektura Compose, więcej walki z kontem i obrazami ARM.  
3. **Unikaj na start:** osobnych managed Postgres + managed frontend + managed backend u PaaS — przy tym stacku szybko wychodzi drożej niż jeden mały VPS.

Domena (opcjonalnie): ~40–80 zł/rok (np. `.pl` / `.eu`). Można startować na samym IP + HTTPS przez IP jest niewygodne — lepiej od razu tania domena.

---

## Architektura docelowa (najtańsza sensowna)

```
Internet
   │
   ▼
┌─────────────────────────────┐
│  VPS (Hetzner / Oracle)     │
│  ┌─────────┐                │
│  │  nginx  │ :80 / :443     │  ← HTTPS (Certbot / Caddy)
│  └────┬────┘                │
│       ├─ /        → pliki frontend (dist) ALBO kontener static
│       └─ /api/    → backend:8000
│  ┌─────────┐  ┌──────────┐  │
│  │ backend │  │ postgres │  │
│  └─────────┘  └──────────┘  │
└─────────────────────────────┘
```

**Frontend w produkcji:** `npm run build` → serwuj `frontend/dist` z nginx (bez `npm run dev`).  
**Backend:** `uvicorn` **bez** `--reload`, bez montowania kodu z hosta.  
**API URL:** przy tym samym origin (domena + `/api`) ustaw `VITE_API_URL=` puste (requesty względne) albo pełny URL `https://twoja-domena.pl` — spójnie z CORS.

---

## Ścieżka A — Hetzner (rekomendowana, ~5 €/mies.)

### 1. Serwer

1. Konto na [hetzner.com/cloud](https://www.hetzner.com/cloud).
2. Utwórz projekt → **Add Server**:
   - Lokalizacja: Falkenstein / Nuremberg / Helsinki
   - Typ: **CX22** lub aktualny odpowiednik (~2 vCPU, 4 GB RAM)
   - Obraz: **Ubuntu 24.04**
   - SSH key (obowiązkowo — wyłącz logowanie hasłem później)
3. Zapisz publiczne IPv4.

### 2. DNS

U domeny ustaw rekord **A**:

```
@    A    <IP_SERWERA>
www  A    <IP_SERWERA>
```

Propagacja: zwykle kilka minut–kilka godzin.

### 3. Pierwsze logowanie i hardening

```bash
ssh root@<IP_SERWERA>

# Użytkownik bez roota (opcjonalnie, ale warto)
adduser deploy
usermod -aG sudo deploy

# Firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Aktualizacje
apt update && apt upgrade -y
```

### 4. Docker

```bash
curl -fsSL https://get.docker.com | sh
usermod -aG docker deploy   # jeśli używasz użytkownika deploy
```

Wyloguj i zaloguj ponownie, żeby grupa `docker` zadziałała.

### 5. Kod i konfiguracja

```bash
# jako deploy
cd /opt
sudo mkdir -p /opt/familyorganiser
sudo chown deploy:deploy /opt/familyorganiser
git clone <URL_REPO> /opt/familyorganiser
cd /opt/familyorganiser

cp .env.example .env
nano .env
```

**Minimum w `.env` na produkcji:**

```env
POSTGRES_USER=familyorg
POSTGRES_PASSWORD=<długie-losowe-hasło>
POSTGRES_DB=familyorg
DATABASE_URL=postgresql+asyncpg://familyorg:<hasło>@db:5432/familyorg

SECRET_KEY=<min-32-znaki-losowe>
ADMIN_EMAIL=admin@twoja-domena.pl
ADMIN_PASSWORD=<mocne-hasło-nie-admin>

CORS_ORIGINS_STR=https://twoja-domena.pl,https://www.twoja-domena.pl
```

Wygeneruj sekrety np.:

```bash
openssl rand -hex 32
```

### 6. Compose produkcyjny

Obecny `docker-compose.yml` **nie wklejaj 1:1 na produkcję**. Docelowo:

- `backend`: build z `Dockerfile`, command bez `--reload`, **bez** volume `./backend:/app`
- `frontend`: multi-stage build (`npm run build` → nginx/alpine z `dist`) **albo** osobny stage i nginx hostujący static
- `db`: Postgres **bez** publikowania `5432` na świat (`ports` tylko wewnętrznie w sieci Compose)
- `proxy`: nginx na 80/443 + certyfikaty

Szkic usług (logika — do dopięcia w repo przed deployem):

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # BEZ ports: "5432:5432" na produkcji

  backend:
    build: ./backend
    restart: unless-stopped
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    depends_on:
      - db
    # command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

  frontend:
    build: ./frontend   # Dockerfile produkcyjny: build → nginx
    restart: unless-stopped

  proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./docker/certs:/etc/nginx/certs:ro
    depends_on:
      - backend
      - frontend
```

Uruchomienie:

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f
```

### 7. HTTPS (Let's Encrypt)

Najprościej na jednym VPS:

**Opcja A — Certbot na hoście** (gdy nginx na porcie 80):

```bash
apt install -y certbot
# zatrzymaj chwilowo proxy albo użyj webroot/plugin
certbot certonly --standalone -d twoja-domena.pl -d www.twoja-domena.pl
```

Skopiuj certy do `docker/certs` albo zamontuj `/etc/letsencrypt` w kontenerze nginx.

**Opcja B — Caddy** zamiast nginx: automatyczny HTTPS (mniej konfiguracji, też darmowy).

Odnowienie certów: cron / systemd timer (`certbot renew`).

### 8. Migracje / start aplikacji

Backend przy starcie tworzy tabele i seeduje admina (zgodnie z README). Na produkcji warto też:

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

(jeśli używasz Alembic w pipeline startowym).

### 9. Backup (obowiązkowy nawet „na tanio”)

```bash
# przykład cron codziennie 3:00
0 3 * * * docker compose -f /opt/familyorganiser/docker-compose.prod.yml exec -T db \
  pg_dump -U familyorg familyorg | gzip > /opt/backups/familyorg-$(date +\%F).sql.gz
```

Trzymaj kopie **poza** VPS (np. Backblaze B2 / Google Drive / drugi dysk) — najtańszy VPS bez backupu = ryzyko utraty danych budżetu rodziny.

---

## Ścieżka B — Oracle Cloud Always Free (0 €)

1. Załóż konto Oracle Cloud (wymaga karty do weryfikacji — nie powinna być obciążana w limicie Always Free).
2. Utwórz VM: **VM.Standard.A1.Flex** (Ampere ARM), np. 2 OCPU / 12 GB RAM (w limicie Always Free).
3. Security List / NSG: otwórz porty **22, 80, 443**.
4. Dalej jak w ścieżce A (Docker + Compose).

**Uwagi:**

- Obrazy muszą wspierać **ARM64** (`postgres:16-alpine` zwykle OK; sprawdzaj własne Dockerfile).
- Kapitał czasowy > kapitał pieniężny — rejestracja i limity bywają frustrujące.
- Dobry wybór, jeśli nie chcesz płacić wcale i akceptujesz ryzyko „zniknięcia” free tieru / blokady konta.

---

## Ścieżka C — PaaS (szybko, zwykle drożej)

Przykład: Render / Railway.

- Frontend: static site z `frontend/dist`
- Backend: web service z `backend/` (Docker lub Poetry)
- Postgres: managed addon

**Kiedy sensowne:** PoC na weekend, zero SSH.  
**Kiedy nie:** chcesz stałe ~5 €/mies. przy pełnym stacku — managed Postgres sam potrafi tyle kosztować.

---

## Checklist przed pierwszym publicznym deployem

- [ ] `SECRET_KEY` i `ADMIN_PASSWORD` zmienione (nie wartości z przykładów)
- [ ] Postgres **niedostępny** z internetu (tylko sieć Dockera)
- [ ] CORS tylko na Twoją domenę `https://...`
- [ ] Frontend to **build produkcyjny**, nie Vite dev
- [ ] Backend bez `--reload`
- [ ] HTTPS działa (przeglądarka bez ostrzeżenia)
- [ ] Logowanie adminem działa; zwykły user **nie** widzi panelu admina
- [ ] Backup `pg_dump` działa i jest gdzieś poza VPS
- [ ] Firewall: tylko 22/80/443 (SSH najlepiej klucz + ewentualnie ograniczenie IP)
- [ ] W Swaggerze `/docs` — rozważ wyłączenie na produkcji (`DEBUG=false` / osobna flaga)

---

## Szacunek kosztów „na spokojnie”

| Pozycja | Miesiąc | Rok |
|---------|---------|-----|
| Hetzner CX22-class | ~5 € | ~60 € |
| Domena `.pl` / `.eu` | — | ~40–80 zł |
| Backup object storage (opcjonalnie) | 0–2 € | — |
| **Razem (bez Oracle)** | **~5–7 €** | **~70–100 € + domena** |

Oracle Always Free: **0 €** hostingu + domena.

---

## Co warto dodać w repo przed deployem

Te rzeczy jeszcze nie są „produkcyjne” w obecnym stanie projektu:

1. `docker-compose.prod.yml` — bez hot-reload i bez exposu Postgresa.
2. `frontend/Dockerfile` multi-stage: `npm run build` → `nginx:alpine` z `dist`.
3. `docker/nginx.prod.conf` — static + `/api` + SSL.
4. `.env.production.example` — checklista sekretów.
5. Skrypt `scripts/backup.sh` + krótka instrukcja restore.

Gdy będziesz gotowy, można to wdrożyć w repo jako kolejny krok (bez zmiany logiki biznesowej).

---

## Szybka decyzja

| Pytanie | Odpowiedź |
|---------|-----------|
| Chcę najtaniej i stabilnie? | **Hetzner + Docker Compose + nginx + Let's Encrypt** |
| Chcę 0 zł? | Oracle Always Free (więcej roboty) |
| Chcę kliknąć i zapomnieć? | PaaS — drożej przy Postgresie |
| Redis na start? | **Nie** — nie jest potrzebny |
| SQLite na serwerze? | **Nie** na produkcji wieloużytkownikowej — Postgres w Compose |

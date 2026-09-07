# Oddanie na produkcję — prosto i na serio

**Data:** 2026-07-30  
**Dla:** właściciel projektu (Ty)  
**Aplikacja:** [family.fmazurkiewicz.dev](https://family.fmazurkiewicz.dev)

---

## Jak dla 5-latka — co to w ogóle jest?

Wyobraź sobie **wspólny notes rodzinny w internecie**:

- **Lista zakupów** — wszyscy widzą, co kupić, i odhaczają kupione.
- **Zadania** — kto ma posprzątać, co do zrobienia.
- **Budżet** — ile wpadło pieniędzy w tym miesiącu, ile wyszło, ile zostało.
- **Inwestycje** — proste wpisy typu lokata (kwota, procent, na ile).
- **Grupa rodzinna** — zapraszasz bliskich linkiem; widzicie wspólne rzeczy.

Żeby wejść, **logujesz się Google’m** (albo linkiem z maila). Nie musisz pamiętać hasła do naszej apki — robi to Supabase (bezpieczny „portier”).

---

## Gdzie co mieszka (3 miejsca)

```
Ty w przeglądarce
       │
       ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  STRONA (Vercel) │────▶│  API (Hetzner)   │────▶│  BAZA (Supabase) │
│  family.fmazur…  │     │  api-family…     │     │  Postgres + Auth │
└──────────────────┘     └──────────────────┘     └──────────────────┘
   wygląd, przyciski        logika, zapis            dane + logowanie
```

| Miejsce | Co to robi | Gdzie kliknąć jak coś zmieniasz |
|---------|------------|----------------------------------|
| **Vercel** | Pokazuje stronę użytkownikom | vercel.com → projekt → Settings → Env / Deployments |
| **Hetzner (VPS)** | Trzyma backend (API) | GitHub → Actions → Deploy; sekrety w GitHub Secrets |
| **Supabase** | Logowanie + baza danych | supabase.com → Authentication / Database |
| **Cloudflare** | Domena `fmazurkiewicz.dev` | DNS rekordy `family` i `api-family` |
| **GitHub** | Kod + auto-deploy API | repo FamilyOrganiser, Secrets, Actions |

---

## Co zostało zrobione (checklista ✅)

### Infrastruktura

- [x] Domena `family.fmazurkiewicz.dev` → frontend na Vercel (HTTPS)
- [x] Domena `api-family.fmazurkiewicz.dev` → API na Hetznerze (Docker + Caddy + Let’s Encrypt)
- [x] Baza Postgres + logowanie w Supabase (managed)
- [x] Auto-deploy backendu: push na `main` → GitHub Actions → VPS
- [x] Auto-deploy frontendu: push na `main` → Vercel
- [x] Health API: `GET /api/health` → `{"status":"ok"}`

### Aplikacja

- [x] Logowanie Google + magic link (Supabase)
- [x] Moduły: zakupy, zadania, budżet, inwestycje, raporty, grupy, profil, powiadomienia
- [x] Panel admina (`ADMIN_EMAIL` → pierwsze logowanie = admin aplikacji)
- [x] Migracje bazy (Alembic) na produkcji

### Bezpieczeństwo (skrót)

- [x] Sekrety **nie** w git — tylko GitHub Secrets / Vercel / Supabase panel
- [x] Frontend: tylko klucz **anon** Supabase (publiczny)
- [x] API: weryfikacja tokenów Supabase (JWT)
- [x] CORS: tylko Twoja domena frontu

Szczegóły: [Audyt bezpieczeństwa](../security/production-audit.md)

---

## Co musisz pamiętać na co dzień

### Zmieniasz kod frontu

1. Push na `main`
2. Vercel sam zbuduje (1–2 min)
3. Jeśli zmieniasz **zmienne** na Vercel → **Redeploy** (env wchodzi przy buildzie)

### Zmieniasz kod backendu / bazę

1. Push na `main` (pliki w `backend/`, Docker, workflow)
2. GitHub Actions sam deployuje na Hetzner
3. Nowa migracja Alembic → idzie w `deploy.sh` (`alembic upgrade head`)

### Dodajesz użytkownika admina

Ustaw `ADMIN_EMAIL` w GitHub Secret (właściciel: `fifmazurkiewicz@gmail.com`) → zaloguj się tym mailem przez Google/magic link → backend ustawi `is_app_admin` i `is_approved`. Bootstrap Gmail jest też w kodzie, więc stary secret `admin@admin.com` nie blokuje właściciela.

### Coś nie działa — szybka diagnoza

| Objaw | Sprawdź |
|-------|---------|
| Biała strona po logowaniu | Vercel env `VITE_*` + redeploy; Supabase Redirect URLs |
| 401 / brak profilu | `VITE_API_URL`, CORS na API, deploy backendu |
| Google nie wraca | Supabase → Redirect URLs: `https://family.fmazurkiewicz.dev/**` |
| API nie odpowiada | Hetzner: `docker compose ps`, logi Caddy, DNS `api-family` |
| Baza | Supabase dashboard, `DATABASE_URL` session pooler **:5432** |

---

## Koszty (orientacyjnie)

| Usługa | Szacunek |
|--------|----------|
| Vercel (frontend) | 0 € (hobby) |
| Hetzner VPS | ~4–6 €/mies. |
| Supabase | 0 € (free tier) przy małym ruchu |
| Domena Cloudflare | wg Twojego planu |

---

## Co NIE jest jeszcze w produkcie (plan v2.1+)

- Eksport Excel
- Archiwum starych list zakupów/zadań
- Pełne powiadomienia push
- Aplikacja mobilna
- Pełny system księgowy z kontami (było w starych wymaganiach v1)

To nie blokuje użytkowania — aplikacja jest **gotowa dla rodziny na produkcji**.

---

## Jedno zdanie podsumowania

**Zbudowaliśmy rodzinny organizer w internecie: ładna strona na Vercel, „mózg” na Twoim serwerze Hetzner, dane i logowanie w Supabase — i wszystko aktualizuje się samo po pushu na GitHub.**

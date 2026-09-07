# FamilyOrganiser — Dokumentacja

**Wersja produkcyjna:** 2.4  
**Ostatnia aktualizacja:** 2026-09-07  
**Status:** ✅ oddane na produkcję

| Adres | Rola |
|-------|------|
| [family.fmazurkiewicz.dev](https://family.fmazurkiewicz.dev) | Aplikacja (Vercel) |
| [api-family.fmazurkiewicz.dev](https://api-family.fmazurkiewicz.dev/api/health) | API (Render) |

---

## Dla Ciebie (właściciel) — zacznij tutaj

- [**Co zostało zrobione — prosto**](business/production-handover.md) — opis „jak dla 5-latka” + checklista
- [Opis funkcji](business/features.md) — co robi aplikacja
- [Lista zmian](business/CHANGELOG.md) — historia wersji
- [Audyt bezpieczeństwa](security/production-audit.md) — czy jest bezpiecznie na prod

---

## Biznesowa

| Dokument | Treść |
|----------|--------|
| [Opis funkcji](business/features.md) | Moduły, flow użytkownika |
| [Handover produkcyjny](business/production-handover.md) | Prosty opis + co gdzie kliknąć |
| [CHANGELOG](business/CHANGELOG.md) | Wersje i zmiany |
| [Wymagania v1 (archiwum)](../BUSINESS_REQUIREMENTS.md) | Pełna wizja 2026-03 — część poza zakresem v2 |

---

## Techniczna

| Dokument | Treść |
|----------|--------|
| [Architektura](technical/architecture.md) | Diagramy, warstwy, ADR, auth Supabase |
| [API Reference](technical/api.md) | Endpointy REST |
| [Model danych](technical/data-model.md) | ERD, tabele |
| [Local setup](technical/local-setup.md) | Dev bez Dockera: Postgres/API/FE + smoke |
| [ADR-005 faza 3](technical/adr-005-phase3.md) | Plan: testy, Excel, archiwum |

---

## Deploy i infrastruktura

| Dokument | Treść |
|----------|--------|
| [**Architektura platformy**](deployment/platform-architecture.md) | **Kanoniczny** opis prod + krok po kroku |
| [Backup i restore](deployment/backup-restore.md) | pg_dump co ~30 dni (GitHub Actions) + restore |
| [GitBook](deployment/gitbook-setup.md) | Podłączenie docs do GitBook (Git Sync) |
| [Porównanie hostingu](deployment/cheap-hosting.md) | Koszty VPS vs PaaS (referencja) |
| [Fly.io PoC](deployment/fly-io.md) | Archiwum historyczne — nie produkcja |

---

## Dla zarządu

- [Executive Summary](executive/summary.html) — dashboard HTML (otwórz w przeglądarce)

---

## Szybki start (dev)

Domyślnie **bez Dockera:** `poetry` w `backend/`, `npm run dev` w `frontend/` — [local-setup.md](technical/local-setup.md) i [README](../README.md).

Opcjonalnie: `docker compose up -d` (FE :3000, API :8000).

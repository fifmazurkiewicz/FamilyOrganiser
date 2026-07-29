# FamilyOrganiser — Dokumentacja

**Wersja:** 2.0  
**Ostatnia aktualizacja:** 2026-07-30  
**Domena produkcyjna:** [family.fmazurkiewicz.dev](https://family.fmazurkiewicz.dev) (FE) · [api-family.fmazurkiewicz.dev](https://api-family.fmazurkiewicz.dev) (API) — Cloudflare + Vercel / Hetzner+Caddy / Supabase — zob. [architektura platformy](deployment/platform-architecture.md)

## Spis treści

### 📋 Biznesowa
- [Opis funkcji](business/features.md) — co aplikacja robi, dla kogo
- [Lista zmian](business/CHANGELOG.md) — co nowego w każdej wersji

### 🔧 Techniczna
- [Architektura](technical/architecture.md) — diagramy, warstwy, decyzje
- [API Reference](technical/api.md) — endpointy, autoryzacja, przykłady
- [Model danych](technical/data-model.md) — ERD, encje, relacje

### 🚀 Deploy
- [**Architektura platformy (decyzja)**](deployment/platform-architecture.md) — Vercel + Hetzner + GH Actions; **instrukcja krok po kroku**
- [Najtańszy hosting](deployment/cheap-hosting.md) — VPS vs free tier, Compose, HTTPS, checklista
- [Fly.io (PoC)](deployment/fly-io.md) — wcześniejszy wariant; nie jest kierunkiem produkcyjnym

### 📊 Dla zarządu
- [Executive Summary](executive/summary.html) — dashboard HTML (otwórz w przeglądarce)

## Szybki start

```bash
# Uruchom lokalnie
docker compose up -d

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1
# Dokumentacja API: http://localhost:8000/docs
```
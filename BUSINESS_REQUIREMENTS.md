# FamilyOrganiser — Wymagania Biznesowe

**Wersja:** 1.0
**Data:** 2026-03-07
**Właściciel produktu:** fifmazurkiewicz

---

## 1. Cel i wizja produktu

FamilyOrganiser to prywatna aplikacja webowa i mobilna dla rodziny, umożliwiająca pełne zarządzanie finansami osobistymi i rodzinnymi. Każdy member rodziny ma własne konto z kontrolą nad prywatnością swoich danych — może wybiórczo udostępniać wydatki, oszczędności lub inwestycje pozostałym członkom rodziny.

**Misja:** Dać każdemu członkowi rodziny pełny wgląd we własne i rodzinne finanse w jednym, bezpiecznym miejscu.

---

## 2. Użytkownicy i role

### 2.1 Model kont

| Rola | Opis |
|------|------|
| **Admin rodziny** | Tworzy grupę rodzinną, zaprasza członków, widzi dane, które zostały mu udostępnione |
| **Członek rodziny** | Pełna kontrola nad własnymi danymi; sam decyduje, co udostępnia grupie |
| **Obserwator (opcjonalnie)** | Dziecko lub osoba z ograniczonym dostępem — tylko odczyt wybranych kategorii |

### 2.2 Model udostępniania

Każdy użytkownik może niezależnie przełączać widoczność swoich danych dla rodziny:

- Wydatki (kategorie lub całość)
- Inwestycje (portfolio lub tylko wartość łączna)
- Oszczędności (konta lub tylko saldo łączne)
- Budżet miesięczny (tak/nie)
- Cele finansowe (publiczne / prywatne)

### 2.3 Przewidywana liczba użytkowników

- Docelowo: 2–6 członków w jednej grupie rodzinnej
- Jedna instancja aplikacji (jedna rodzina)

---

## 3. Wymagania funkcjonalne

### F-01 Uwierzytelnianie i konta

- [ ] Rejestracja z e-mailem i hasłem (bcrypt/Argon2)
- [ ] Logowanie przez przeglądarkę i aplikację mobilną (JWT + Refresh Token)
- [ ] Zaproszenia do grupy rodzinnej przez link/kod
- [ ] Zarządzanie profilem (avatar, imię, waluta domyślna)
- [ ] Resetowanie hasła przez e-mail
- [ ] Opcjonalne: 2FA (TOTP / Google Authenticator)

### F-02 Zarządzanie wydatkami

- [ ] Dodawanie transakcji: kwota, data, kategoria, opis, osoba płacąca
- [ ] Kategorie wydatków (edytowalne): jedzenie, transport, zdrowie, edukacja, rozrywka, mieszkanie, ubrania, inne
- [ ] Podkategorie (np. Jedzenie → sklep spożywczy, restauracja)
- [ ] Tagi dowolne (np. „wakacje 2026", „remont kuchni")
- [ ] Wydatki cykliczne (abonament, czynsz, ubezpieczenie) z automatycznym przypomnieniem
- [ ] Import wyciągów bankowych (CSV / OFX / MT940)
- [ ] Przypisanie wydatku do kategorii: osobisty / rodzinny / wspólny
- [ ] Wydatki podzielone (split) między członków rodziny
- [ ] Zdjęcie paragonu (OCR opcjonalnie w v2)

### F-03 Budżet

- [ ] Tworzenie budżetów miesięcznych i rocznych per kategoria
- [ ] Budżet osobisty i budżet rodzinny (shared)
- [ ] Alerty przy przekroczeniu X% budżetu
- [ ] Porównanie: plan vs rzeczywistość
- [ ] Budżet kroczący (rolling budget)
- [ ] Historia budżetów (archiwum miesięczne)

### F-04 Oszczędności

- [ ] Konta oszczędnościowe / „skarbonki" z celem kwotowym i datą
  - Przykłady: wakacje, fundusz awaryjny, wymiana samochodu
- [ ] Śledzenie postępu (procent osiągnięcia celu)
- [ ] Wpłaty manualne lub automatyczne z budżetu
- [ ] Konta prywatne i rodzinne
- [ ] Powiadomienia o osiągnięciu celu lub opóźnieniu

### F-05 Inwestycje

- [ ] Portfel inwestycyjny per użytkownik
- [ ] Obsługiwane klasy aktywów:
  - **Akcje / ETF / Fundusze** — ticker + liczba jednostek + cena zakupu
  - **Nieruchomości** — adres, wartość zakupu, bieżąca wycena, przychód z najmu
  - **Kryptowaluty** — ticker + ilość + cena zakupu
  - **Lokaty / Obligacje** — kwota, oprocentowanie, data zapadalności
- [ ] Ręczne aktualizacje wycen (v1)
- [ ] Automatyczne kursy z zewnętrznego API (v2): giełda, krypto, NBP
- [ ] Historia wartości portfela (wykres liniowy)
- [ ] ROI (return on investment) per aktywo i całego portfela
- [ ] Podgląd rodzinny (łączna wartość portfeli — jeśli udostępnione)

### F-06 Planowanie wydatków (cele i prognozy)

- [ ] Planowane wydatki jednorazowe (np. zakup auta, remont — data + kwota)
- [ ] Śledzenie funduszu na planowany wydatek
- [ ] Prognoza cashflow: ile zostanie po opłaceniu stałych kosztów
- [ ] Scenariusze „co jeśli" (basic): co jeśli zwiększę oszczędności o X zł?
- [ ] Kalendarz finansowy — widok wydatków/dochodów na osi czasu

### F-07 Przychody

- [ ] Rejestracja przychodów: wynagrodzenie, premia, freelance, wynajem, dywidenda
- [ ] Przychody cykliczne (wynagrodzenie automatycznie co miesiąc)
- [ ] Podział na przychody osobiste i rodzinne

### F-08 Raporty i analityki

- [ ] Dashboard główny: saldo, wydatki miesiąc, oszczędności, portfel inwestycyjny
- [ ] Wykresy:
  - Wydatki wg kategorii (donut chart)
  - Trend wydatków (linia, ostatnie 12 miesięcy)
  - Budżet vs rzeczywistość (bar chart)
  - Wzrost wartości portfela
  - Networth (majątek netto) w czasie
- [ ] Raporty miesięczne i roczne (PDF export)
- [ ] Widok rodzinny: suma finansów wszystkich członków (tylko to, co udostępnili)

### F-09 Powiadomienia

- [ ] Push notification (mobile) i e-mail:
  - Przekroczenie budżetu
  - Zbliżający się termin cyklicznego wydatku
  - Osiągnięcie celu oszczędnościowego
  - Cotygodniowe podsumowanie finansów

### F-10 Wielowalutowość

- [ ] Domyślna waluta PLN
- [ ] Obsługa wielu walut per transakcja (EUR, USD, GBP)
- [ ] Przeliczenie na walutę bazową po kursie NBP / ECB (v2)

---

## 4. Wymagania niefunkcjonalne

### 4.1 Bezpieczeństwo

- Szyfrowanie danych w spoczynku (AES-256) i podczas transmisji (TLS 1.3)
- Hasła hashowane Argon2id
- JWT z krótkim TTL (15 min) + Refresh Token (30 dni, rotacja)
- RBAC — kontrola dostępu oparta na rolach
- Rate limiting na endpointach auth
- Audyt logów dostępu do danych finansowych
- OWASP Top 10 compliance

### 4.2 Dostępność i wydajność

- Czas odpowiedzi API < 200 ms (p95)
- Dostępność: 99.5% (self-hosted dopuszcza okna serwisowe)
- Responsywny UI (mobile-first)

### 4.3 Prywatność

- Dane przechowywane wyłącznie na własnym serwerze / wybranej chmurze
- Brak przekazywania danych finansowych do podmiotów trzecich (poza opcjonalnymi API kursów walut)
- RODO — prawo do eksportu i usunięcia konta

### 4.4 Skalowalność

- Architektura monolityczna na start (może być rozbita na mikroserwisy w przyszłości)
- Konteneryzacja przez Docker (łatwy deployment i backup)

---

## 5. Stack technologiczny

### 5.1 Frontend (Web)

| Warstwa | Technologia | Uzasadnienie |
|---------|-------------|--------------|
| Framework | **React 18 + TypeScript** | Wymaganie klienta |
| Router | React Router v6 | Standard |
| State | Zustand lub Redux Toolkit | Prosty state globalny |
| UI | Shadcn/ui + Tailwind CSS | Gotowe komponenty, łatwa customizacja |
| Wykresy | Recharts lub ApexCharts | SVG, React-native, licencja MIT |
| Formularze | React Hook Form + Zod | Walidacja schema-first |
| HTTP | Axios + React Query (TanStack) | Cache, refetch, optimistic updates |
| Testy | Vitest + React Testing Library | |

### 5.2 Backend

| Warstwa | Technologia | Uzasadnienie |
|---------|-------------|--------------|
| Framework | **FastAPI (Python 3.12)** | Async, auto-dokumentacja OpenAPI, szybki |
| ORM | SQLAlchemy 2.0 + Alembic | Migracje, relacyjny model |
| Baza danych | PostgreSQL 16 | Solidna, ACID, JSON support |
| Cache | Redis 7 | Sesje, rate limiting, kursy walut |
| Auth | python-jose (JWT) + passlib (Argon2) | |
| Zadania cykliczne | APScheduler lub Celery + Redis | Powiadomienia, przypomnienia |
| Email | FastMail / SendGrid | |
| Testy | pytest + httpx | |

### 5.3 Aplikacja mobilna (rekomendacja)

**Rekomendacja: React Native + Expo**

| Kryterium | React Native + Expo |
|-----------|---------------------|
| Zgodność z istniejącym stackiem | ✅ Ten sam język (TypeScript/JS), współdzielona logika |
| iOS (iPhone 15 Pro) | ✅ Natywne API |
| Android (Samsung FE 21) | ✅ Natywne API |
| Push Notifications | ✅ Expo Notifications |
| Jedna baza kodu | ✅ 80–90% kodu współdzielone |
| Krzywa uczenia | Łagodna (już znasz React) |
| Czas do MVP | Krótszy niż Kotlin + Swift osobno |

> Alternatywa: **Flutter** — jeśli preferujesz Dart. Lepszy performance na starszych urządzeniach, ale wymaga nauki nowego języka i brak współdzielenia kodu z React frontendem.

### 5.4 Infrastruktura

```
Docker Compose (development + produkcja):
├── app/           FastAPI (Python)
├── web/           React (Nginx)
├── db/            PostgreSQL
├── cache/         Redis
└── proxy/         Nginx (reverse proxy, SSL termination)
```

**Hosting opcje:**
- Self-hosted VPS (Hetzner, OVH) — ~20–40 zł/mies.
- Cloud: Railway.app lub Render.com — prosta konfiguracja CI/CD

---

## 6. Architektura systemu (high-level)

```
┌─────────────────────────────────────────────┐
│                  KLIENTY                     │
│  React Web App  │  React Native Mobile App  │
└────────┬─────────────────────┬──────────────┘
         │    HTTPS/REST API   │
         ▼                     ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │  Auth    │ │ Budget   │ │ Investments │ │
│  │ Service  │ │ Service  │ │  Service    │ │
│  └──────────┘ └──────────┘ └─────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │Savings   │ │ Reports  │ │Notification │ │
│  │ Service  │ │ Service  │ │  Service    │ │
│  └──────────┘ └──────────┘ └─────────────┘ │
└───────────┬──────────────────┬──────────────┘
            │                  │
    ┌───────▼───────┐  ┌───────▼───────┐
    │  PostgreSQL   │  │     Redis     │
    └───────────────┘  └───────────────┘
```

---

## 7. Roadmapa (MVP → v2)

### MVP — Faza 1 (Web, ~8–12 tygodni)

| Priorytet | Moduł |
|-----------|-------|
| P0 | Konta użytkowników, grupy rodzinne, udostępnianie |
| P0 | Wydatki (dodawanie, kategorie, lista) |
| P0 | Przychody |
| P0 | Budżet miesięczny |
| P1 | Oszczędności (cele) |
| P1 | Dashboard + podstawowe wykresy |
| P1 | Wydatki cykliczne + powiadomienia e-mail |
| P2 | Import CSV |

### Faza 2 (Web + Mobile, ~6–8 tygodni)

| Priorytet | Moduł |
|-----------|-------|
| P0 | React Native Mobile App (iOS + Android) |
| P0 | Push Notifications |
| P1 | Inwestycje (ręczny portfel) |
| P1 | Planowanie wydatków (kalendarz, prognozy) |
| P2 | Raporty PDF |
| P2 | Wielowalutowość + kursy NBP |

### Faza 3 (Zaawansowana, ~4–6 tygodni)

| Priorytet | Moduł |
|-----------|-------|
| P1 | Automatyczne kursy inwestycji (API) |
| P1 | OCR paragonów (zdjęcie → transakcja) |
| P2 | Open Banking / import bankowy automatyczny |
| P2 | Scenariusze finansowe „co jeśli" |
| P3 | Analityka AI (sugestie oszczędności) |

---

## 8. Definicja sukcesu (KPI)

- Wszystkie wydatki rodziny rejestrowane w aplikacji (cel: 90% transakcji)
- Budżet tworzony i śledzony co miesiąc
- Wartość portfela inwestycyjnego aktualizowana co tydzień
- Cele oszczędnościowe realizowane zgodnie z planem
- Dostęp przez przeglądarkę i telefon (iOS + Android) bez problemów technicznych

---

## 9. Słownik pojęć

| Termin | Definicja |
|--------|-----------|
| Transakcja | Pojedynczy wydatek lub przychód |
| Budżet | Plan finansowy na dany okres (miesiąc/rok) per kategoria |
| Cel oszczędnościowy | Skarbonka z docelową kwotą i datą realizacji |
| Portfel | Zestaw aktywów inwestycyjnych użytkownika |
| Networth | Majątek netto = Aktywa − Zobowiązania |
| Udostępnianie | Mechanizm selektywnego pokazania swoich danych innym członkom rodziny |
| Cashflow | Przepływ gotówki: przychody − wydatki w danym okresie |

---

*Dokument jest żywym dokumentem — zaktualizuj go przed rozpoczęciem każdej kolejnej fazy.*

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

- [ ] **Rejestracja** — e-mail (jako login) + hasło (Argon2); **bez weryfikacji e-mail** — konto aktywne od razu po rejestracji
- [ ] Logowanie przez przeglądarkę i aplikację mobilną (JWT + Refresh Token)
- [ ] Zaproszenia do grupy rodzinnej przez link/kod
- [ ] Zarządzanie profilem (avatar, imię, waluta domyślna)
- [ ] Opcjonalne: 2FA (TOTP / Google Authenticator)

#### Resetowanie hasła
- [ ] **Pytanie zabezpieczające** — użytkownik ustawia pytanie + odpowiedź podczas rejestracji; poprawna odpowiedź umożliwia ustawienie nowego hasła (bez żadnego e-maila)
- [ ] **Admin rodziny resetuje hasło członka** — admin grupy rodzinnej może ustawić nowe hasło dowolnemu członkowi swojej grupy; akcja logowana w historii grupy z informacją kto i kiedy zresetował
- [ ] **Admin aplikacji resetuje hasło** — administrator całej aplikacji może zresetować hasło dowolnego użytkownika; akcja logowana w systemowym logu audytowym
- [ ] Po resecie przez admina użytkownik dostaje powiadomienie in-app: „Twoje hasło zostało zmienione przez administratora" (bez podawania nowego hasła w powiadomieniu)
- [ ] Użytkownik może samodzielnie zmienić hasło po zalogowaniu (stare hasło → nowe hasło)

### F-01a Konta i portfele (źródła środków)

#### Definiowanie kont
- [ ] Każdy użytkownik definiuje własne konta finansowe
- [ ] Dane konta: nazwa, typ, waluta, kolor/ikona, saldo początkowe, data otwarcia
- [ ] Typy kont:

| Typ | Przykłady |
|-----|-----------|
| **Konto bankowe (indywidualne)** | mBank, PKO BP, Santander, ING, Pekao |
| **Konto bankowe (wspólne / joint account)** | Konto małżeńskie, konto dla pary, konto rodzinne |
| **Karta prepaid / e-portfel** | Revolut, Wise, BLIK-portfel |
| **Gotówka** | Portfel, sejf domowy |
| **Karta kredytowa** | limit, saldo zadłużenia, dzień spłaty |
| **Konto oszczędnościowe** | Konto oszcz. w mBanku, eKonto Santander |
| **Kryptogiełda** | Binance, Coinbase (saldo FIAT lub crypto) |

#### Konto bankowe wspólne (joint account)
- [ ] Oznaczenie konta jako **wspólne** podczas tworzenia lub edycji
- [ ] **Właściciele konta** — lista członków rodziny ze współdostępem (np. mąż + żona)
  - Każdy właściciel widzi pełną historię transakcji i saldo
  - Każdy właściciel może dodawać transakcje z tego konta
- [ ] **Widoczność konta w profilach** — konto pojawia się na dashboardzie KAŻDEGO właściciela
- [ ] **Saldo zsumowane** — w widoku rodzinnym konto wspólne wliczone tylko raz (nie podwójnie)
- [ ] Import wyciągu dla konta wspólnego dostępny dla każdego właściciela (transakcje nie duplikują się)
- [ ] Wyróżnik wizualny konta wspólnego (np. ikona dwóch osób / inny kolor ramki)
- [ ] **Powiadomienia** — opcja: każdy właściciel dostaje push o transakcji na wspólnym koncie
- [ ] Historia zmian salda widoczna dla wszystkich właścicieli (kto dodał jaką transakcję)
- [ ] **Usunięcie / edycja transakcji na wspólnym koncie** — obowiązuje mechanizm zgody (patrz F-04 „Zgoda na usunięcie i edycję zasobów wspólnych")
- [ ] **Zamknięcie (usunięcie) wspólnego konta** — wymagana zgoda wszystkich właścicieli; ten sam przepływ wniosek → zatwierdzenie

#### Zarządzanie saldem
- [ ] **Saldo bieżące** — automatycznie aktualizowane na podstawie zarejestrowanych transakcji
- [ ] **Ręczna korekta salda** — wpisanie rzeczywistego salda z banku (np. po imporcie wyciągu) z adnotacją „korekta"
- [ ] **Historia salda** — wykres salda konta w czasie
- [ ] Obsługa kart kredytowych:
  - Limit kredytowy, aktualne zadłużenie, dostępny limit
  - Dzień generowania wyciągu, dzień spłaty
  - Alert przed terminem spłaty

#### Powiązanie z transakcjami
- [ ] Każda transakcja (wydatek / wpływ) przypisana do konkretnego konta
- [ ] Transfer między kontami (np. przelew z mBanku na Revolut) — nie generuje wydatku, tylko przenosi środki
- [ ] Przy dodawaniu transakcji — domyślne konto konfigurowalne per użytkownik

#### Widoki
- [ ] **Przegląd wszystkich kont** — kafelki z nazwą, saldem bieżącym, walutą i ikoną banku
- [ ] **Łączne saldo** — suma wszystkich kont użytkownika (w PLN po przeliczeniu walut)
- [ ] Widok rodzinny — łączne salda członków rodziny (jeśli udostępnione)
- [ ] Sortowanie: według salda, nazwy, ostatniej aktywności

#### Udostępnianie
- [ ] Użytkownik decyduje, które konta są widoczne dla rodziny (tylko saldo lub też transakcje)
- [ ] Możliwość ukrycia wybranego konta całkowicie (np. konto prywatne)

### F-02 Zarządzanie wydatkami

- [ ] Dodawanie transakcji: kwota, data, kategoria, opis, osoba płacąca, **konto źródłowe**
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

### F-04 Oszczędności i cele

#### Tworzenie celu oszczędnościowego
- [ ] Dane celu: nazwa, krótki opis (do czego służy), ikona/emoji, kolor
  - Przykłady: „Wakacje Grecja 2027 — wyjazd całą rodziną w sierpniu", „Fundusz awaryjny — 6 miesięcy wydatków na nieprzewidziane sytuacje", „Nowy laptop — MacBook Pro M4"
- [ ] Kwota docelowa i opcjonalna data realizacji
- [ ] Typ celu: **osobisty** / **rodzinny** (wspólny dla wszystkich lub wybranych członków)
- [ ] Powiązanie z kontem źródłowym (środki fizycznie na konkretnym koncie bankowym lub „wirtualny" cel bez konta)

#### Prognoza i śledzenie postępu
- [ ] Pasek postępu (X zł z Y zł, Z%)
- [ ] **Szacowany czas osiągnięcia celu** — automatyczna kalkulacja:
  - Na podstawie historycznego tempa wpłat (średnia z ostatnich 3 miesięcy)
  - Na podstawie zadeklarowanej miesięcznej kwoty wpłat
  - Wyświetlenie: „Osiągniesz cel za ~8 miesięcy (listopad 2026)"
- [ ] Alert jeśli cel nie zostanie osiągnięty na czas — „Aby zdążyć do X, musisz wpłacać Y zł/mies."
- [ ] **Scenariusze**: co jeśli wpłacę więcej / mniej miesięcznie? (suwak → aktualizacja daty)
- [ ] Historia wpłat z datą, kwotą i źródłem (konto, użytkownik)

#### Zasilanie celów — skąd mogą płynąć środki
- [ ] **Ręczna wpłata** — użytkownik podaje kwotę i konto źródłowe
- [ ] **Wpłata cykliczna** — automatyczna rezerwacja X zł miesięcznie z wybranego konta (np. co 1. miesiąca)
- [ ] **Przelew z konta indywidualnego** na cel (osobisty lub rodzinny)
- [ ] **Przelew z konta rodzinnego/wspólnego** na cel
- [ ] **Wpłaty wielu członków rodziny** do jednego celu rodzinnego — widać kto ile wpłacił

#### Transfery między kontami i celami (F-04a)
- [ ] **Transfer konto → konto** (np. mBank → Revolut) — bez kategorii wydatku, tylko przesunięcie
- [ ] **Transfer konto → cel oszczędnościowy** — zasilanie skarbonki
- [ ] **Transfer cel → konto** — wypłata z celu (np. kiedy cel osiągnięty lub anulowany)
- [ ] **Transfer między celami** — przeniesienie nadwyżki z jednego celu do drugiego
- [ ] Każdy transfer: data, kwota, waluta, konto źródłowe, konto docelowe / cel, opcjonalny opis
- [ ] Historia wszystkich transferów z filtrowaniem

#### Konta i portfele wspólne (rodzinne)
- [ ] **Tworzenie wspólnego konta/portfela** — widoczne i zarządzane przez wybranych członków rodziny
  - Przykłady: „Budżet domowy", „Fundusz wakacyjny rodziny", „Oszczędności na remont"
- [ ] Admin wspólnego portfela zaprasza innych członków rodziny do współzarządzania
- [ ] **Role w portfelu wspólnym**:
  - *Właściciel* — pełne uprawnienia; usunięcie portfela wymaga zgody wszystkich właścicieli (patrz niżej)
  - *Współzarządzający* — dodawanie transakcji, zasilanie, przeglądanie
  - *Obserwator* — tylko podgląd salda i historii
- [ ] Saldo wspólnego portfela widoczne na dashboardzie każdego uczestnika
- [ ] Historia transakcji wspólnego portfela — kto, kiedy, co
- [ ] Powiadomienie dla uczestników przy każdej transakcji na wspólnym portfelu (konfigurowalne)

#### Zgoda na usunięcie i edycję zasobów wspólnych
- [ ] **Usunięcie wspólnego portfela / konta bankowego wspólnego** — wymagana akceptacja WSZYSTKICH właścicieli:
  1. Inicjator wysyła wniosek o usunięcie (opcjonalny komentarz, np. „konto zamknięte w banku")
  2. Pozostali właściciele otrzymują powiadomienie push + in-app z prośbą o zatwierdzenie
  3. Zasób jest usuwany dopiero gdy WSZYSCY zatwierdzą wniosek
  4. Jeśli którykolwiek właściciel odrzuci — wniosek anulowany, wszyscy dostają powiadomienie
  5. Wniosek wygasa automatycznie po 7 dniach bez odpowiedzi (konfigurowalne)
- [ ] **Usunięcie wspólnej transakcji** — ten sam mechanizm wniosek → zatwierdzenie przez wszystkich właścicieli konta/portfela
- [ ] **Edycja wspólnej transakcji** (zmiana kwoty, kategorii, daty) — konfigurowalne per portfel:
  - *Wymagaj zgody* — jak wyżej, zmiana aktywna po akceptacji wszystkich
  - *Tylko powiadom* — zmiana zapisywana od razu, pozostali dostają powiadomienie
- [ ] **Panel „Oczekujące wnioski"** — widok wszystkich otwartych wniosków czekających na moją decyzję (Zatwierdź / Odrzuć)
- [ ] Historia wniosków — kto wnioskował, kto zatwierdził / odrzucił, kiedy

#### Widoki i raporty
- [ ] Lista celów z paskiem postępu, datą realizacji i prognozowaną datą osiągnięcia
- [ ] Sortowanie: według priorytetu, % ukończenia, daty realizacji
- [ ] Dashboard oszczędności: łączna kwota odłożona (osobista + rodzinna), suma aktywnych celów
- [ ] Powiadomienia: osiągnięcie celu, opóźnienie, zbliżający się termin wpłaty cyklicznej

### F-05 Inwestycje

- [ ] Portfel inwestycyjny per użytkownik
- [ ] Obsługiwane klasy aktywów:
  - **Akcje / ETF / Fundusze** — ticker + liczba jednostek + cena zakupu
  - **Nieruchomości** — adres, wartość zakupu, bieżąca wycena, przychód z najmu
  - **Kryptowaluty** — ticker + ilość + cena zakupu
  - **Polskie Obligacje Skarbowe** — szczegóły poniżej (F-05a)
  - **Lokaty bankowe** — kwota, oprocentowanie stałe, data zapadalności, bank
- [ ] Ręczne aktualizacje wycen (v1)
- [ ] Automatyczne kursy z zewnętrznego API (v2): giełda, krypto, NBP
- [ ] Historia wartości portfela (wykres liniowy)
- [ ] ROI (return on investment) per aktywo i całego portfela
- [ ] Podgląd rodzinny (łączna wartość portfeli — jeśli udostępnione)

### F-05a Polskie Obligacje Skarbowe (szczegółowy moduł)

#### Obsługiwane typy obligacji (oferta PKO/MF)

| Symbol | Nazwa | Okres | Oprocentowanie |
|--------|-------|-------|----------------|
| OFL | Obligacje 3-miesięczne | 3 miesiące | Stałe |
| ROR | Obligacje roczne | 1 rok | Zmienne (stopa ref. NBP + marża) |
| DOR | Obligacje 2-letnie | 2 lata | Zmienne (stopa ref. NBP + marża) |
| TOS | Obligacje 3-letnie | 3 lata | Stałe |
| COI | Obligacje 4-letnie | 4 lata | Zmienne (inflacja CPI + marża) |
| EDO | Obligacje 10-letnie (emerytalne) | 10 lat | Zmienne (inflacja CPI + marża) |
| ROS / ROD | Rodzinne Obligacje Skarbowe | 6 / 12 lat | Zmienne (inflacja CPI + marża), dla beneficjentów 800+ |

#### Dane wprowadzane przy zakupie
- [ ] Typ obligacji (lista z tabeli powyżej)
- [ ] Seria obligacji (np. `EDO0336` — identyfikator z potwierdzenia zakupu)
- [ ] Liczba sztuk (1 sztuka = 100 zł wartości nominalnej)
- [ ] Data zakupu (= data emisji serii)
- [ ] Oprocentowanie pierwszego okresu odsetkowego (wpisywane ręcznie z prospektu emisyjnego)

#### Automatyczne obliczenia
- [ ] **Wartość bieżąca** = liczba sztuk × 100 zł × (1 + narosłe odsetki za bieżący okres)
- [ ] **Narosłe odsetki** — kalkulacja na podstawie daty zakupu, długości okresu odsetkowego i oprocentowania
- [ ] **Data zapadalności** — liczona automatycznie z daty zakupu + okres obligacji
- [ ] **Kolejne okresy odsetkowe** dla obligacji zmiennych:
  - Dla ROR/DOR: aktualna stopa referencyjna NBP (wprowadzana ręcznie lub pobierana z API NBP v2)
  - Dla COI/EDO/ROS/ROD: inflacja CPI z ostatniego odczytu GUS + marża (ręcznie lub API GUS v2)
- [ ] **Harmonogram odsetek** — tabela: data, oprocentowanie okresu, odsetki, wartość obligacji
- [ ] **Efektywna stopa zwrotu** (uwzględnia podatek Belki 19%)
- [ ] **Podatek Belki** — szacunkowa kwota przy wykupie / przy każdym okresie

#### Wcześniejszy wykup
- [ ] Symulacja wcześniejszego wykupu: ile otrzymam jeśli sprzedam dziś?
  - Uwzględnia opłatę za przedterminowy wykup (np. 0,70 zł / sztukę dla EDO, zależnie od okresu)
- [ ] Porównanie: trzymaj do zapadalności vs wykup teraz (różnica w PLN i %)

#### Widoki i raporty
- [ ] Lista wszystkich serii z: wartością bieżącą, datą zapadalności, oprocentowaniem aktualnego okresu, narosłymi odsetkami
- [ ] Łączna wartość portfela obligacji + prognoza wartości na datę zapadalności
- [ ] Kalendarz wykupów — które serie zapadają w kolejnych miesiącach
- [ ] Eksport do Excela: harmonogram odsetkowy per seria

### F-06 Planowanie wydatków (cele i prognozy)

- [ ] Planowane wydatki jednorazowe (np. zakup auta, remont — data + kwota)
- [ ] Śledzenie funduszu na planowany wydatek
- [ ] Prognoza cashflow: ile zostanie po opłaceniu stałych kosztów
- [ ] Scenariusze „co jeśli" (basic): co jeśli zwiększę oszczędności o X zł?
- [ ] Kalendarz finansowy — widok wydatków/dochodów na osi czasu

### F-07 Przychody

#### Stałe wpływy cykliczne
- [ ] Definiowanie szablonu stałego wpływu: nazwa, kwota bazowa, dzień miesiąca, waluta, kategoria
  - Przykłady: Wynagrodzenie (10. każdego miesiąca, 8 000 zł), Wynajem mieszkania (1. każdego miesiąca, 2 500 zł)
- [ ] Automatyczne generowanie wpływu w danym miesiącu na podstawie szablonu
- [ ] **Edycja kwoty dla konkretnego miesiąca** bez zmiany szablonu — nadpisanie wartości bazowej
  - Przykład: wynagrodzenie bazowe 8 000 zł, w marcu wpisano 9 200 zł (premia) → szablon pozostaje 8 000 zł
  - Edytowana kwota oznaczona wizualnie jako „zmodyfikowana" (ikona/kolor)
- [ ] Dodanie wpływu dodatkowego do miesiąca (np. premia, nadgodziny) obok stałego
- [ ] Historia zmian kwot per miesiąc — widać kiedy i o ile zarobiono więcej/mniej niż bazowo
- [ ] Możliwość pominięcia wpływu w danym miesiącu (np. urlop bezpłatny, zwolnienie lekarskie)

#### Wpływy jednorazowe
- [ ] Rejestracja ręczna: kwota, data, kategoria (premia, freelance, sprzedaż, dywidenda, darowizna, inne)
- [ ] Opcjonalny opis i załącznik (np. rachunek)

#### Kategorie przychodów
- [ ] Wynagrodzenie etatowe
- [ ] Premia / nadgodziny
- [ ] Freelance / zlecenie
- [ ] Wynajem nieruchomości
- [ ] Dywidenda / zyski z inwestycji
- [ ] Sprzedaż (np. rzeczy używanych)
- [ ] Inne (edytowalne przez użytkownika)

#### Widoki i analityki
- [ ] Podział na przychody osobiste i rodzinne
- [ ] Porównanie przychody vs wydatki per miesiąc
- [ ] Trend przychodów — wykres liniowy z zaznaczonymi miesiącami z premią/odbiegającymi od bazy

### F-08 Raporty i analityki

- [ ] Dashboard główny: saldo, wydatki miesiąc, oszczędności, portfel inwestycyjny
- [ ] Wykresy dynamiczne (interaktywne):
  - Wydatki wg kategorii (donut chart — kliknięcie → drill-down do podkategorii)
  - Trend wydatków (linia, ostatnie 12 miesięcy — zoom, hover z detalami)
  - Budżet vs rzeczywistość (bar chart — porównanie plan/wykonanie)
  - Wzrost wartości portfela (area chart z tooltipem per aktywo)
  - Networth (majątek netto) w czasie (linia z punktami granicznymi)
  - Cashflow miesięczny — przychody vs wydatki (grouped bar)
  - Heatmapa wydatków — intensywność wydatków per dzień tygodnia/miesiąc
  - Filtrowanie wykresów: zakres dat, kategorie, członek rodziny
  - Przełączanie widoku: osobisty / rodzinny
- [ ] Raporty miesięczne i roczne (PDF export)
- [ ] **Eksport do Excela (.xlsx):**
  - Eksport listy transakcji (z filtrami: zakres dat, kategoria, użytkownik)
  - Eksport budżetu (plan vs wykonanie per miesiąc)
  - Eksport portfela inwestycyjnego (wszystkie aktywa + ROI)
  - Eksport celów oszczędnościowych (postęp, wpłaty)
  - Plik wieloarkuszowy (każdy moduł = osobny arkusz)
  - Gotowe formatowanie tabeli w Excelu (nagłówki, sumowanie, waluta)
- [ ] Widok rodzinny: suma finansów wszystkich członków (tylko to, co udostępnili)

### F-09 Powiadomienia

#### Kanały dostarczania
- [ ] Push notification (aplikacja mobilna)
- [ ] Powiadomienie in-app (dzwonek w nagłówku / centrum powiadomień)
- ~~E-mail~~ — **nie używamy kanału e-mail do powiadomień**

#### Alerty dla wydatków jednorazowych (planowanych)
- [ ] Przy tworzeniu planowanego wydatku użytkownik ustawia **własny alert** z wyprzedzeniem (np. 7 dni, 3 dni, 1 dzień przed)
- [ ] Możliwość ustawienia **wielu przypomnień** dla jednego wydatku (np. 30 dni + 7 dni + 1 dzień)
- [ ] Powiadomienie zawiera: nazwę wydatku, kwotę, datę płatności, ile dni zostało
- [ ] Alert gdy brak wystarczających środków na planowany wydatek

#### Alerty dla wydatków stałych / cyklicznych
- [ ] Przy tworzeniu wydatku cyklicznego (rata za auto, czynsz, abonament) użytkownik ustawia przypomnienie z wyprzedzeniem (np. 5 dni przed terminem)
- [ ] Domyślne wyprzedzenie konfigurowalne globalnie w ustawieniach (np. zawsze 3 dni wcześniej)
- [ ] Powiadomienie zawiera: nazwę (np. „Rata za auto"), kwotę, datę płatności, numer raty (np. „rata 8/60")
- [ ] Alert o niepotwierdzonym wydatku cyklicznym — jeśli termin minął, a transakcja nie została zarejestrowana
- [ ] Opcja „Potwierdź płatność" bezpośrednio z powiadomienia (szybka akcja)

#### Pozostałe alerty
- [ ] Przekroczenie X% budżetu miesięcznego (próg konfigurowalny, np. 80% i 100%)
- [ ] Osiągnięcie celu oszczędnościowego
- [ ] Zbliżający się termin lokaty / obligacji (np. 14 dni przed zapadalnością)
- [ ] Cotygodniowe podsumowanie finansów (opcjonalne, dzień i godzina do wyboru)

#### Zarządzanie powiadomieniami
- [ ] Centrum powiadomień — historia wszystkich alertów z odczytem/nieodczytem
- [ ] Każdy użytkownik konfiguruje własne preferencje (co, kiedy, jakim kanałem)
- [ ] Możliwość wyciszenia powiadomień na wybrany okres (urlop)

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
| Wykresy | **Recharts** (web) + **Victory Native** (mobile) | Recharts: interaktywność, drill-down, zoom; wspólne API |
| Eksport Excel | **SheetJS (xlsx)** po stronie klienta | Generowanie .xlsx w przeglądarce bez backendu |
| Eksport Excel (alt.) | **openpyxl** po stronie backendu | Zaawansowane formatowanie, wieloarkuszowe raporty |
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
| Push / in-app | FCM (Firebase Cloud Messaging) | Powiadomienia mobilne i in-app; brak integracji e-mail |
| Eksport Excel | **openpyxl** | Wieloarkuszowe .xlsx z formatowaniem, walutami, sumami |
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
| P1 | Wydatki cykliczne + powiadomienia push/in-app |
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

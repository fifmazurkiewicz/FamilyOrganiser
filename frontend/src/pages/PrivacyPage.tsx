import { Link } from "react-router-dom";
import { Home, Shield } from "lucide-react";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="text-xl font-semibold text-foreground">{title}</h2>
      <div className="space-y-2 text-sm leading-6 text-muted-foreground">{children}</div>
    </section>
  );
}

export default function PrivacyPage() {
  return (
    <div className="min-h-dvh bg-gradient-to-br from-background via-background to-primary-light/20">
      <header className="border-b border-border bg-card/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-4xl items-center justify-between px-4">
          <Link to="/" className="flex items-center gap-2 font-bold text-foreground">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary">
              <Home className="h-4 w-4 text-white" />
            </span>
            <span>Family<span className="text-primary">Organiser</span></span>
          </Link>
          <Link to="/login" className="text-sm font-semibold text-primary hover:text-primary-dark">Zaloguj się</Link>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-10 sm:py-14">
        <article className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-10">
          <div className="mb-8 flex items-start gap-3">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-light">
              <Shield className="h-5 w-5 text-primary" />
            </span>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Polityka prywatności</h1>
              <p className="mt-1 text-sm text-muted-foreground">Wersja 1.0 · obowiązuje od 13 września 2026 r.</p>
            </div>
          </div>
          <div className="space-y-8">
            <Section title="Administrator i kontakt">
              <p>Administratorem danych jest Filip Mazurkiewicz, operator aplikacji FamilyOrganiser. W sprawach prywatności napisz na <a className="text-primary underline" href="mailto:fifmazurkiewicz@gmail.com">fifmazurkiewicz@gmail.com</a>.</p>
            </Section>
            <Section title="Jakie dane przetwarzamy">
              <p>Dane konta obejmują adres e-mail, nazwę profilu, identyfikator uwierzytelniania i ustawienia. Funkcje aplikacji mogą zawierać członkostwa w grupach, listy zakupów, zadania, budżety, przychody, wydatki, inwestycje, notatki i powiadomienia. Rejestrujemy też niezbędne informacje techniczne i zdarzenia bezpieczeństwa.</p>
            </Section>
            <Section title="Cele i podstawy">
              <p>Dane są używane do utworzenia i zabezpieczenia konta, świadczenia wybranych funkcji, synchronizacji danych w grupie rodzinnej, obsługi zgłoszeń oraz ochrony aplikacji. Podstawą jest wykonanie usługi żądanej przez użytkownika, uzasadniony interes polegający na bezpieczeństwie i obronie roszczeń oraz obowiązek prawny, jeśli ma zastosowanie.</p>
            </Section>
            <Section title="Dane współdzielone">
              <p>Informacje zapisane w grupie rodzinnej mogą być widoczne dla jej członków zgodnie z ustawieniami udostępniania. Nie wpisuj danych innej osoby, jeżeli nie jest to potrzebne lub nie masz prawa ich udostępnić.</p>
            </Section>
            <Section title="Dostawcy">
              <p>Korzystamy z Supabase do bazy danych i logowania, Render do hostowania API oraz Vercel do hostowania interfejsu. Dostawcy mogą przetwarzać dane techniczne niezbędne do działania usługi. Szczegóły lokalizacji i mechanizmów transferu zależą od aktywnej konfiguracji produkcyjnej i umów z dostawcami.</p>
            </Section>
            <Section title="Okres przechowywania">
              <p>Dane aktywnego konta przechowujemy przez czas korzystania z usługi. Po usunięciu konta prywatne dane są usuwane lub anonimizowane. Wspólne wpisy mogą pozostać w grupie jako utworzone przez „Usuniętego użytkownika”, aby nie utracić danych innych członków. Kopie zapasowe i ograniczone logi bezpieczeństwa mogą pozostać do czasu ich rotacji lub dłużej, jeśli wymaga tego prawo albo obrona roszczeń.</p>
            </Section>
            <Section title="Twoje prawa">
              <p>Możesz uzyskać dostęp do danych, poprawić profil, pobrać kopię danych lub usunąć konto w sekcji „Profil użytkownika”. Możesz również żądać ograniczenia przetwarzania, sprzeciwić się przetwarzaniu opartemu na uzasadnionym interesie i złożyć skargę do Prezesa Urzędu Ochrony Danych Osobowych.</p>
            </Section>
            <Section title="Pamięć przeglądarki i AI">
              <p>Aplikacja używa pamięci przeglądarki niezbędnej do utrzymania bezpiecznej sesji i ustawień interfejsu. Obecnie nie używamy reklamowych plików cookie ani generatywnej sztucznej inteligencji. Jeśli to się zmieni, zaktualizujemy tę informację i wdrożymy wymagane wybory przed uruchomieniem takich funkcji.</p>
            </Section>
          </div>
        </article>
      </main>
    </div>
  );
}

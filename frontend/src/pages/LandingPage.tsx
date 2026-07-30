import { Link } from "react-router-dom";
import {
  Users, PiggyBank, TrendingUp, BarChart2,
  Shield, ArrowRight, Home, CreditCard, Sparkles
} from "lucide-react";

const features = [
  {
    icon: Users,
    title: "Grupy rodzinne",
    description: "Twórz wspólne grupy i zarządzaj finansami całej rodziny w jednym miejscu.",
  },
  {
    icon: PiggyBank,
    title: "Cele oszczędnościowe",
    description: "Wyznaczaj cele, śledź postępy i motywuj się do oszczędzania z rodziną.",
  },
  {
    icon: BarChart2,
    title: "Inteligentny budżet",
    description: "Planuj miesięczne budżety i otrzymuj alerty gdy zbliżasz się do limitu.",
  },
  {
    icon: CreditCard,
    title: "Wszystkie konta",
    description: "Połącz wszystkie konta bankowe, karty kredytowe i portfele w jednym panelu.",
  },
  {
    icon: TrendingUp,
    title: "Inwestycje",
    description: "Śledź inwestycje, obliczaj stopy zwrotu i monitoruj dywersyfikację.",
  },
  {
    icon: Shield,
    title: "Bezpieczeństwo",
    description: "Szyfrowane dane, pytania bezpieczeństwa i bezpieczne logowanie JWT.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary-light/30">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-card/80 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center group-hover:bg-primary-dark transition-colors shadow-sm shadow-primary/20">
                <Home className="h-4 w-4 text-white" />
              </div>
              <span className="text-xl font-bold text-foreground tracking-tight">
                Family<span className="text-primary">Organiser</span>
              </span>
            </Link>
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="px-4 py-2 text-sm font-semibold text-muted-foreground hover:text-foreground transition-colors"
              >
                Zaloguj się
              </Link>
              <Link
                to="/register"
                className="px-5 py-2.5 text-sm font-semibold text-white bg-primary hover:bg-primary-dark rounded-xl shadow-sm shadow-primary/20 hover:shadow-md hover:shadow-primary/30 transition-all duration-200 flex items-center gap-1.5"
              >
                <Sparkles className="h-4 w-4" />
                Zacznij za darmo
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-20 -left-20 w-[500px] h-[500px] bg-primary rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-emerald-400 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 sm:pt-28 sm:pb-32">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-light text-primary text-sm font-medium mb-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
              <Sparkles className="h-4 w-4" />
              Nowa wersja już dostępna
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground tracking-tight leading-tight animate-in fade-in slide-in-from-bottom-3 duration-700">
              Finanse rodzinne <span className="text-primary">pod kontrolą</span>
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
              Wspólny budżet, cele oszczędnościowe, śledzenie inwestycji i inteligentne raporty — wszystko w jednym, bezpiecznym miejscu. Dla Ciebie i Twojej rodziny.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4 animate-in fade-in slide-in-from-bottom-5 duration-700">
              <Link
                to="/register"
                className="px-8 py-3.5 text-base font-semibold text-white bg-primary hover:bg-primary-dark rounded-xl shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all duration-300 flex items-center gap-2"
              >
                Rozpocznij za darmo
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                to="/login"
                className="px-8 py-3.5 text-base font-semibold text-foreground bg-card hover:bg-muted rounded-xl border border-border shadow-sm hover:shadow-md transition-all duration-300"
              >
                Zaloguj się
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 sm:py-28 bg-muted/30 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground tracking-tight">
              Wszystko czego potrzebujesz
            </h2>
            <p className="mt-4 text-muted-foreground max-w-xl mx-auto">
              Kompleksowe narzędzie do zarządzania finansami rodziny, zaprojektowane z myślą o prostocie i bezpieczeństwie.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => (
              <div
                key={f.title}
                className="group p-6 rounded-2xl bg-card border border-border shadow-sm hover:shadow-xl hover:border-primary/20 transition-all duration-300 hover:-translate-y-1"
              >
                <div className="w-12 h-12 rounded-xl bg-primary-light flex items-center justify-center mb-4 group-hover:bg-primary group-hover:text-white transition-all duration-300">
                  <f.icon className="h-6 w-6 text-primary group-hover:text-white transition-colors" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 sm:py-28">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="p-10 sm:p-14 rounded-3xl bg-gradient-to-br from-primary-dark via-primary to-emerald-400 text-white shadow-2xl shadow-primary/20 relative overflow-hidden">
            <div className="absolute inset-0 opacity-10">
              <div className="absolute -top-20 -right-20 w-80 h-80 bg-white rounded-full blur-3xl" />
              <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-emerald-300 rounded-full blur-3xl" />
            </div>
            <div className="relative z-10">
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
                Gotowy na porządek w finansach?
              </h2>
              <p className="mt-4 text-emerald-100 text-lg max-w-lg mx-auto">
                Dołącz do rodzin, które już korzystają z FamilyOrganiser. Za darmo, bez zobowiązań.
              </p>
              <Link
                to="/register"
                className="mt-8 inline-flex items-center gap-2 px-8 py-3.5 bg-white text-primary font-semibold rounded-xl shadow-lg hover:shadow-xl hover:bg-emerald-50 transition-all duration-300"
              >
                Utwórz darmowe konto
                <ArrowRight className="h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
                <Home className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="text-sm font-semibold text-foreground">
                Family<span className="text-primary">Organiser</span>
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              © 2025 FamilyOrganiser. Wszelkie prawa zastrzeżone.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
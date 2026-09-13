import { Link } from "react-router-dom";
import { Home } from "lucide-react";

/** Rejestracja = magic link / Google na stronie logowania (Supabase Auth). */
export default function RegisterPage() {
  return (
    <div className="min-h-dvh flex items-center justify-center p-6 bg-gradient-to-br from-background via-background to-primary-light/20">
      <div className="w-full max-w-md bg-card/80 border border-border rounded-2xl shadow-xl p-8 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mx-auto">
          <Home className="h-6 w-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-foreground">Załóż konto</h1>
        <p className="text-sm text-muted-foreground">
          Konta tworzone są automatycznie przy pierwszym logowaniu — magic linkiem
          albo przez Google.
        </p>
        <p className="text-xs leading-5 text-muted-foreground">
          Przy pierwszym logowaniu utworzymy profil potrzebny do działania usługi. Dowiedz się,
          jak chronimy dane, w <Link className="text-primary underline" to="/privacy">Polityce prywatności</Link>.
        </p>
        <Link
          to="/login"
          className="inline-flex items-center justify-center rounded-lg bg-primary text-white px-4 py-2.5 text-sm font-semibold hover:bg-primary-dark transition-colors"
        >
          Przejdź do logowania
        </Link>
      </div>
    </div>
  );
}

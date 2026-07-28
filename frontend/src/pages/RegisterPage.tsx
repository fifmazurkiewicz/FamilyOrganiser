import { Link } from "react-router-dom";
import { Home } from "lucide-react";

/** Rejestracja = magic link / Google na stronie logowania (Supabase Auth). */
export default function RegisterPage() {
  return (
    <div className="min-h-dvh flex items-center justify-center p-6 bg-gradient-to-br from-gray-50 via-white to-primary-light/20">
      <div className="w-full max-w-md bg-white/80 border border-gray-100 rounded-2xl shadow-xl p-8 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mx-auto">
          <Home className="h-6 w-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Załóż konto</h1>
        <p className="text-sm text-gray-500">
          Konta tworzone są automatycznie przy pierwszym logowaniu — magic linkiem
          albo przez Google.
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

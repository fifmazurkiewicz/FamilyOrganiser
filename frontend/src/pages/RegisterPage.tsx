import { Link } from "react-router-dom";
import { RegisterForm } from "@/features/auth/RegisterForm";
import { Home, Users, TrendingUp, Shield } from "lucide-react";

const features = [
  { icon: Users, label: "Wspólne grupy rodzinne" },
  { icon: TrendingUp, label: "Cele oszczędnościowe" },
  { icon: Shield, label: "Bezpieczeństwo danych" },
];

export default function RegisterPage() {
  return (
    <div className="min-h-dvh flex">
      {/* Left — branding */}
      <div className="hidden lg:flex lg:w-5/12 xl:w-1/2 bg-gradient-to-br from-primary-dark via-primary to-emerald-400 text-white flex-col justify-between p-12 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 -left-20 w-96 h-96 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-10 w-80 h-80 bg-emerald-300 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-white rounded-full blur-3xl" />
        </div>

        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center group-hover:bg-white/30 transition-colors">
              <Home className="h-5 w-5 text-white" />
            </div>
            <span className="text-2xl font-bold tracking-tight">
              Family<span className="text-emerald-200">Organiser</span>
            </span>
          </Link>
        </div>

        <div className="relative z-10 space-y-8">
          <div>
            <h2 className="text-3xl font-bold leading-tight">
              Zacznij organizować<br />finanse rodzinne
            </h2>
            <p className="mt-3 text-emerald-100 text-lg">
              Dołącz do rodzin, które mają pełną kontrolę nad budżetem
            </p>
          </div>

          <div className="space-y-4">
            {features.map((f) => (
              <div key={f.label} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/15 backdrop-blur-sm flex items-center justify-center shrink-0">
                  <f.icon className="h-4 w-4 text-emerald-200" />
                </div>
                <span className="text-white/90 text-sm">{f.label}</span>
              </div>
            ))}
          </div>
        </div>

        <p className="relative z-10 text-emerald-200/70 text-xs">
          © 2025 FamilyOrganiser. Wszelkie prawa zastrzeżone.
        </p>
      </div>

      {/* Right — form */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-50 via-white to-primary-light/20 pb-[max(1rem,env(safe-area-inset-bottom))] pt-[max(1rem,env(safe-area-inset-top))]">
        <div className="w-full max-w-md">
          <div className="lg:hidden text-center mb-6">
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mx-auto mb-3">
              <Home className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
              Family<span className="text-primary">Organiser</span>
            </h1>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 p-5 sm:p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Utwórz konto</h2>
              <p className="mt-1 text-sm text-gray-500">Zacznij zarządzać finansami rodziny</p>
            </div>
            <RegisterForm />
            <p className="mt-8 text-center text-sm text-gray-500">
              Masz już konto?{" "}
              <Link to="/login" className="text-primary font-semibold hover:text-primary-dark transition-colors">
                Zaloguj się →
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
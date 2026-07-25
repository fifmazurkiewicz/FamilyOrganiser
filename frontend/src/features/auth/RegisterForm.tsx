import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "@/lib/api/auth";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Eye, EyeOff, UserPlus } from "lucide-react";

const SECURITY_QUESTIONS = [
  "Jak miało na imię Twoje pierwsze zwierzę domowe?",
  "Jakie jest nazwisko panieńskie Twojej matki?",
  "W jakim mieście chodziłeś/aś do szkoły podstawowej?",
  "Jaki jest tytuł Twojej ulubionej książki z dzieciństwa?",
  "Jaki był model Twojego pierwszego samochodu?",
];

function PasswordStrength({ password }: { password: string }) {
  if (!password) return null;
  const checks = [
    password.length >= 8,
    /[A-Z]/.test(password),
    /[0-9]/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ];
  const score = checks.filter(Boolean).length;
  const labels = ["", "Słabe", "Średnie", "Dobre", "Silne"];
  const colors = ["", "bg-red-500", "bg-orange-500", "bg-yellow-500", "bg-green-500"];

  return (
    <div className="mt-1.5 space-y-1">
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className={`h-1 flex-1 rounded-full transition-colors ${i <= score ? colors[score] : "bg-gray-200"}`} />
        ))}
      </div>
      <p className="text-xs text-gray-500">{labels[score]} hasło</p>
    </div>
  );
}

export function RegisterForm() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    security_question: SECURITY_QUESTIONS[0],
    security_answer: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password.length < 8) {
      setError("Hasło musi mieć co najmniej 8 znaków");
      return;
    }
    setLoading(true);
    try {
      await authApi.register(form);
      navigate("/login");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Błąd rejestracji. Sprawdź dane i spróbuj ponownie.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <Input
        label="Imię i nazwisko"
        value={form.full_name}
        onChange={(e) => setForm({ ...form, full_name: e.target.value })}
        placeholder="Jan Kowalski"
        required
      />
      <Input
        label="Email"
        type="email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        autoComplete="email"
        placeholder="twoj@email.pl"
        required
      />
      <div className="space-y-1">
        <div className="relative">
          <Input
            label="Hasło"
            type={showPassword ? "text" : "password"}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            autoComplete="new-password"
            placeholder="Min. 8 znaków"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-[34px] text-gray-400 hover:text-gray-600 transition-colors"
            tabIndex={-1}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        <PasswordStrength password={form.password} />
      </div>
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">Pytanie bezpieczeństwa</label>
        <select
          className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm bg-white shadow-sm
            focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
          value={form.security_question}
          onChange={(e) => setForm({ ...form, security_question: e.target.value })}
        >
          {SECURITY_QUESTIONS.map((q) => <option key={q} value={q}>{q}</option>)}
        </select>
      </div>
      <Input
        label="Odpowiedź na pytanie"
        value={form.security_answer}
        onChange={(e) => setForm({ ...form, security_answer: e.target.value })}
        placeholder="Twoja odpowiedź"
        required
      />

      {error && (
        <div className="p-3 rounded-lg bg-destructive-muted border border-destructive/20 text-sm text-destructive animate-in fade-in slide-in-from-top-1 duration-200">
          {error}
        </div>
      )}

      <Button type="submit" className="w-full" size="lg" loading={loading}>
        <UserPlus className="h-4 w-4" /> Zarejestruj się
      </Button>
    </form>
  );
}
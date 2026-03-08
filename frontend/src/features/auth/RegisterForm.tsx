import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "@/lib/api/auth";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

const SECURITY_QUESTIONS = [
  "Jak miało na imię Twoje pierwsze zwierzę domowe?",
  "Jakie jest nazwisko panieńskie Twojej matki?",
  "W jakim mieście chodziłeś/aś do szkoły podstawowej?",
  "Jaki jest tytuł Twojej ulubionej książki z dzieciństwa?",
  "Jaki był model Twojego pierwszego samochodu?",
];

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
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
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input label="Imię i nazwisko" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
      <Input label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} autoComplete="email" required />
      <Input label="Hasło" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} autoComplete="new-password" required minLength={8} />
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">Pytanie bezpieczeństwa</label>
        <select
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          value={form.security_question}
          onChange={(e) => setForm({ ...form, security_question: e.target.value })}
        >
          {SECURITY_QUESTIONS.map((q) => <option key={q} value={q}>{q}</option>)}
        </select>
      </div>
      <Input label="Odpowiedź" value={form.security_answer} onChange={(e) => setForm({ ...form, security_answer: e.target.value })} required />
      {error && <p className="text-sm text-red-600">{error}</p>}
      <Button type="submit" className="w-full" loading={loading}>Zarejestruj się</Button>
    </form>
  );
}

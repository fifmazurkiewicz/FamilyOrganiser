import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { api } from "@/api/client";
import { useAuthStore } from "@/stores/authStore";

const SECURITY_QUESTIONS = [
  "Jak miał na imię Twój pierwszy zwierzak?",
  "Jakie jest panieńskie nazwisko Twojej matki?",
  "W jakim mieście się urodziłeś/aś?",
  "Jaka była nazwa Twojej pierwszej szkoły?",
  "Jaki jest Twój ulubiony film?",
  "Inne (wpisz własne pytanie)",
];

const schema = z.object({
  email: z.string().email("Niepoprawny adres e-mail"),
  password: z.string().min(8, "Hasło musi mieć co najmniej 8 znaków"),
  full_name: z.string().min(2, "Imię i nazwisko są wymagane"),
  default_currency: z.string().default("PLN"),
  security_question_preset: z.string(),
  security_question_custom: z.string().optional(),
  security_answer: z.string().min(1, "Odpowiedź jest wymagana"),
});

type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const navigate = useNavigate();
  const { setTokens } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [showCustomQuestion, setShowCustomQuestion] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { default_currency: "PLN" },
  });

  const questionPreset = watch("security_question_preset");

  const onSubmit = async (data: FormData) => {
    setError(null);
    const question =
      data.security_question_preset === "Inne (wpisz własne pytanie)"
        ? data.security_question_custom || ""
        : data.security_question_preset;

    if (!question) {
      setError("Pytanie zabezpieczające jest wymagane");
      return;
    }

    try {
      const res = await api.post("/auth/register", {
        email: data.email,
        password: data.password,
        full_name: data.full_name,
        default_currency: data.default_currency,
        security_question: question,
        security_answer: data.security_answer,
      });
      setTokens(res.data.access_token, res.data.refresh_token);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Błąd rejestracji");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-10">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">FamilyOrganiser</h1>
          <p className="text-gray-500 mt-2">Utwórz nowe konto</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Imię i nazwisko</label>
            <input
              {...register("full_name")}
              placeholder="Jan Kowalski"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            {errors.full_name && <p className="text-red-500 text-xs mt-1">{errors.full_name.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
            <input
              {...register("email")}
              type="email"
              placeholder="jan@rodzina.pl"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Hasło</label>
            <input
              {...register("password")}
              type="password"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Domyślna waluta</label>
            <select
              {...register("default_currency")}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="PLN">PLN</option>
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
              <option value="GBP">GBP</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pytanie zabezpieczające</label>
            <select
              {...register("security_question_preset")}
              onChange={(e) => setShowCustomQuestion(e.target.value === "Inne (wpisz własne pytanie)")}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Wybierz pytanie...</option>
              {SECURITY_QUESTIONS.map((q) => (
                <option key={q} value={q}>{q}</option>
              ))}
            </select>
            {showCustomQuestion && (
              <input
                {...register("security_question_custom")}
                placeholder="Wpisz własne pytanie..."
                className="w-full mt-2 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Odpowiedź na pytanie</label>
            <input
              {...register("security_answer")}
              placeholder="Twoja odpowiedź..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <p className="text-xs text-gray-400 mt-1">Odpowiedź nie jest wrażliwa na wielkość liter</p>
            {errors.security_answer && <p className="text-red-500 text-xs mt-1">{errors.security_answer.message}</p>}
          </div>

          {error && <div className="bg-red-50 text-red-700 text-sm px-3 py-2 rounded-lg">{error}</div>}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-primary text-white py-2 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {isSubmitting ? "Rejestracja..." : "Zarejestruj się"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Masz już konto?{" "}
          <Link to="/login" className="text-primary font-medium hover:underline">
            Zaloguj się
          </Link>
        </p>
      </div>
    </div>
  );
}

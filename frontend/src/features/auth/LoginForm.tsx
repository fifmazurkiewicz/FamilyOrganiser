import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { beginClientSession } from "@/lib/session";
import { authApi } from "@/lib/api/auth";
import { usersApi } from "@/lib/api/users";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Eye, EyeOff, LogIn } from "lucide-react";

export function LoginForm() {
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const tokens = await authApi.login(form);
      beginClientSession(tokens.access_token, tokens.refresh_token);
      const user = await usersApi.me();
      setUser(user);
      navigate("/app");
    } catch (err: unknown) {
      const axiosErr = err as {
        response?: { data?: { detail?: string | { msg?: string }[] } };
        code?: string;
        message?: string;
      };
      const detail = axiosErr.response?.data?.detail;
      if (typeof detail === "string") {
        setError(detail === "Invalid email or password" ? "Nieprawidłowy email lub hasło" : detail);
      } else if (!axiosErr.response) {
        setError("Brak połączenia z API. Uruchom backend na porcie 8000.");
      } else {
        setError("Nieprawidłowy email lub hasło");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form method="post" action="/login" onSubmit={handleSubmit} className="space-y-5" autoComplete="on">
      <Input
        id="login-email"
        label="Email"
        type="email"
        name="username"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        autoComplete="username"
        placeholder="twoj@email.pl"
        required
      />
      <div className="space-y-1">
        <div className="relative">
          <Input
            id="login-password"
            label="Hasło"
            type={showPassword ? "text" : "password"}
            name="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            autoComplete="current-password"
            placeholder="••••••••"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-[34px] text-gray-400 hover:text-gray-600 transition-colors"
            tabIndex={-1}
            aria-label={showPassword ? "Ukryj hasło" : "Pokaż hasło"}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-destructive-muted border border-destructive/20 text-sm text-destructive animate-in fade-in slide-in-from-top-1 duration-200">
          {error}
        </div>
      )}

      <Button type="submit" className="w-full" size="lg" loading={loading}>
        <LogIn className="h-4 w-4" /> Zaloguj się
      </Button>
    </form>
  );
}
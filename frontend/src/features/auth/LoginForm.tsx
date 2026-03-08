import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { authApi } from "@/lib/api/auth";
import { usersApi } from "@/lib/api/users";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export function LoginForm() {
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const tokens = await authApi.login(form);
      setTokens(tokens.access_token, tokens.refresh_token);
      const user = await usersApi.me();
      setUser(user);
      navigate("/");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Nieprawidłowy email lub hasło");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Email"
        type="email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        autoComplete="email"
        required
      />
      <Input
        label="Hasło"
        type="password"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
        autoComplete="current-password"
        required
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
      <Button type="submit" className="w-full" loading={loading}>
        Zaloguj się
      </Button>
    </form>
  );
}

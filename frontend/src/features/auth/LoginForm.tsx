import { useState } from "react";
import { supabase, authRedirectTo } from "@/lib/supabase";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { LogIn, Mail } from "lucide-react";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setInfo("");
    setLoading(true);
    try {
      const { error: otpError } = await supabase.auth.signInWithOtp({
        email: email.trim(),
        options: {
          emailRedirectTo: authRedirectTo(),
          shouldCreateUser: true,
        },
      });
      if (otpError) {
        setError(otpError.message);
        return;
      }
      setInfo("Sprawdź skrzynkę — wysłaliśmy link do logowania.");
    } catch {
      setError("Nie udało się wysłać linku. Spróbuj ponownie.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    setError("");
    setInfo("");
    setGoogleLoading(true);
    try {
      const { error: oauthError } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: authRedirectTo(),
        },
      });
      if (oauthError) {
        setError(oauthError.message);
        setGoogleLoading(false);
      }
    } catch {
      setError("Logowanie Google nie powiodło się.");
      setGoogleLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <form method="post" onSubmit={handleMagicLink} className="space-y-5" autoComplete="on">
        <Input
          id="login-email"
          label="Email"
          type="email"
          name="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          placeholder="twoj@email.pl"
          required
        />

        {error && (
          <div className="p-3 rounded-lg bg-destructive-muted border border-destructive/20 text-sm text-destructive">
            {error}
          </div>
        )}
        {info && (
          <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-sm text-emerald-800">
            {info}
          </div>
        )}

        <Button type="submit" className="w-full" size="lg" loading={loading}>
          <Mail className="h-4 w-4" /> Wyślij magic link
        </Button>
      </form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-2 text-gray-400">lub</span>
        </div>
      </div>

      <Button
        type="button"
        variant="outline"
        className="w-full"
        size="lg"
        loading={googleLoading}
        onClick={handleGoogle}
      >
        <LogIn className="h-4 w-4" /> Kontynuuj z Google
      </Button>
    </div>
  );
}

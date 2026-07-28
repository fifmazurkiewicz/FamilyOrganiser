import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/lib/supabase";
import { usersApi } from "@/lib/api/users";
import { useAuthStore } from "@/stores/authStore";
import { clearClientCaches } from "@/lib/session";

/** OAuth / magic-link redirect target — recovers session from URL. */
export default function AuthCallbackPage() {
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function finish() {
      const { data, error: sessionError } = await supabase.auth.getSession();
      if (cancelled) return;

      if (sessionError || !data.session) {
        setError(sessionError?.message || "Brak sesji po przekierowaniu.");
        return;
      }

      clearClientCaches();
      useAuthStore.setState({
        accessToken: data.session.access_token,
        refreshToken: data.session.refresh_token,
        isAuthenticated: true,
        user: null,
      });

      try {
        const user = await usersApi.me();
        if (!cancelled) {
          setUser(user);
          navigate("/app", { replace: true });
        }
      } catch {
        if (!cancelled) {
          navigate("/app", { replace: true });
        }
      }
    }

    void finish();
    return () => {
      cancelled = true;
    };
  }, [navigate, setUser]);

  if (error) {
    return (
      <div className="min-h-dvh flex flex-col items-center justify-center gap-4 p-6">
        <p className="text-sm text-destructive">{error}</p>
        <a href="/login" className="text-primary text-sm font-medium">
          Wróć do logowania
        </a>
      </div>
    );
  }

  return (
    <div className="min-h-dvh flex items-center justify-center text-sm text-gray-500">
      Finalizowanie logowania…
    </div>
  );
}

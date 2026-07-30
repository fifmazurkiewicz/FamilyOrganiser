import { useEffect, useState, type ReactNode } from "react";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";
import { useAuthStore } from "@/stores/authStore";
import { clearClientCaches } from "@/lib/session";
import { usersApi } from "@/lib/api/users";

async function syncProfile(session: Session | null) {
  if (!session?.access_token) {
    useAuthStore.getState().logout();
    return;
  }

  useAuthStore.setState({
    accessToken: session.access_token,
    refreshToken: session.refresh_token,
    isAuthenticated: true,
  });

  try {
    const user = await usersApi.me();
    useAuthStore.getState().setUser(user);
  } catch {
    // Token OK, profil API jeszcze niedostępny — zostaw sesję
  }
}

/** Hydrates Zustand from Supabase session and keeps them in sync. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let mounted = true;

    const markReady = () => {
      if (mounted) setReady(true);
    };

    const sessionTimeout = window.setTimeout(markReady, 8000);

    supabase.auth
      .getSession()
      .then(({ data }) => {
        if (!mounted) return;
        void syncProfile(data.session).finally(markReady);
      })
      .catch(() => {
        markReady();
      });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_OUT") {
        clearClientCaches();
        useAuthStore.getState().logout();
        return;
      }
      if (event === "SIGNED_IN" || event === "TOKEN_REFRESHED" || event === "INITIAL_SESSION") {
        if (event === "SIGNED_IN") {
          clearClientCaches();
        }
        void syncProfile(session);
      }
    });

    return () => {
      mounted = false;
      window.clearTimeout(sessionTimeout);
      subscription.unsubscribe();
    };
  }, []);

  if (!ready) {
    return (
      <div className="min-h-dvh flex items-center justify-center text-sm text-muted-foreground bg-background">
        Ładowanie…
      </div>
    );
  }

  return <>{children}</>;
}

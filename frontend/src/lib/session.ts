import { queryClient } from "@/lib/queryClient";
import { useAuthStore } from "@/stores/authStore";
import { useGroupStore } from "@/stores/groupStore";
import { supabase } from "@/lib/supabase";

/** Clear cached API data and persisted group selection (call on logout / before new login). */
export function clearClientCaches() {
  queryClient.clear();
  useGroupStore.getState().reset();
}

export async function clearClientSession() {
  clearClientCaches();
  useAuthStore.getState().logout();
  try {
    await supabase.auth.signOut();
  } catch {
    // ignore
  }
}

export function beginClientSession(accessToken: string, refreshToken: string) {
  clearClientCaches();
  useAuthStore.setState({
    accessToken,
    refreshToken,
    isAuthenticated: true,
    user: null,
  });
}

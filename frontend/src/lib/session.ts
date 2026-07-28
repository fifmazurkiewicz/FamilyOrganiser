import { queryClient } from "@/lib/queryClient";
import { useAuthStore } from "@/stores/authStore";
import { useGroupStore } from "@/stores/groupStore";

/** Clear cached API data and persisted group selection (call on logout / before new login). */
export function clearClientCaches() {
  queryClient.clear();
  useGroupStore.getState().reset();
}

export function clearClientSession() {
  clearClientCaches();
  useAuthStore.getState().logout();
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

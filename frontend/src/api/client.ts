import axios from "axios";
import { useAuthStore } from "@/stores/authStore";
import { clearClientSession } from "@/lib/session";
import { supabase } from "@/lib/supabase";

const API_URL = import.meta.env.VITE_API_URL || "";

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const { data, error: refreshError } = await supabase.auth.refreshSession();
        if (refreshError || !data.session) {
          await clearClientSession();
          return Promise.reject(error);
        }
        useAuthStore.getState().setTokens(
          data.session.access_token,
          data.session.refresh_token
        );
        original.headers.Authorization = `Bearer ${data.session.access_token}`;
        return api(original);
      } catch {
        await clearClientSession();
      }
    }
    return Promise.reject(error);
  }
);

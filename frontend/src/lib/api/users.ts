import { api } from "@/api/client";
import type { User } from "@/types";

export interface UserUpdate {
  full_name?: string;
  default_currency?: string;
  avatar_url?: string;
}

export const usersApi = {
  me: async (): Promise<User> => (await api.get("/v1/users/me")).data,

  update: async (data: UserUpdate): Promise<User> =>
    (await api.patch("/v1/users/me", data)).data,

  // ── Admin ──
  listUsers: async (): Promise<User[]> => (await api.get("/v1/users/")).data,

  lockUser: async (userId: string): Promise<void> => {
    await api.post(`/v1/users/${userId}/lock`);
  },

  unlockUser: async (userId: string): Promise<void> => {
    await api.post(`/v1/users/${userId}/unlock`);
  },

  deleteUser: async (userId: string): Promise<void> => {
    await api.delete(`/v1/users/${userId}`);
  },
};

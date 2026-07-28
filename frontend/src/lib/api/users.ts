import { api } from "@/api/client";

export const usersApi = {
  me: () => api.get("/v1/users/me").then((r) => r.data),

  update: (data: { full_name?: string; default_currency?: string; avatar_url?: string }) =>
    api.patch("/v1/users/me", data).then((r) => r.data),

  listUsers: () => api.get("/v1/users/").then((r) => r.data),

  lockUser: (userId: string) =>
    api.post(`/v1/users/${userId}/lock`).then((r) => r.data),

  unlockUser: (userId: string) =>
    api.post(`/v1/users/${userId}/unlock`).then((r) => r.data),

  deleteUser: (userId: string) =>
    api.delete(`/v1/users/${userId}`).then((r) => r.data),
};

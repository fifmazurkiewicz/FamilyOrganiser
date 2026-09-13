import { api } from "@/api/client";

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  is_app_admin: boolean;
  is_locked: boolean;
  is_active: boolean;
  is_approved: boolean;
}

export const usersApi = {
  me: () => api.get("/v1/users/me").then((r) => r.data),

  update: (data: { full_name?: string; default_currency?: string; avatar_url?: string }) =>
    api.patch("/v1/users/me", data).then((r) => r.data),

  exportMyData: () => api.get("/v1/users/me/export", { responseType: "blob" }),

  deleteMyAccount: () => api.delete("/v1/users/me"),

  listUsers: (): Promise<AdminUser[]> => api.get("/v1/users/").then((r) => r.data),

  lockUser: (userId: string) =>
    api.post(`/v1/users/${userId}/lock`).then((r) => r.data),

  unlockUser: (userId: string) =>
    api.post(`/v1/users/${userId}/unlock`).then((r) => r.data),

  approveUser: (userId: string) =>
    api.post(`/v1/users/${userId}/approve`).then((r) => r.data),

  revokeUser: (userId: string) =>
    api.post(`/v1/users/${userId}/revoke`).then((r) => r.data),

  deleteUser: (userId: string) =>
    api.delete(`/v1/users/${userId}`).then((r) => r.data),
};

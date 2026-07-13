import { api } from "@/api/client";
import type { AuthTokens, LoginRequest, RegisterRequest } from "@/types";

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthTokens> =>
    (await api.post("/v1/auth/login", data)).data,

  register: async (data: RegisterRequest): Promise<AuthTokens> =>
    (await api.post("/v1/auth/register", data)).data,

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await api.post("/v1/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  adminResetPassword: async (userId: string, newPassword: string): Promise<void> => {
    await api.post("/v1/auth/admin/reset-password", {
      user_id: userId,
      new_password: newPassword,
    });
  },
};

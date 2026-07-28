import { api } from "@/api/client";

export const authApi = {
  login: (data: { email: string; password: string }) =>
    api.post("/v1/auth/login", data).then((r) => r.data),

  register: (data: {
    email: string;
    password: string;
    full_name: string;
    security_question: string;
    security_answer: string;
    default_currency?: string;
  }) => api.post("/v1/auth/register", data).then((r) => r.data),

  changePassword: (current_password: string, new_password: string) =>
    api.post("/v1/auth/change-password", { current_password, new_password }).then((r) => r.data),

  adminResetPassword: (userId: string, new_password: string) =>
    api
      .post("/v1/auth/admin/reset-password", { user_id: userId, new_password })
      .then((r) => r.data),
};

import { api } from "@/api/client";
import type { Budget } from "@/types";

export const budgetsApi = {
  list: async (): Promise<Budget[]> => {
    const res = await api.get("/v1/budgets/");
    return res.data;
  },

  get: async (id: string): Promise<Budget> => {
    const res = await api.get(`/v1/budgets/${id}`);
    return res.data;
  },

  create: async (data: Record<string, unknown>): Promise<Budget> => {
    const res = await api.post("/v1/budgets/", data);
    return res.data;
  },

  update: async (id: string, data: Record<string, unknown>): Promise<Budget> => {
    const res = await api.patch(`/v1/budgets/${id}`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/v1/budgets/${id}`);
  },
};

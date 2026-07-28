import { api } from "@/api/client";
import type { Investment, PolishBond } from "@/types";

export const investmentsApi = {
  list: async (): Promise<Investment[]> => {
    const res = await api.get("/v1/investments/");
    return res.data;
  },

  get: async (id: string): Promise<Investment> => {
    const res = await api.get(`/v1/investments/${id}`);
    return res.data;
  },

  create: async (data: Record<string, unknown>): Promise<Investment> => {
    const res = await api.post("/v1/investments/", data);
    return res.data;
  },

  update: async (id: string, data: Record<string, unknown>): Promise<Investment> => {
    const res = await api.patch(`/v1/investments/${id}`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/v1/investments/${id}`);
  },

  listBonds: async (): Promise<PolishBond[]> => {
    const res = await api.get("/v1/investments/bonds/");
    return res.data;
  },

  createBond: async (data: Record<string, unknown>): Promise<PolishBond> => {
    const res = await api.post("/v1/investments/bonds/", data);
    return res.data;
  },

  deleteBond: async (id: string): Promise<void> => {
    await api.delete(`/v1/investments/bonds/${id}`);
  },
};

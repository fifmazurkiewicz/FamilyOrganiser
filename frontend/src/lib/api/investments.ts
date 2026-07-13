import { api } from "@/api/client";
import type { Investment, InvestmentType } from "@/types";

export interface InvestmentCreate {
  name: string;
  investment_type: InvestmentType;
  ticker?: string;
  quantity?: number;
  purchase_price?: number;
  current_price?: number;
  currency?: string;
  purchase_date?: string;
  notes?: string;
}

export const investmentsApi = {
  list: async (): Promise<Investment[]> => (await api.get("/v1/investments/")).data,

  create: async (data: InvestmentCreate): Promise<Investment> =>
    (await api.post("/v1/investments/", data)).data,

  update: async (id: string, data: Record<string, unknown>): Promise<Investment> =>
    (await api.patch(`/v1/investments/${id}`, data)).data,

  delete: async (id: string): Promise<void> => {
    await api.delete(`/v1/investments/${id}`);
  },
};

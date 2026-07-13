import { api } from "@/api/client";
import type { Income, IncomeCategory, IncomeTemplate } from "@/types";

export interface IncomeCreate {
  account_id: string;
  template_id?: string;
  name: string;
  amount: number;
  base_amount?: number;
  currency?: string;
  category: IncomeCategory;
  income_date: string;
  description?: string;
}

export interface IncomeTemplateCreate {
  account_id: string;
  name: string;
  base_amount: number;
  currency?: string;
  category: IncomeCategory;
  day_of_month: number;
}

export const incomeApi = {
  list: async (year?: number, month?: number): Promise<Income[]> =>
    (await api.get("/v1/income/", { params: { year, month } })).data,

  create: async (data: IncomeCreate): Promise<Income> =>
    (await api.post("/v1/income/", data)).data,

  update: async (id: string, data: Record<string, unknown>): Promise<Income> =>
    (await api.patch(`/v1/income/${id}`, data)).data,

  delete: async (id: string): Promise<void> => {
    await api.delete(`/v1/income/${id}`);
  },

  // ── Szablony (np. stałe wynagrodzenie) ──
  listTemplates: async (): Promise<IncomeTemplate[]> =>
    (await api.get("/v1/income/templates")).data,

  createTemplate: async (data: IncomeTemplateCreate): Promise<IncomeTemplate> =>
    (await api.post("/v1/income/templates", data)).data,

  deleteTemplate: async (id: string): Promise<void> => {
    await api.delete(`/v1/income/templates/${id}`);
  },
};

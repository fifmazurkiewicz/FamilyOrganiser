import { api } from "@/api/client";
import type { Budget } from "@/types";

export interface BudgetCategoryInput {
  category_id: string;
  planned_amount: number;
  currency?: string;
}

export interface BudgetCreate {
  name: string;
  scope?: "personal" | "family";
  year: number;
  month?: number;
  alert_threshold_percent?: number;
  categories: BudgetCategoryInput[];
}

export const budgetsApi = {
  list: async (): Promise<Budget[]> => (await api.get("/v1/budgets/")).data,

  create: async (data: BudgetCreate): Promise<Budget> =>
    (await api.post("/v1/budgets/", data)).data,

  delete: async (id: string): Promise<void> => {
    await api.delete(`/v1/budgets/${id}`);
  },
};

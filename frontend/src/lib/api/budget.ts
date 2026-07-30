import { api } from "@/api/client";

export type BudgetEntryType = "income" | "expense";

export interface BudgetEntry {
  id: string;
  budget_id?: string;
  name: string;
  amount: number;
  entry_type: BudgetEntryType;
  is_recurring: boolean;
  currency?: string;
}

export interface MonthlyBudget {
  id: string;
  year: number;
  month: number;
  family_group_id?: string;
  entries: BudgetEntry[];
}

export interface BudgetEntryCreate {
  name: string;
  amount: number;
  entry_type: BudgetEntryType;
  is_recurring: boolean;
  year?: number;
  month?: number;
  currency?: string;
}

export const budgetApi = {
  getByMonth: (year: number, month: number, familyGroupId: string): Promise<MonthlyBudget> =>
    api
      .get("/v1/monthly-budgets/by-month", {
        params: { year, month, family_group_id: familyGroupId },
      })
      .then((r) => r.data),

  addEntry: (budgetId: string, data: BudgetEntryCreate) =>
    api.post(`/v1/monthly-budgets/${budgetId}/entries`, data).then((r) => r.data),

  updateEntry: (entryId: string, data: Partial<BudgetEntryCreate>) =>
    api.patch(`/v1/monthly-budgets/entries/${entryId}`, data).then((r) => r.data),

  deleteEntry: (entryId: string) =>
    api.delete(`/v1/monthly-budgets/entries/${entryId}`).then((r) => r.data),
};

export function isIncomeEntry(entry: BudgetEntry): boolean {
  return entry.entry_type === "income";
}

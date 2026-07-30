import { api } from "@/api/client";

export interface ExpenseByCategory {
  category: string;
  amount: number;
}

export interface MonthlyTrendPoint {
  month: string;
  income: number;
  expenses: number;
}

export const reportsApi = {
  dashboard: (familyGroupId?: string) =>
    api
      .get("/v1/reports/dashboard", {
        params: familyGroupId ? { family_group_id: familyGroupId } : undefined,
      })
      .then((r) => r.data),

  expensesByCategory: (
    year: number,
    month?: number,
    familyGroupId?: string
  ): Promise<ExpenseByCategory[]> =>
    api
      .get("/v1/reports/expenses-by-category", {
        params: {
          year,
          month,
          ...(familyGroupId ? { family_group_id: familyGroupId } : {}),
        },
      })
      .then((r) => r.data),

  monthlyTrend: (months = 12, familyGroupId?: string): Promise<MonthlyTrendPoint[]> =>
    api
      .get("/v1/reports/monthly-trend", {
        params: {
          months,
          ...(familyGroupId ? { family_group_id: familyGroupId } : {}),
        },
      })
      .then((r) => r.data),
};

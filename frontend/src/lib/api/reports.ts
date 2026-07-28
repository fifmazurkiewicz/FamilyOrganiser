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
  dashboard: () => api.get("/v1/reports/dashboard").then((r) => r.data),

  expensesByCategory: (year: number, month?: number): Promise<ExpenseByCategory[]> =>
    api
      .get("/v1/reports/expenses-by-category", { params: { year, month } })
      .then((r) => r.data),

  monthlyTrend: (months = 12): Promise<MonthlyTrendPoint[]> =>
    api.get("/v1/reports/monthly-trend", { params: { months } }).then((r) => r.data),
};

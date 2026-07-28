import { api } from "@/api/client";

export const reportsApi = {
  dashboard: () => api.get("/v1/reports/dashboard").then((r) => r.data),

  expensesByCategory: (year: number, month?: number) =>
    api
      .get("/v1/reports/expenses-by-category", { params: { year, month } })
      .then((r) => r.data),

  monthlyTrend: (months = 12) =>
    api.get("/v1/reports/monthly-trend", { params: { months } }).then((r) => r.data),
};

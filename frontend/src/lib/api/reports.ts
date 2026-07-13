import { api } from "@/api/client";
import type { DashboardData, MonthlyTrend } from "@/types";

export interface CategoryExpense {
  category: string;
  amount: number;
}

/** Zakres dat (pierwszy/ostatni dzień) dla roku lub konkretnego miesiąca. */
function monthRange(year: number, month?: number): { start_date: string; end_date: string } {
  const start = new Date(Date.UTC(year, month ? month - 1 : 0, 1));
  const end = month ? new Date(Date.UTC(year, month, 0)) : new Date(Date.UTC(year, 11, 31));
  return {
    start_date: start.toISOString().split("T")[0],
    end_date: end.toISOString().split("T")[0],
  };
}

export const reportsApi = {
  dashboard: async (): Promise<DashboardData> =>
    (await api.get("/v1/reports/dashboard")).data,

  expensesByCategory: async (year: number, month?: number): Promise<CategoryExpense[]> => {
    const { data } = await api.get("/v1/reports/expenses-by-category", { params: { year, month } });
    // Backend zwraca kwoty jako stringi (Decimal) — normalizujemy do liczb dla wykresów.
    return (data as { category: string; amount: string | number }[]).map((row) => ({
      category: row.category,
      amount: Number(row.amount),
    }));
  },

  monthlyTrend: async (months = 12): Promise<MonthlyTrend[]> =>
    (await api.get("/v1/reports/monthly-trend", { params: { months } })).data,

  /** Pobiera eksport transakcji jako plik .xlsx i uruchamia pobieranie w przeglądarce. */
  exportExcel: async (year: number, month?: number): Promise<void> => {
    const response = await api.get("/v1/reports/export/transactions", {
      params: monthRange(year, month),
      responseType: "blob",
    });
    const url = URL.createObjectURL(response.data as Blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = month
      ? `transakcje-${year}-${String(month).padStart(2, "0")}.xlsx`
      : `transakcje-${year}.xlsx`;
    link.click();
    URL.revokeObjectURL(url);
  },
};

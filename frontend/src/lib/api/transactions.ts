import { api } from "@/api/client";
import type { Transaction, TransactionCategory } from "@/types";

export type RecurringFrequency = "weekly" | "biweekly" | "monthly";

export interface RecurringTransaction {
  id: string;
  name: string;
  amount: number;
  currency: string;
  transaction_type: "expense" | "income";
  frequency: RecurringFrequency;
  day_of_month: number;
  reminder_days_before: number;
  is_active: boolean;
  start_date: string;
  end_date?: string;
}

export interface RecurringTransactionCreate {
  account_id: string;
  category_id?: string;
  name: string;
  amount: number;
  currency?: string;
  transaction_type: "expense" | "income";
  frequency: RecurringFrequency;
  day_of_month?: number;
  start_date: string;
  end_date?: string;
  description?: string;
}

export interface TransactionFilters {
  account_id?: string;
  category_id?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

export interface TransactionCreate {
  account_id: string;
  category_id?: string;
  transaction_type: "expense" | "income" | "transfer";
  amount: number;
  currency?: string;
  transaction_date: string;
  description?: string;
  merchant?: string;
}

export const transactionsApi = {
  list: async (filters?: TransactionFilters): Promise<Transaction[]> =>
    (await api.get("/v1/transactions/", { params: filters })).data,

  create: async (data: TransactionCreate): Promise<Transaction> =>
    (await api.post("/v1/transactions/", data)).data,

  update: async (id: string, data: Record<string, unknown>): Promise<Transaction> =>
    (await api.patch(`/v1/transactions/${id}`, data)).data,

  delete: async (id: string): Promise<void> => {
    await api.delete(`/v1/transactions/${id}`);
  },

  listCategories: async (): Promise<TransactionCategory[]> =>
    (await api.get("/v1/transactions/categories")).data,

  // ── Transakcje cykliczne ──
  listRecurring: async (): Promise<RecurringTransaction[]> =>
    (await api.get("/v1/transactions/recurring/list")).data,

  createRecurring: async (data: RecurringTransactionCreate): Promise<RecurringTransaction> =>
    (await api.post("/v1/transactions/recurring", data)).data,

  deactivateRecurring: async (id: string): Promise<void> => {
    await api.delete(`/v1/transactions/recurring/${id}`);
  },
};

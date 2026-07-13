import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { transactionsApi } from "@/lib/api/transactions";
import { invalidateFinanceViews } from "./invalidate";

export const TRANSACTIONS_KEY = ["transactions"] as const;
export const CATEGORIES_KEY = ["categories"] as const;

export function useTransactions(filters?: Parameters<typeof transactionsApi.list>[0]) {
  return useQuery({
    queryKey: [...TRANSACTIONS_KEY, filters],
    queryFn: () => transactionsApi.list(filters),
  });
}

export function useCategories() {
  return useQuery({
    queryKey: CATEGORIES_KEY,
    queryFn: transactionsApi.listCategories,
    staleTime: Infinity,
  });
}

export function useCreateTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: transactionsApi.create,
    onSuccess: () => invalidateFinanceViews(qc, TRANSACTIONS_KEY),
  });
}

export function useUpdateTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      transactionsApi.update(id, data),
    onSuccess: () => invalidateFinanceViews(qc, TRANSACTIONS_KEY),
  });
}

export function useDeleteTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: transactionsApi.delete,
    onSuccess: () => invalidateFinanceViews(qc, TRANSACTIONS_KEY),
  });
}

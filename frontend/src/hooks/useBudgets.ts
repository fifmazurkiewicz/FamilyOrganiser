import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { budgetsApi } from "@/lib/api/budgets";

export const BUDGETS_KEY = ["budgets"] as const;

export function useBudgets() {
  return useQuery({ queryKey: BUDGETS_KEY, queryFn: budgetsApi.list });
}

export function useCreateBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: budgetsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: BUDGETS_KEY }),
  });
}

export function useDeleteBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: budgetsApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: BUDGETS_KEY }),
  });
}

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { savingsApi } from "@/lib/api/savings";

export const SAVINGS_KEY = ["savings"] as const;

export function useSavingsGoals() {
  return useQuery({ queryKey: SAVINGS_KEY, queryFn: savingsApi.listGoals });
}

export function useCreateGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: savingsApi.createGoal,
    onSuccess: () => qc.invalidateQueries({ queryKey: SAVINGS_KEY }),
  });
}

export function useUpdateGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      savingsApi.updateGoal(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: SAVINGS_KEY }),
  });
}

export function useDeleteGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: savingsApi.deleteGoal,
    onSuccess: () => qc.invalidateQueries({ queryKey: SAVINGS_KEY }),
  });
}

export function useAddContribution(goalId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof savingsApi.addContribution>[1]) =>
      savingsApi.addContribution(goalId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: SAVINGS_KEY }),
  });
}

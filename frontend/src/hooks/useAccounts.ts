import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { accountsApi } from "@/lib/api/accounts";

export const ACCOUNTS_KEY = ["accounts"] as const;

export function useAccounts() {
  return useQuery({ queryKey: ACCOUNTS_KEY, queryFn: accountsApi.list });
}

export function useCreateAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: accountsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ACCOUNTS_KEY }),
  });
}

export function useUpdateAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof accountsApi.update>[1] }) =>
      accountsApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ACCOUNTS_KEY }),
  });
}

export function useDeactivateAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: accountsApi.deactivate,
    onSuccess: () => qc.invalidateQueries({ queryKey: ACCOUNTS_KEY }),
  });
}

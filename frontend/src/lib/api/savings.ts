import { api } from "@/api/client";
import type { SavingsContribution, SavingsGoal } from "@/types";

export interface SavingsGoalCreate {
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  target_amount: number;
  currency?: string;
  target_date?: string;
  monthly_contribution?: number;
}

export interface ContributionCreate {
  amount: number;
  contribution_date?: string;
  note?: string;
  is_withdrawal?: boolean;
}

export const savingsApi = {
  listGoals: async (): Promise<SavingsGoal[]> => (await api.get("/v1/savings/")).data,

  createGoal: async (data: SavingsGoalCreate): Promise<SavingsGoal> =>
    (await api.post("/v1/savings/", data)).data,

  updateGoal: async (id: string, data: Record<string, unknown>): Promise<SavingsGoal> =>
    (await api.patch(`/v1/savings/${id}`, data)).data,

  deleteGoal: async (id: string): Promise<void> => {
    await api.delete(`/v1/savings/${id}`);
  },

  addContribution: async (goalId: string, data: ContributionCreate): Promise<SavingsContribution> =>
    (await api.post(`/v1/savings/${goalId}/contributions`, data)).data,
};

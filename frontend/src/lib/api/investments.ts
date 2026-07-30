import { api } from "@/api/client";

export interface Investment {
  id: string;
  name: string;
  investment_type: string;
  principal_amount: number;
  interest_rate: number;
  interest_period: string;
  duration_value: number;
  duration_unit: string;
  start_date: string;
  end_date: string;
  projected_profit: number;
  projected_total: number;
  created_at: string;
}

export interface InvestmentCreate {
  name: string;
  investment_type: string;
  amount: number;
  currency: string;
  rate: number;
  duration_months: number;
  start_date: string;
  family_group_id?: string;
}

export const investmentsApi = {
  list: (familyGroupId?: string): Promise<Investment[]> =>
    api
      .get("/v1/simple-investments/", {
        params: familyGroupId ? { family_group_id: familyGroupId } : undefined,
      })
      .then((r) => r.data),

  create: (data: InvestmentCreate) =>
    api
      .post("/v1/simple-investments/", {
        ...data,
        interest_period: "yearly",
        duration_unit: "months",
        principal_amount: data.amount,
        interest_rate: data.rate,
        duration_value: data.duration_months,
      })
      .then((r) => r.data),

  delete: (id: string) =>
    api.delete(`/v1/simple-investments/${id}`).then((r) => r.data),
};

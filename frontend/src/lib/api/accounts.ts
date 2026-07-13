import { api } from "@/api/client";
import type { Account, AccountType } from "@/types";

export interface AccountCreate {
  name: string;
  account_type: AccountType;
  currency?: string;
  initial_balance?: number;
  color?: string;
  icon?: string;
  is_joint?: boolean;
  credit_limit?: number;
}

export interface AccountUpdate {
  name?: string;
  color?: string;
  icon?: string;
  is_joint?: boolean;
  credit_limit?: number;
}

export const accountsApi = {
  list: async (): Promise<Account[]> => (await api.get("/v1/accounts/")).data,

  create: async (data: AccountCreate): Promise<Account> =>
    (await api.post("/v1/accounts/", data)).data,

  update: async (id: string, data: AccountUpdate): Promise<Account> =>
    (await api.patch(`/v1/accounts/${id}`, data)).data,

  deactivate: async (id: string): Promise<void> => {
    await api.delete(`/v1/accounts/${id}`);
  },
};

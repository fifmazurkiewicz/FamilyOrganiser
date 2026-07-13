import { api } from "@/api/client";
import type { FamilyGroup } from "@/types";

export interface InvitationLink {
  id: string;
  token: string;
  /** Pełny URL zaproszenia, jeśli backend go zwraca; w innym wypadku używamy tokenu. */
  url?: string;
  single_use: boolean;
  used: boolean;
  expires_at: string;
  is_active: boolean;
  created_at: string;
}

export const familyApi = {
  listGroups: async (): Promise<FamilyGroup[]> => (await api.get("/v1/groups/")).data,

  createGroup: async (data: { name: string; description?: string }): Promise<FamilyGroup> =>
    (await api.post("/v1/groups/", data)).data,

  createInvitation: async (groupId: string): Promise<InvitationLink> =>
    (await api.post(`/v1/groups/${groupId}/invitations`, {})).data,

  joinGroup: async (token: string): Promise<{ message: string }> =>
    (await api.post(`/v1/groups/join/${encodeURIComponent(token)}`)).data,

  // ── Admin ──
  adminListAllGroups: async (): Promise<FamilyGroup[]> =>
    (await api.get("/v1/groups/admin/all")).data,

  adminDeleteGroup: async (groupId: string): Promise<void> => {
    await api.delete(`/v1/groups/admin/${groupId}`);
  },
};

import { api } from "@/api/client";

export interface FamilyGroupSummary {
  id: string;
  name: string;
  description?: string;
  member_count: number;
}

export interface AdminFamilyGroup {
  id: string;
  name: string;
  member_count: number;
}

export const familyApi = {
  listGroups: (): Promise<FamilyGroupSummary[]> =>
    api.get("/v1/groups/").then((r) => r.data),

  createGroup: (data: { name: string; description?: string }) =>
    api.post("/v1/groups/", { name: data.name }).then((r) => r.data),

  createInvitation: (groupId: string) =>
    api.post(`/v1/groups/${groupId}/invitations`, {}).then((r) => r.data),

  joinGroup: (token: string) =>
    api.post(`/v1/groups/join/${encodeURIComponent(token)}`).then((r) => r.data),

  adminListAllGroups: (): Promise<AdminFamilyGroup[]> =>
    api.get("/v1/groups/admin/all").then((r) => r.data),

  adminDeleteGroup: (groupId: string) =>
    api.delete(`/v1/groups/admin/${groupId}`).then((r) => r.data),
};

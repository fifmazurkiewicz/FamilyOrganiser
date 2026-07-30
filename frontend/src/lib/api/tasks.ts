import { api } from "@/api/client";

export interface TaskItem {
  id: string;
  title: string;
  is_done: boolean;
  assigned_to?: string;
  assignee_name?: string;
  due_date?: string;
  done_by?: string;
  done_at?: string;
}

export interface TaskList {
  id: string;
  name: string;
  items: TaskItem[];
  created_at: string;
}

export interface FamilyMember {
  id: string;
  user_id: string;
  full_name: string;
}

export const tasksApi = {
  listLists: (familyGroupId: string): Promise<TaskList[]> =>
    api
      .get("/v1/tasks/lists", { params: { family_group_id: familyGroupId } })
      .then((r) => r.data),

  createList: (name: string, familyGroupId: string) =>
    api
      .post("/v1/tasks/lists", { name, family_group_id: familyGroupId })
      .then((r) => r.data),

  deleteList: (listId: string) =>
    api.delete(`/v1/tasks/lists/${listId}`).then((r) => r.data),

  listItems: (listId: string, includeDone = false): Promise<TaskItem[]> =>
    api
      .get(`/v1/tasks/lists/${listId}/items`, {
        params: { include_done: includeDone },
      })
      .then((r) => r.data),

  addItem: (listId: string, title: string) =>
    api.post(`/v1/tasks/lists/${listId}/items`, { title }).then((r) => r.data),

  toggleItem: (itemId: string) =>
    api.post(`/v1/tasks/items/${itemId}/toggle`).then((r) => r.data),

  assignItem: (itemId: string, assignedTo: string | null) =>
    api.patch(`/v1/tasks/items/${itemId}`, { assigned_to: assignedTo }).then((r) => r.data),

  removeItem: (itemId: string) =>
    api.delete(`/v1/tasks/items/${itemId}`).then((r) => r.data),

  listMembers: (groupId: string): Promise<FamilyMember[]> =>
    api.get(`/v1/groups/${groupId}/members`).then((r) => r.data),
};

import { api } from "@/api/client";

export interface ShoppingItem {
  id: string;
  name: string;
  quantity: number;
  is_bought: boolean;
  bought_by?: string;
  bought_at?: string;
}

export interface ShoppingList {
  id: string;
  name: string;
  items: ShoppingItem[];
  created_at: string;
}

export const shoppingApi = {
  listLists: (familyGroupId: string): Promise<ShoppingList[]> =>
    api
      .get("/v1/shopping/lists", { params: { family_group_id: familyGroupId } })
      .then((r) => r.data),

  createList: (name: string, familyGroupId: string) =>
    api
      .post("/v1/shopping/lists", { name, family_group_id: familyGroupId })
      .then((r) => r.data),

  deleteList: (listId: string) =>
    api.delete(`/v1/shopping/lists/${listId}`).then((r) => r.data),

  listItems: (listId: string, includeDone = false): Promise<ShoppingItem[]> =>
    api
      .get(`/v1/shopping/lists/${listId}/items`, {
        params: { include_done: includeDone },
      })
      .then((r) => r.data),

  addItem: (listId: string, name: string, quantity = 1) =>
    api
      .post(`/v1/shopping/lists/${listId}/items`, { name, quantity })
      .then((r) => r.data),

  toggleItem: (itemId: string) =>
    api.post(`/v1/shopping/items/${itemId}/toggle`).then((r) => r.data),

  removeItem: (itemId: string) =>
    api.delete(`/v1/shopping/items/${itemId}`).then((r) => r.data),
};

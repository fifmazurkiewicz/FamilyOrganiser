import { api } from "@/api/client";
import type { Notification } from "@/types";

export const notificationsApi = {
  list: async (): Promise<Notification[]> => (await api.get("/v1/notifications/")).data,

  unreadCount: async (): Promise<{ count: number }> =>
    (await api.get("/v1/notifications/count")).data,

  markRead: async (id: string): Promise<void> => {
    await api.post(`/v1/notifications/${id}/read`);
  },

  markAllRead: async (): Promise<void> => {
    await api.post("/v1/notifications/read-all");
  },
};

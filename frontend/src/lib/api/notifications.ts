import { api } from "@/api/client";

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export const notificationsApi = {
  list: (): Promise<AppNotification[]> =>
    api.get("/v1/notifications/").then((r) => r.data),

  unreadCount: () =>
    api.get("/v1/notifications/count").then((r) => r.data.count as number),

  markRead: (id: string) => api.post(`/v1/notifications/${id}/read`),

  markAllRead: () => api.post("/v1/notifications/read-all"),
};

import { api } from "@/api/client";

export const notificationsApi = {
  list: () => api.get("/v1/notifications/").then((r) => r.data),

  unreadCount: () =>
    api.get("/v1/notifications/count").then((r) => r.data.count as number),

  markRead: (id: string) => api.post(`/v1/notifications/${id}/read`),

  markAllRead: () => api.post("/v1/notifications/read-all"),
};

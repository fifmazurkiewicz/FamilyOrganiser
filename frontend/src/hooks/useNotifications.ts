import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "@/lib/api/notifications";

const NOTIF_KEY = ["notifications"] as const;
const COUNT_KEY = ["notif-count"] as const;

export function useNotifications() {
  return useQuery({ queryKey: NOTIF_KEY, queryFn: notificationsApi.list });
}

export function useNotificationCount() {
  return useQuery({
    queryKey: COUNT_KEY,
    queryFn: notificationsApi.unreadCount,
    refetchInterval: 30_000,
  });
}

export function useMarkRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: notificationsApi.markRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: NOTIF_KEY });
      qc.invalidateQueries({ queryKey: COUNT_KEY });
    },
  });
}

export function useMarkAllRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: NOTIF_KEY });
      qc.invalidateQueries({ queryKey: COUNT_KEY });
    },
  });
}

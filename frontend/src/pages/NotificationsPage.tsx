import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Bell, Check } from "lucide-react";

export default function NotificationsPage() {
  const qc = useQueryClient();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => api.get("/notifications/").then((r) => r.data),
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => api.post(`/notifications/${id}/read`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notif-count"] });
    },
  });

  const markAllMutation = useMutation({
    mutationFn: () => api.post("/notifications/read-all"),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notif-count"] });
    },
  });

  const unreadCount = notifications.filter((n: any) => !n.is_read).length;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Powiadomienia</h1>
          {unreadCount > 0 && (
            <p className="text-gray-500 text-sm">{unreadCount} nieprzeczytanych</p>
          )}
        </div>
        {unreadCount > 0 && (
          <button
            onClick={() => markAllMutation.mutate()}
            className="flex items-center gap-2 border border-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm hover:bg-gray-50"
          >
            <Check className="h-4 w-4" />
            Oznacz wszystkie jako przeczytane
          </button>
        )}
      </div>

      {isLoading ? (
        <p className="text-gray-400">Ładowanie...</p>
      ) : notifications.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <Bell className="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p>Brak powiadomień</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n: any) => (
            <div
              key={n.id}
              className={`bg-white rounded-xl border p-4 flex items-start gap-3 ${
                !n.is_read ? "border-primary/30 bg-blue-50/30" : "border-gray-100"
              }`}
            >
              <div
                className={`rounded-full p-2 flex-shrink-0 ${
                  !n.is_read ? "bg-primary text-white" : "bg-gray-100 text-gray-500"
                }`}
              >
                <Bell className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{n.title}</p>
                <p className="text-sm text-gray-500 mt-0.5">{n.body}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {new Date(n.created_at).toLocaleString("pl-PL")}
                </p>
              </div>
              {!n.is_read && (
                <button
                  onClick={() => markReadMutation.mutate(n.id)}
                  className="text-xs text-primary hover:underline flex-shrink-0"
                >
                  Przeczytano
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { Bell, CheckCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useNotifications, useMarkRead, useMarkAllRead } from "@/hooks/useNotifications";
import { formatDistanceToNow } from "date-fns";
import { pl } from "date-fns/locale";

export function NotificationCenter() {
  const { data: notifications, isLoading } = useNotifications();
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();

  if (isLoading) return <Spinner />;

  const unread = notifications?.filter((n) => !n.is_read).length ?? 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Powiadomienia {unread > 0 && <Badge variant="danger">{unread}</Badge>}
        </h2>
        {unread > 0 && (
          <Button variant="outline" size="sm" onClick={() => markAllRead.mutate()} loading={markAllRead.isPending}>
            <CheckCheck className="h-4 w-4" /> Oznacz wszystkie
          </Button>
        )}
      </div>

      <Card>
        {!notifications || notifications.length === 0 ? (
          <EmptyState icon={Bell} title="Brak powiadomień" description="Nie masz nowych powiadomień." />
        ) : (
          <div className="divide-y divide-gray-50">
            {notifications.map((n) => (
              <div
                key={n.id}
                className={`flex gap-3 px-6 py-4 ${!n.is_read ? "bg-blue-50/50" : ""}`}
              >
                <div className="mt-0.5">
                  {!n.is_read && (
                    <span className="inline-block h-2 w-2 rounded-full bg-blue-500" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{n.title}</p>
                  <p className="text-sm text-gray-500 mt-0.5">{n.message}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {formatDistanceToNow(new Date(n.created_at), { addSuffix: true, locale: pl })}
                  </p>
                </div>
                {!n.is_read && (
                  <button
                    className="text-xs text-blue-600 hover:underline whitespace-nowrap"
                    onClick={() => markRead.mutate(n.id)}
                  >
                    Przeczytane
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

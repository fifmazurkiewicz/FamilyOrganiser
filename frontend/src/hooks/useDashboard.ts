import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api/reports";
import { useGroupStore } from "@/stores/groupStore";

export function useDashboard() {
  const { activeGroup } = useGroupStore();

  return useQuery({
    queryKey: ["dashboard", activeGroup?.id],
    queryFn: () => reportsApi.dashboard(activeGroup!.id),
    enabled: !!activeGroup?.id,
  });
}

export function useMonthlyTrend(months = 12) {
  const { activeGroup } = useGroupStore();

  return useQuery({
    queryKey: ["monthly-trend", months, activeGroup?.id],
    queryFn: () => reportsApi.monthlyTrend(months, activeGroup!.id),
    enabled: !!activeGroup?.id,
  });
}

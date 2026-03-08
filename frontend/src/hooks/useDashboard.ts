import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api/reports";

export function useDashboard() {
  return useQuery({ queryKey: ["dashboard"], queryFn: reportsApi.dashboard });
}

export function useMonthlyTrend(months = 12) {
  return useQuery({
    queryKey: ["monthly-trend", months],
    queryFn: () => reportsApi.monthlyTrend(months),
  });
}

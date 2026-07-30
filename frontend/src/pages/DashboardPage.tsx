import { DashboardSummary } from "@/features/dashboard/DashboardSummary";

export default function DashboardPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Dashboard</h1>
      <DashboardSummary />
    </div>
  );
}

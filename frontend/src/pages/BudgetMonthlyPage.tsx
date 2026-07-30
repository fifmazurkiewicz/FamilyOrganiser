import { BudgetPanel } from "@/features/budget-monthly/BudgetPanel";

export default function BudgetMonthlyPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Budżet miesięczny</h1>
      <BudgetPanel />
    </div>
  );
}
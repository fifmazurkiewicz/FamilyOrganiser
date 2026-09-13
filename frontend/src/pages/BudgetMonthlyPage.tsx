import { BudgetPanel } from "@/features/budget-monthly/BudgetPanel";

export default function BudgetMonthlyPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Budżet miesięczny</h1>
      <p className="mb-4 rounded-xl border border-primary/20 bg-primary-light/40 p-3 text-sm text-muted-foreground">
        Wpisy budżetowe mogą być współdzielone z rodziną. Używaj opisów bez zbędnych danych osobowych.
      </p>
      <BudgetPanel />
    </div>
  );
}

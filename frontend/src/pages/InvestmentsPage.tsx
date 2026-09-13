import { InvestmentList } from "@/features/investments/InvestmentList";

export default function InvestmentsPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Inwestycje</h1>
      <p className="mb-4 rounded-xl border border-primary/20 bg-primary-light/40 p-3 text-sm text-muted-foreground">
        Moduł zapisuje wprowadzone przez Ciebie informacje i wykonuje obliczenia. Nie stanowi porady inwestycyjnej.
      </p>
      <InvestmentList />
    </div>
  );
}

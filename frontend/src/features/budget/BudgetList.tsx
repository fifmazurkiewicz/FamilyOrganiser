import { useState } from "react";
import { Plus, BarChart2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Progress } from "@/components/ui/Progress";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useBudgets, useCreateBudget, useDeleteBudget } from "@/hooks/useBudgets";
import { formatCurrency } from "@/utils/currency";
import type { Budget } from "@/types";

function BudgetCard({ budget, onDelete }: { budget: Budget; onDelete: (id: string) => void }) {
  const totalPlanned = budget.categories.reduce((s, c) => s + c.planned_amount, 0);
  const totalActual = budget.categories.reduce((s, c) => s + c.actual_amount, 0);
  const overBudget = totalActual > totalPlanned;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{budget.name}</CardTitle>
            <p className="text-xs text-gray-500 mt-0.5">
              {budget.year}{budget.month ? `/${String(budget.month).padStart(2, "0")}` : " (roczny)"}
            </p>
          </div>
          <Badge variant={budget.scope === "family" ? "info" : "default"}>
            {budget.scope === "family" ? "Rodzinny" : "Osobisty"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-2 flex justify-between text-sm">
          <span className={overBudget ? "text-red-600 font-medium" : "text-gray-700"}>
            {formatCurrency(totalActual)} / {formatCurrency(totalPlanned)}
          </span>
          <span className="text-gray-400">
            {totalPlanned > 0 ? Math.round((totalActual / totalPlanned) * 100) : 0}%
          </span>
        </div>
        <Progress value={totalActual} max={totalPlanned || 1} />

        {budget.categories.length > 0 && (
          <ul className="mt-3 space-y-2">
            {budget.categories.slice(0, 3).map((c) => (
              <li key={c.id} className="space-y-0.5">
                <div className="flex justify-between text-xs text-gray-600">
                  <span>Kategoria</span>
                  <span>{formatCurrency(c.actual_amount)} / {formatCurrency(c.planned_amount)}</span>
                </div>
                <Progress value={c.actual_amount} max={c.planned_amount || 1} className="h-1" />
              </li>
            ))}
          </ul>
        )}

        <div className="mt-3 flex justify-end">
          <Button variant="ghost" size="sm" className="text-red-500 hover:bg-red-50" onClick={() => onDelete(budget.id)}>
            Usuń
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function BudgetList() {
  const { data: budgets, isLoading } = useBudgets();
  const createBudget = useCreateBudget();
  const deleteBudget = useDeleteBudget();
  const [open, setOpen] = useState(false);
  const now = new Date();
  const [form, setForm] = useState({
    name: "",
    year: String(now.getFullYear()),
    month: String(now.getMonth() + 1),
    scope: "personal" as "personal" | "family",
    alert_threshold_percent: "80",
  });

  const handleCreate = async () => {
    await createBudget.mutateAsync({
      name: form.name,
      year: parseInt(form.year),
      month: form.month ? parseInt(form.month) : undefined,
      scope: form.scope,
      alert_threshold_percent: parseInt(form.alert_threshold_percent),
      categories: [],
    });
    setOpen(false);
  };

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Budżety</h2>
        <Button size="sm" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> Nowy budżet
        </Button>
      </div>

      {!budgets || budgets.length === 0 ? (
        <EmptyState icon={BarChart2} title="Brak budżetów" description="Utwórz budżet, aby kontrolować wydatki." action={{ label: "Utwórz budżet", onClick: () => setOpen(true) }} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {budgets.map((b) => (
            <BudgetCard key={b.id} budget={b} onDelete={(id) => deleteBudget.mutate(id)} />
          ))}
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="Nowy budżet">
        <div className="space-y-4">
          <Input label="Nazwa" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="np. Budżet sierpień 2025" />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Rok" type="number" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} />
            <Input label="Miesiąc (puste = roczny)" type="number" min={1} max={12} value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })} />
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Zakres</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={form.scope} onChange={(e) => setForm({ ...form, scope: e.target.value as "personal" | "family" })}>
              <option value="personal">Osobisty</option>
              <option value="family">Rodzinny</option>
            </select>
          </div>
          <Input label="Próg alertu (%)" type="number" min={1} max={100} value={form.alert_threshold_percent} onChange={(e) => setForm({ ...form, alert_threshold_percent: e.target.value })} />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreate} loading={createBudget.isPending} disabled={!form.name}>
              Utwórz
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

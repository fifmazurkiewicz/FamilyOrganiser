import { useState } from "react";
import { Plus, DollarSign } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { incomeApi } from "@/lib/api/income";
import { accountsApi } from "@/lib/api/accounts";
import { formatCurrency } from "@/utils/currency";
import { format } from "date-fns";
import type { IncomeCategory } from "@/types";

const categoryLabels: Record<IncomeCategory, string> = {
  salary: "Wynagrodzenie",
  freelance: "Freelance",
  rental: "Wynajem",
  dividend: "Dywidenda",
  interest: "Odsetki",
  bonus: "Premia",
  pension: "Emerytura",
  other: "Inne",
};

export function IncomeList() {
  const qc = useQueryClient();
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  const { data: incomes, isLoading } = useQuery({
    queryKey: ["incomes", year, month],
    queryFn: () => incomeApi.list(year, month),
  });
  const { data: accounts } = useQuery({ queryKey: ["accounts"], queryFn: accountsApi.list });
  const createIncome = useMutation({
    mutationFn: incomeApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["incomes"] }),
  });
  const deleteIncome = useMutation({
    mutationFn: incomeApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["incomes"] }),
  });

  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    account_id: "",
    name: "",
    amount: "",
    currency: "PLN",
    category: "salary" as IncomeCategory,
    income_date: now.toISOString().split("T")[0],
    description: "",
  });

  const handleCreate = async () => {
    await createIncome.mutateAsync({
      account_id: form.account_id,
      name: form.name,
      amount: parseFloat(form.amount),
      currency: form.currency,
      category: form.category,
      income_date: form.income_date,
      description: form.description || undefined,
    });
    setOpen(false);
  };

  if (isLoading) return <Spinner />;

  const total = incomes?.reduce((s, i) => s + i.amount, 0) ?? 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Przychody</h2>
          <p className="text-sm text-gray-500">Łącznie: <strong>{formatCurrency(total)}</strong></p>
        </div>
        <div className="flex items-center gap-2">
          <select className="rounded-lg border border-gray-300 px-2 py-1 text-sm" value={month} onChange={(e) => setMonth(parseInt(e.target.value))}>
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>{m.toString().padStart(2, "0")}</option>
            ))}
          </select>
          <Input type="number" value={String(year)} onChange={(e) => setYear(parseInt(e.target.value))} className="w-24" />
          <Button size="sm" onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" /> Dodaj
          </Button>
        </div>
      </div>

      <Card>
        {!incomes || incomes.length === 0 ? (
          <EmptyState icon={DollarSign} title="Brak przychodów" description="Dodaj przychód, aby śledzić zarobki." action={{ label: "Dodaj przychód", onClick: () => setOpen(true) }} />
        ) : (
          <div className="divide-y divide-gray-50">
            {incomes.map((inc) => (
              <div key={inc.id} className="flex items-center gap-3 px-6 py-3 hover:bg-gray-50 group">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{inc.name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <Badge variant="success">{categoryLabels[inc.category]}</Badge>
                    <span className="text-xs text-gray-400">{format(new Date(inc.income_date), "dd.MM.yyyy")}</span>
                    {inc.is_modified && <Badge variant="warning">Zmieniony</Badge>}
                  </div>
                </div>
                <span className="text-sm font-semibold text-emerald-600">
                  +{formatCurrency(inc.amount, inc.currency)}
                </span>
                <button
                  className="invisible group-hover:visible text-gray-400 hover:text-red-500 text-xs"
                  onClick={() => deleteIncome.mutate(inc.id)}
                >
                  Usuń
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Modal open={open} onClose={() => setOpen(false)} title="Nowy przychód">
        <div className="space-y-4">
          <Input label="Nazwa" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="np. Wynagrodzenie marzec" />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Konto</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={form.account_id} onChange={(e) => setForm({ ...form, account_id: e.target.value })}>
              <option value="">Wybierz konto</option>
              {accounts?.filter((a) => a.is_active).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Kategoria</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value as IncomeCategory })}>
              {Object.entries(categoryLabels).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Kwota" type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
            <Input label="Data" type="date" value={form.income_date} onChange={(e) => setForm({ ...form, income_date: e.target.value })} />
          </div>
          <Input label="Opis (opcjonalnie)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreate} loading={createIncome.isPending} disabled={!form.name || !form.account_id || !form.amount}>
              Dodaj
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

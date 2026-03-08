import { useState } from "react";
import { Plus, Receipt, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useTransactions, useCreateTransaction, useDeleteTransaction, useCategories } from "@/hooks/useTransactions";
import { useAccounts } from "@/hooks/useAccounts";
import { formatCurrency } from "@/utils/currency";
import { format } from "date-fns";

export function TransactionList() {
  const { data: transactions, isLoading } = useTransactions({ limit: 50 });
  const { data: accounts } = useAccounts();
  const { data: categories } = useCategories();
  const createTx = useCreateTransaction();
  const deleteTx = useDeleteTransaction();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    account_id: "",
    category_id: "",
    amount: "",
    description: "",
    merchant: "",
    transaction_date: new Date().toISOString().split("T")[0],
    transaction_type: "expense" as "expense" | "income",
    currency: "PLN",
  });

  const handleCreate = async () => {
    await createTx.mutateAsync({
      ...form,
      amount: parseFloat(form.amount),
      category_id: form.category_id || undefined,
      merchant: form.merchant || undefined,
      description: form.description || undefined,
    });
    setOpen(false);
    setForm({ account_id: "", category_id: "", amount: "", description: "", merchant: "", transaction_date: new Date().toISOString().split("T")[0], transaction_type: "expense", currency: "PLN" });
  };

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Transakcje</h2>
        <Button size="sm" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> Dodaj
        </Button>
      </div>

      <Card>
        {!transactions || transactions.length === 0 ? (
          <EmptyState icon={Receipt} title="Brak transakcji" action={{ label: "Dodaj transakcję", onClick: () => setOpen(true) }} />
        ) : (
          <div className="divide-y divide-gray-50">
            {transactions.map((t) => (
              <div key={t.id} className="flex items-center gap-3 px-6 py-3 hover:bg-gray-50 group">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {t.description || t.merchant || "Transakcja"}
                  </p>
                  <p className="text-xs text-gray-400">{format(new Date(t.transaction_date), "dd.MM.yyyy")}</p>
                </div>
                <span
                  className={`text-sm font-semibold ${
                    t.transaction_type === "expense" ? "text-red-600" : "text-emerald-600"
                  }`}
                >
                  {t.transaction_type === "expense" ? "-" : "+"}{formatCurrency(t.amount, t.currency)}
                </span>
                <button
                  className="invisible group-hover:visible text-gray-400 hover:text-red-500"
                  onClick={() => deleteTx.mutate(t.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Modal open={open} onClose={() => setOpen(false)} title="Nowa transakcja">
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Typ</label>
            <select
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              value={form.transaction_type}
              onChange={(e) => setForm({ ...form, transaction_type: e.target.value as "expense" | "income" })}
            >
              <option value="expense">Wydatek</option>
              <option value="income">Przychód</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Konto</label>
            <select
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              value={form.account_id}
              onChange={(e) => setForm({ ...form, account_id: e.target.value })}
            >
              <option value="">Wybierz konto</option>
              {accounts?.filter((a) => a.is_active).map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Kategoria</label>
            <select
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              value={form.category_id}
              onChange={(e) => setForm({ ...form, category_id: e.target.value })}
            >
              <option value="">Bez kategorii</option>
              {categories?.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Kwota" type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
            <Input label="Data" type="date" value={form.transaction_date} onChange={(e) => setForm({ ...form, transaction_date: e.target.value })} />
          </div>
          <Input label="Opis (opcjonalnie)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <Input label="Sprzedawca (opcjonalnie)" value={form.merchant} onChange={(e) => setForm({ ...form, merchant: e.target.value })} />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreate} loading={createTx.isPending} disabled={!form.account_id || !form.amount}>
              Dodaj
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

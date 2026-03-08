import { useState } from "react";
import { Plus, Receipt, Trash2, Repeat, Pencil } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useTransactions, useCreateTransaction, useUpdateTransaction, useDeleteTransaction, useCategories } from "@/hooks/useTransactions";
import { useAccounts } from "@/hooks/useAccounts";
import { transactionsApi, type RecurringTransaction, type RecurringFrequency } from "@/lib/api/transactions";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { formatCurrency } from "@/utils/currency";
import { format } from "date-fns";
import type { Transaction } from "@/types";

const frequencyLabels: Record<RecurringFrequency, string> = {
  weekly: "Raz na tydzień",
  biweekly: "Co 2 tygodnie",
  monthly: "Raz na miesiąc",
};

function EditTransactionForm({
  transaction,
  categories,
  onSave,
  onCancel,
  isLoading,
}: {
  transaction: Transaction;
  accounts: { id: string; name: string; is_active?: boolean }[];
  categories: { id: string; name: string }[];
  onSave: (data: { category_id?: string | null; amount: number; transaction_date: string; description?: string | null }) => void;
  onCancel: () => void;
  isLoading: boolean;
}) {
  const [category_id, setCategoryId] = useState(transaction.category_id ?? "");
  const [amount, setAmount] = useState(String(Math.abs(transaction.amount)));
  const [transaction_date, setTransactionDate] = useState(
    transaction.transaction_date ? new Date(transaction.transaction_date).toISOString().split("T")[0] : ""
  );
  const [description, setDescription] = useState(transaction.description ?? "");

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">Kategoria</label>
        <select
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          value={category_id}
          onChange={(e) => setCategoryId(e.target.value)}
        >
          <option value="">Bez kategorii</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Input label="Kwota" type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} />
        <Input label="Data" type="date" value={transaction_date} onChange={(e) => setTransactionDate(e.target.value)} />
      </div>
      <Input label="Opis (opcjonalnie)" value={description} onChange={(e) => setDescription(e.target.value)} />
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onCancel}>Anuluj</Button>
        <Button
          onClick={() =>
            onSave({
              category_id: category_id || null,
              amount: parseFloat(amount),
              transaction_date,
              description: description || null,
            })
          }
          loading={isLoading}
          disabled={!amount || !transaction_date}
        >
          Zapisz
        </Button>
      </div>
    </div>
  );
}

export function TransactionList() {
  const qc = useQueryClient();
  const { data: transactions, isLoading } = useTransactions({ limit: 50 });
  const { data: accounts } = useAccounts();
  const { data: categories } = useCategories();
  const { data: recurring } = useQuery({
    queryKey: ["recurring-transactions"],
    queryFn: transactionsApi.listRecurring,
  });
  const createTx = useCreateTransaction();
  const updateTx = useUpdateTransaction();
  const deleteTx = useDeleteTransaction();
  const createRecurring = useMutation({
    mutationFn: transactionsApi.createRecurring,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["recurring-transactions"] });
      setRecurringOpen(false);
      setRecurringForm(initialRecurringForm());
    },
  });
  const deactivateRecurring = useMutation({
    mutationFn: transactionsApi.deactivateRecurring,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["recurring-transactions"] }),
  });

  const initialRecurringForm = () => ({
    name: "",
    account_id: "",
    category_id: "",
    amount: "",
    currency: "PLN",
    transaction_type: "expense" as "expense" | "income",
    frequency: "monthly" as RecurringFrequency,
    day_of_month: "1",
    start_date: new Date().toISOString().split("T")[0],
    description: "",
  });

  const [open, setOpen] = useState(false);
  const [editTx, setEditTx] = useState<Transaction | null>(null);
  const [recurringOpen, setRecurringOpen] = useState(false);
  const [recurringForm, setRecurringForm] = useState(initialRecurringForm());
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

  const handleCreateRecurring = async () => {
    await createRecurring.mutateAsync({
      account_id: recurringForm.account_id,
      category_id: recurringForm.category_id || undefined,
      name: recurringForm.name,
      amount: parseFloat(recurringForm.amount),
      currency: recurringForm.currency,
      transaction_type: recurringForm.transaction_type,
      frequency: recurringForm.frequency,
      day_of_month: parseInt(recurringForm.day_of_month) || 1,
      start_date: recurringForm.start_date,
      description: recurringForm.description || undefined,
    });
  };

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Transakcje</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setRecurringOpen(true)}>
            <Repeat className="h-4 w-4" /> Transakcja stała
          </Button>
          <Button size="sm" onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" /> Dodaj
          </Button>
        </div>
      </div>

      {recurring && recurring.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Transakcje stałe</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recurring.map((r) => (
                <div key={r.id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2">
                  <div>
                    <p className="text-sm font-medium">{r.name}</p>
                    <p className="text-xs text-gray-500">
                      {formatCurrency(r.amount, r.currency)} · {frequencyLabels[r.frequency]}
                      {r.frequency === "monthly" && ` (dzień ${r.day_of_month}.)`}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={r.transaction_type === "expense" ? "danger" : "success"}>
                      {r.transaction_type === "expense" ? "Wydatek" : "Przychód"}
                    </Badge>
                    <button
                      className="text-gray-400 hover:text-destructive p-1"
                      onClick={() => deactivateRecurring.mutate(r.id)}
                      title="Usuń"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

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
                    t.transaction_type === "expense" ? "text-destructive" : "text-success"
                  }`}
                >
                  {t.transaction_type === "expense" ? "-" : "+"}{formatCurrency(t.amount, t.currency)}
                </span>
                <div className="flex items-center gap-1 invisible group-hover:visible">
                  <button className="text-gray-400 hover:text-primary p-1" onClick={() => setEditTx(t)} title="Edytuj">
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button className="text-gray-400 hover:text-red-500 p-1" onClick={() => deleteTx.mutate(t.id)} title="Usuń">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Modal open={!!editTx} onClose={() => setEditTx(null)} title="Edytuj transakcję">
        {editTx && (
          <EditTransactionForm
            transaction={editTx}
            accounts={accounts ?? []}
            categories={categories ?? []}
            onSave={(data) => {
              updateTx.mutate({ id: editTx.id, data }, { onSuccess: () => setEditTx(null) });
            }}
            onCancel={() => setEditTx(null)}
            isLoading={updateTx.isPending}
          />
        )}
      </Modal>

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

      <Modal open={recurringOpen} onClose={() => setRecurringOpen(false)} title="Transakcja stała">
        <div className="space-y-4">
          <Input label="Nazwa" value={recurringForm.name} onChange={(e) => setRecurringForm({ ...recurringForm, name: e.target.value })} placeholder="np. Czynsz, Netflix" />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Typ</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={recurringForm.transaction_type} onChange={(e) => setRecurringForm({ ...recurringForm, transaction_type: e.target.value as "expense" | "income" })}>
              <option value="expense">Wydatek</option>
              <option value="income">Przychód</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Konto</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={recurringForm.account_id} onChange={(e) => setRecurringForm({ ...recurringForm, account_id: e.target.value })}>
              <option value="">Wybierz konto</option>
              {accounts?.filter((a) => a.is_active).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Kategoria</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={recurringForm.category_id} onChange={(e) => setRecurringForm({ ...recurringForm, category_id: e.target.value })}>
              <option value="">Bez kategorii</option>
              {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Częstotliwość</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={recurringForm.frequency} onChange={(e) => setRecurringForm({ ...recurringForm, frequency: e.target.value as RecurringFrequency })}>
              {Object.entries(frequencyLabels).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          {recurringForm.frequency === "monthly" && (
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Dzień miesiąca</label>
              <Input type="number" min={1} max={31} value={recurringForm.day_of_month} onChange={(e) => setRecurringForm({ ...recurringForm, day_of_month: e.target.value })} />
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <Input label="Kwota" type="number" step="0.01" value={recurringForm.amount} onChange={(e) => setRecurringForm({ ...recurringForm, amount: e.target.value })} />
            <Input label="Data rozpoczęcia" type="date" value={recurringForm.start_date} onChange={(e) => setRecurringForm({ ...recurringForm, start_date: e.target.value })} />
          </div>
          <Input label="Opis (opcjonalnie)" value={recurringForm.description} onChange={(e) => setRecurringForm({ ...recurringForm, description: e.target.value })} />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setRecurringOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreateRecurring} loading={createRecurring.isPending} disabled={!recurringForm.name || !recurringForm.account_id || !recurringForm.amount}>
              Utwórz
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

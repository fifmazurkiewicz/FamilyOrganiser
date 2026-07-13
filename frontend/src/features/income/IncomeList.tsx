import { useState } from "react";
import { Plus, DollarSign, Repeat, Trash2, Pencil } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { incomeApi } from "@/lib/api/income";
import { accountsApi } from "@/lib/api/accounts";
import { invalidateFinanceViews } from "@/hooks/invalidate";
import { formatCurrency } from "@/utils/currency";
import { format } from "date-fns";
import type { Income, IncomeCategory, IncomeTemplate } from "@/types";

const categoryLabels: Record<string, string> = {
  salary: "Wynagrodzenie",
  freelance: "Freelance",
  rental: "Wynajem",
  dividend: "Dywidenda",
  interest: "Odsetki",
  bonus: "Premia",
  pension: "Emerytura",
  sale: "Sprzedaż",
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
    onSuccess: () => invalidateFinanceViews(qc, ["incomes"]),
  });
  const updateIncome = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      incomeApi.update(id, data),
    onSuccess: () => invalidateFinanceViews(qc, ["incomes"]),
  });
  const deleteIncome = useMutation({
    mutationFn: incomeApi.delete,
    onSuccess: () => invalidateFinanceViews(qc, ["incomes"]),
  });

  const { data: templates } = useQuery({
    queryKey: ["income-templates"],
    queryFn: incomeApi.listTemplates,
  });
  const createTemplate = useMutation({
    mutationFn: incomeApi.createTemplate,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["income-templates"] });
      setTemplateOpen(false);
      setTemplateForm({ name: "Wynagrodzenie stałe", account_id: "", base_amount: "", currency: "PLN", category: "salary" as IncomeCategory, day_of_month: "25" });
    },
  });
  const deleteTemplate = useMutation({
    mutationFn: incomeApi.deleteTemplate,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["income-templates"] }),
  });

  const [open, setOpen] = useState(false);
  const [editInc, setEditInc] = useState<Income | null>(null);
  const [templateOpen, setTemplateOpen] = useState(false);
  const [templateForm, setTemplateForm] = useState({
    name: "Wynagrodzenie stałe",
    account_id: "",
    base_amount: "",
    currency: "PLN",
    category: "salary" as IncomeCategory,
    day_of_month: "25",
  });
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

  const handleCreateTemplate = async () => {
    await createTemplate.mutateAsync({
      account_id: templateForm.account_id,
      name: templateForm.name,
      base_amount: parseFloat(templateForm.base_amount),
      currency: templateForm.currency,
      category: templateForm.category,
      day_of_month: parseInt(templateForm.day_of_month) || 1,
    });
  };

  const handleAddFromTemplate = async (tmpl: IncomeTemplate) => {
    const day = Math.min(tmpl.day_of_month, 28);
    const incomeDate = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    await createIncome.mutateAsync({
      account_id: tmpl.account_id,
      template_id: tmpl.id,
      name: tmpl.name,
      amount: tmpl.base_amount,
      base_amount: tmpl.base_amount,
      currency: tmpl.currency,
      category: tmpl.category,
      income_date: incomeDate,
    });
  };

  const alreadyAddedFromTemplate = (tmplId: string) =>
    incomes?.some((i) => i.template_id === tmplId) ?? false;

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
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Wynagrodzenie stałe</CardTitle>
            <Button variant="outline" size="sm" onClick={() => setTemplateOpen(true)}>
              <Repeat className="h-4 w-4" /> Dodaj wynagrodzenie stałe
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {!templates || templates.length === 0 ? (
            <p className="text-sm text-gray-500">Brak szablonów. Dodaj wynagrodzenie stałe, aby szybko dodawać je co miesiąc.</p>
          ) : (
            <div className="space-y-2">
              {templates.map((tmpl) => (
                <div key={tmpl.id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2">
                  <div>
                    <p className="text-sm font-medium">{tmpl.name}</p>
                    <p className="text-xs text-gray-500">
                      {formatCurrency(tmpl.base_amount, tmpl.currency)} · dzień {tmpl.day_of_month}. · {categoryLabels[tmpl.category] ?? tmpl.category}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleAddFromTemplate(tmpl)}
                      disabled={alreadyAddedFromTemplate(tmpl.id)}
                      loading={createIncome.isPending}
                    >
                      {alreadyAddedFromTemplate(tmpl.id) ? "Dodane" : "Dodaj do miesiąca"}
                    </Button>
                    <button
                      className="text-gray-400 hover:text-destructive text-sm p-1"
                      onClick={() => deleteTemplate.mutate(tmpl.id)}
                      title="Usuń szablon"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

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
                <span className="text-sm font-semibold text-success">
                  +{formatCurrency(inc.amount, inc.currency)}
                </span>
                <div className="flex items-center gap-1 invisible group-hover:visible">
                  <button className="text-gray-400 hover:text-primary p-1" onClick={() => setEditInc(inc)} title="Edytuj">
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button className="text-gray-400 hover:text-red-500 p-1" onClick={() => deleteIncome.mutate(inc.id)} title="Usuń">
                    Usuń
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Modal open={!!editInc} onClose={() => setEditInc(null)} title="Edytuj przychód">
        {editInc && (
          <div className="space-y-4">
            <Input label="Nazwa" value={editInc.name} onChange={(e) => setEditInc({ ...editInc, name: e.target.value })} />
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Konto</label>
              <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={editInc.account_id} onChange={(e) => setEditInc({ ...editInc, account_id: e.target.value })}>
                <option value="">Wybierz konto</option>
                {accounts?.filter((a) => a.is_active).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </div>
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Kategoria</label>
              <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={editInc.category} onChange={(e) => setEditInc({ ...editInc, category: e.target.value as IncomeCategory })}>
                {Object.entries(categoryLabels).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Input label="Kwota" type="number" step="0.01" value={String(editInc.amount)} onChange={(e) => setEditInc({ ...editInc, amount: parseFloat(e.target.value) || 0 })} />
              <Input label="Data" type="date" value={editInc.income_date ? new Date(editInc.income_date).toISOString().split("T")[0] : ""} onChange={(e) => setEditInc({ ...editInc, income_date: e.target.value })} />
            </div>
            <Input label="Opis (opcjonalnie)" value={editInc.description ?? ""} onChange={(e) => setEditInc({ ...editInc, description: e.target.value || undefined })} />
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="outline" onClick={() => setEditInc(null)}>Anuluj</Button>
              <Button
                onClick={() => {
                  updateIncome.mutate(
                    {
                      id: editInc.id,
                      data: {
                        name: editInc.name,
                        account_id: editInc.account_id,
                        amount: editInc.amount,
                        category: editInc.category,
                        income_date: editInc.income_date,
                        description: editInc.description,
                      },
                    },
                    { onSuccess: () => setEditInc(null) }
                  );
                }}
                loading={updateIncome.isPending}
                disabled={!editInc.name || !editInc.account_id || !editInc.amount}
              >
                Zapisz
              </Button>
            </div>
          </div>
        )}
      </Modal>

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

      <Modal open={templateOpen} onClose={() => { setTemplateOpen(false); setTemplateForm({ name: "Wynagrodzenie stałe", account_id: "", base_amount: "", currency: "PLN", category: "salary" as IncomeCategory, day_of_month: "25" }); }} title="Wynagrodzenie stałe">
        <div className="space-y-4">
          <Input label="Nazwa" value={templateForm.name} onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })} placeholder="np. Wynagrodzenie stałe" />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Konto</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={templateForm.account_id} onChange={(e) => setTemplateForm({ ...templateForm, account_id: e.target.value })}>
              <option value="">Wybierz konto</option>
              {accounts?.filter((a) => a.is_active).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Kwota miesięczna" type="number" step="0.01" value={templateForm.base_amount} onChange={(e) => setTemplateForm({ ...templateForm, base_amount: e.target.value })} />
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Dzień wypłaty</label>
              <Input type="number" min={1} max={28} value={templateForm.day_of_month} onChange={(e) => setTemplateForm({ ...templateForm, day_of_month: e.target.value })} />
            </div>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Kategoria</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={templateForm.category} onChange={(e) => setTemplateForm({ ...templateForm, category: e.target.value as IncomeCategory })}>
              {Object.entries(categoryLabels).filter(([k]) => ["salary", "bonus", "freelance", "rental", "dividend", "sale", "other"].includes(k)).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setTemplateOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreateTemplate} loading={createTemplate.isPending} disabled={!templateForm.name || !templateForm.account_id || !templateForm.base_amount}>
              Utwórz
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

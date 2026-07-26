import { useState, useMemo } from "react";
import { Plus, Receipt, User, Calendar, ChevronDown, ChevronUp } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { useToast } from "@/components/ui/Toast";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import { cn } from "@/utils/cn";
import { format } from "date-fns";
import { pl } from "date-fns/locale";

// ── Types ──

interface Expense {
  id: string;
  amount: number;
  currency: string;
  description?: string;
  expense_date: string;
  added_by?: string;
  added_by_name?: string;
}

interface MonthlyGroup {
  month: string;
  label: string;
  expenses: Expense[];
  total: number;
}

// ── Helpers ──

function groupByMonth(expenses: Expense[]): MonthlyGroup[] {
  const groups: Record<string, Expense[]> = {};
  for (const e of expenses) {
    const key = e.expense_date.slice(0, 7);
    (groups[key] ??= []).push(e);
  }
  return Object.entries(groups)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([month, exps]) => ({
      month,
      label: format(new Date(month + "-01"), "LLLL yyyy", { locale: pl }),
      expenses: exps,
      total: exps.reduce((s, e) => s + e.amount, 0),
    }));
}

// ── Main Component ──

export function ExpenseList() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const [addOpen, setAddOpen] = useState(false);
  const [collapsedMonths, setCollapsedMonths] = useState<Set<string>>(new Set());
  const [form, setForm] = useState({
    amount: "",
    description: "",
    expense_date: new Date().toISOString().slice(0, 10),
  });

  const { data: expenses, isLoading } = useQuery<Expense[]>({
    queryKey: ["expenses"],
    queryFn: () => api.get("/v1/simple-expenses/").then((r) => r.data),
  });

  const addExpense = useMutation({
    mutationFn: (data: { amount: number; description: string; expense_date: string }) =>
      api.post("/v1/simple-expenses/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["expenses"] });
      setAddOpen(false);
      setForm({ amount: "", description: "", expense_date: new Date().toISOString().slice(0, 10) });
      toast("success", "Dodano", "Wydatek został dodany.");
    },
    onError: () => toast("error", "Błąd", "Nie udało się dodać wydatku."),
  });

  const deleteExpense = useMutation({
    mutationFn: (id: string) => api.delete(`/v1/simple-expenses/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["expenses"] });
      toast("success", "Usunięto", "Wydatek został usunięty.");
    },
  });

  const monthlyGroups = useMemo(
    () => (expenses ? groupByMonth(expenses) : []),
    [expenses]
  );

  const toggleMonth = (month: string) => {
    setCollapsedMonths((prev) => {
      const next = new Set(prev);
      next.has(month) ? next.delete(month) : next.add(month);
      return next;
    });
  };

  const handleAdd = () => {
    const amt = parseFloat(form.amount);
    if (!amt || amt <= 0) return;
    addExpense.mutate({
      amount: amt,
      description: form.description,
      expense_date: form.expense_date,
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-7 w-32" />
          <Skeleton className="h-8 w-36" />
        </div>
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Wydatki</h2>
        <Button size="sm" onClick={() => setAddOpen(true)}>
          <Plus className="h-4 w-4" /> Dodaj wydatek
        </Button>
      </div>

      {!expenses || expenses.length === 0 ? (
        <EmptyState
          icon={Receipt}
          title="Brak wydatków"
          description="Dodaj pierwszy wydatek, aby śledzić finanse."
          action={{ label: "Dodaj wydatek", onClick: () => setAddOpen(true) }}
        />
      ) : (
        <div className="space-y-4">
          {/* Monthly groups */}
          {monthlyGroups.map((group) => (
            <Card key={group.month}>
              <button
                onClick={() => toggleMonth(group.month)}
                className="w-full px-5 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors rounded-t-xl"
              >
                <div className="flex items-center gap-3">
                  <h3 className="text-base font-semibold text-gray-900 capitalize">
                    {group.label}
                  </h3>
                  <Badge variant="info">{group.expenses.length} wydatków</Badge>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-semibold text-destructive">
                    {formatCurrency(group.total)}
                  </span>
                  {collapsedMonths.has(group.month) ? (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  )}
                </div>
              </button>

              {!collapsedMonths.has(group.month) && (
                <CardContent className="border-t border-gray-100 pt-0">
                  <div className="divide-y divide-gray-50">
                    {group.expenses.map((exp) => (
                      <div
                        key={exp.id}
                        className="flex items-center justify-between py-3 group"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">
                            {exp.description || "Bez opisu"}
                          </p>
                          <div className="flex items-center gap-3 text-xs text-gray-400 mt-0.5">
                            <span className="inline-flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {format(new Date(exp.expense_date), "dd.MM.yyyy", {
                                locale: pl,
                              })}
                            </span>
                            {exp.added_by_name && (
                              <span className="inline-flex items-center gap-1">
                                <User className="h-3 w-3" />
                                {exp.added_by_name}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-destructive">
                            {formatCurrency(exp.amount, exp.currency)}
                          </span>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={() => deleteExpense.mutate(exp.id)}
                          >
                            ✕
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}

      {/* Add expense modal */}
      <Modal
        open={addOpen}
        onClose={() => setAddOpen(false)}
        title="Dodaj wydatek"
      >
        <div className="space-y-4">
          <Input
            label="Kwota"
            type="number"
            step="0.01"
            value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
            placeholder="0.00"
          />
          <Input
            label="Opis"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="np. Zakupy w Biedronce"
          />
          <Input
            label="Data"
            type="date"
            value={form.expense_date}
            onChange={(e) => setForm({ ...form, expense_date: e.target.value })}
          />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setAddOpen(false)}>
              Anuluj
            </Button>
            <Button
              onClick={handleAdd}
              loading={addExpense.isPending}
              disabled={!form.amount || parseFloat(form.amount) <= 0}
            >
              Dodaj
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
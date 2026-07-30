import { useState } from "react";
import {
  Plus,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  PiggyBank,
  Trash2,
  RefreshCw,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Badge } from "@/components/ui/Badge";
import { Progress } from "@/components/ui/Progress";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { useToast } from "@/components/ui/Toast";
import {
  budgetApi,
  isIncomeEntry,
  type BudgetEntry,
  type BudgetEntryType,
  type MonthlyBudget,
} from "@/lib/api/budget";
import { formatCurrency } from "@/utils/currency";
import { useGroupStore } from "@/stores/groupStore";
import { cn } from "@/utils/cn";

// ── Components ──

function SummaryBar({
  totalIncome,
  totalExpenses,
  savingsGoal,
  onSavingsGoalChange,
}: {
  totalIncome: number;
  totalExpenses: number;
  savingsGoal: number;
  onSavingsGoalChange: (val: number) => void;
}) {
  const remaining = totalIncome - totalExpenses;
  const afterSavings = remaining - savingsGoal;
  const daysInMonth = new Date(
    new Date().getFullYear(),
    new Date().getMonth() + 1,
    0
  ).getDate();
  const today = new Date().getDate();
  const daysLeft = daysInMonth - today + 1;
  const dailyBudget = daysLeft > 0 ? afterSavings / daysLeft : 0;

  const progressPercent =
    totalIncome > 0
      ? Math.min(100, Math.max(0, (totalExpenses / totalIncome) * 100))
      : 0;

  return (
    <Card className="bg-gradient-to-br from-muted/50 to-card">
      <CardContent className="py-4">
        <div className="grid gap-3 mb-4 sm:grid-cols-4">
          <div className="text-center sm:text-left">
            <p className="text-xs text-muted-foreground flex items-center gap-1 justify-center sm:justify-start">
              <ArrowUpRight className="h-3 w-3 text-emerald-500" /> Przychody
            </p>
            <p className="text-lg font-bold text-emerald-600">
              {formatCurrency(totalIncome)}
            </p>
          </div>
          <div className="text-center sm:text-left">
            <p className="text-xs text-muted-foreground flex items-center gap-1 justify-center sm:justify-start">
              <ArrowDownRight className="h-3 w-3 text-red-500" /> Wydatki
            </p>
            <p className="text-lg font-bold text-red-600">
              {formatCurrency(totalExpenses)}
            </p>
          </div>
          <div className="text-center sm:text-left">
            <p className="text-xs text-muted-foreground flex items-center gap-1 justify-center sm:justify-start">
              <Wallet className="h-3 w-3 text-primary" /> Pozostało
            </p>
            <p
              className={cn(
                "text-lg font-bold",
                remaining >= 0 ? "text-primary" : "text-destructive"
              )}
            >
              {formatCurrency(remaining)}
            </p>
          </div>
          <div className="text-center sm:text-left">
            <p className="text-xs text-muted-foreground flex items-center gap-1 justify-center sm:justify-start">
              <PiggyBank className="h-3 w-3 text-amber-500" /> Dzienny budżet
            </p>
            <p
              className={cn(
                "text-lg font-bold",
                dailyBudget >= 0 ? "text-amber-600" : "text-destructive"
              )}
            >
              {formatCurrency(dailyBudget)}
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="flex-1">
              <Progress
                value={totalExpenses}
                max={totalIncome || 1}
                className="h-3"
                indicatorClassName={cn(
                  remaining >= 0 ? "bg-emerald-500" : "bg-red-500"
                )}
              />
            </div>
            <span
              className={cn(
                "text-xs font-semibold",
                remaining >= 0 ? "text-emerald-600" : "text-red-600"
              )}
            >
              {Math.round(progressPercent)}%
            </span>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <label className="text-xs text-muted-foreground whitespace-nowrap">
              Cel oszczędnościowy:
            </label>
            <Input
              type="number"
              value={savingsGoal || ""}
              onChange={(e) =>
                onSavingsGoalChange(e.target.value ? parseFloat(e.target.value) : 0)
              }
              placeholder="0.00"
              className="h-7 text-xs w-32"
            />
            {savingsGoal > 0 && (
              <span className="text-xs text-muted-foreground">
                Po odłożeniu: {formatCurrency(afterSavings)}
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function EntryRow({
  entry,
  onToggleRecurring,
  onDelete,
}: {
  entry: BudgetEntry;
  onToggleRecurring: (id: string, recurring: boolean) => void;
  onDelete: (id: string) => void;
}) {
  const income = isIncomeEntry(entry);

  return (
    <div className="flex items-center justify-between py-2.5 group border-b border-border/50 last:border-0">
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <div
          className={cn(
            "w-2 h-2 rounded-full shrink-0",
            income ? "bg-emerald-500" : "bg-red-500"
          )}
        />
        <span className="text-sm text-foreground truncate">{entry.name}</span>
        {entry.is_recurring && (
          <Badge variant="info" className="text-[10px] px-1.5 py-0">
            <RefreshCw className="h-2.5 w-2.5 mr-0.5" /> cykliczne
          </Badge>
        )}
      </div>
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "text-sm font-semibold",
            income ? "text-emerald-600" : "text-red-600"
          )}
        >
          {formatCurrency(entry.amount, entry.currency)}
        </span>
        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="text-muted-foreground hover:text-primary text-[10px] px-1 h-6"
            onClick={() => onToggleRecurring(entry.id, !entry.is_recurring)}
            title={entry.is_recurring ? "Wyłącz cykliczne" : "Włącz cykliczne"}
          >
            <RefreshCw className={cn("h-3 w-3", entry.is_recurring && "text-primary")} />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-red-400 hover:text-red-600"
            onClick={() => onDelete(entry.id)}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}

// ── Main Component ──

export function BudgetPanel() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const { activeGroup } = useGroupStore();
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [addOpen, setAddOpen] = useState(false);
  const [savingsGoal, setSavingsGoal] = useState(0);
  const [form, setForm] = useState({
    name: "",
    amount: "",
    entry_type: "expense" as BudgetEntryType,
    is_recurring: false,
  });

  const { data: budget, isLoading } = useQuery<MonthlyBudget>({
    queryKey: ["monthly-budget", year, month, activeGroup?.id],
    queryFn: () => budgetApi.getByMonth(year, month, activeGroup!.id),
    enabled: !!activeGroup?.id,
  });

  const addEntry = useMutation({
    mutationFn: (data: {
      name: string;
      amount: number;
      entry_type: BudgetEntryType;
      is_recurring: boolean;
    }) =>
      budgetApi.addEntry(budget!.id, {
        ...data,
        year,
        month,
        currency: "PLN",
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["monthly-budget"] });
      setAddOpen(false);
      setForm({ name: "", amount: "", entry_type: "expense", is_recurring: false });
      toast("success", "Dodano", "Pozycja została dodana do budżetu.");
    },
    onError: () =>
      toast("error", "Błąd", "Nie udało się dodać pozycji."),
  });

  const deleteEntry = useMutation({
    mutationFn: (id: string) => budgetApi.deleteEntry(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["monthly-budget"] });
      toast("success", "Usunięto", "Pozycja została usunięta.");
    },
  });

  const toggleRecurring = useMutation({
    mutationFn: ({ id, is_recurring }: { id: string; is_recurring: boolean }) =>
      budgetApi.updateEntry(id, { is_recurring }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["monthly-budget"] }),
  });

  const entries = budget?.entries ?? [];
  const incomeEntries = entries.filter(isIncomeEntry);
  const expenseEntries = entries.filter((e) => !isIncomeEntry(e));
  const totalIncome = incomeEntries.reduce((s, e) => s + Number(e.amount), 0);
  const totalExpenses = expenseEntries.reduce((s, e) => s + Number(e.amount), 0);

  const handleAdd = () => {
    const amt = parseFloat(form.amount);
    if (!amt || amt <= 0) return;
    addEntry.mutate({
      name: form.name,
      amount: amt,
      entry_type: form.entry_type,
      is_recurring: form.is_recurring,
    });
  };

  const monthNames = [
    "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
    "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień",
  ];

  if (!activeGroup) {
    return (
      <EmptyState
        icon={Wallet}
        title="Wybierz grupę rodzinną"
        description="Aby korzystać z budżetu miesięcznego, wybierz aktywną grupę w menu."
      />
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-12 w-64" />
        <Skeleton className="h-24 rounded-xl" />
        <Skeleton className="h-48 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (month === 1) {
                setMonth(12);
                setYear((y) => y - 1);
              } else {
                setMonth((m) => m - 1);
              }
            }}
          >
            ←
          </Button>
          <h2 className="text-lg font-semibold text-foreground min-w-[160px] text-center">
            {monthNames[month - 1]} {year}
          </h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (month === 12) {
                setMonth(1);
                setYear((y) => y + 1);
              } else {
                setMonth((m) => m + 1);
              }
            }}
          >
            →
          </Button>
        </div>
        <Button size="sm" onClick={() => setAddOpen(true)}>
          <Plus className="h-4 w-4" /> Dodaj pozycję
        </Button>
      </div>

      <SummaryBar
        totalIncome={totalIncome}
        totalExpenses={totalExpenses}
        savingsGoal={savingsGoal}
        onSavingsGoalChange={setSavingsGoal}
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-emerald-500" />
              Przychody
            </CardTitle>
          </CardHeader>
          <CardContent>
            {incomeEntries.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                Brak przychodów w tym miesiącu.
              </p>
            ) : (
              incomeEntries.map((entry) => (
                <EntryRow
                  key={entry.id}
                  entry={entry}
                  onToggleRecurring={(id, rec) =>
                    toggleRecurring.mutate({ id, is_recurring: rec })
                  }
                  onDelete={(id) => deleteEntry.mutate(id)}
                />
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-500" />
              Wydatki
            </CardTitle>
          </CardHeader>
          <CardContent>
            {expenseEntries.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                Brak wydatków w tym miesiącu.
              </p>
            ) : (
              expenseEntries.map((entry) => (
                <EntryRow
                  key={entry.id}
                  entry={entry}
                  onToggleRecurring={(id, rec) =>
                    toggleRecurring.mutate({ id, is_recurring: rec })
                  }
                  onDelete={(id) => deleteEntry.mutate(id)}
                />
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <Modal
        open={addOpen}
        onClose={() => setAddOpen(false)}
        title="Dodaj pozycję budżetową"
      >
        <div className="space-y-4">
          <Input
            label="Nazwa"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="np. Wynagrodzenie, Czynsz"
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Kwota"
              type="number"
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              placeholder="0.00"
            />
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-foreground">Typ</label>
              <select
                className="block w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground"
                value={form.entry_type}
                onChange={(e) =>
                  setForm({ ...form, entry_type: e.target.value as BudgetEntryType })
                }
              >
                <option value="income">Przychód</option>
                <option value="expense">Wydatek</option>
              </select>
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_recurring}
              onChange={(e) =>
                setForm({ ...form, is_recurring: e.target.checked })
              }
              className="rounded border-border text-primary focus:ring-primary"
            />
            <RefreshCw className="h-3.5 w-3.5 text-muted-foreground" />
            Pozycja cykliczna (co miesiąc)
          </label>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setAddOpen(false)}>
              Anuluj
            </Button>
            <Button
              onClick={handleAdd}
              loading={addEntry.isPending}
              disabled={!form.name.trim() || !form.amount || parseFloat(form.amount) <= 0}
            >
              Dodaj
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

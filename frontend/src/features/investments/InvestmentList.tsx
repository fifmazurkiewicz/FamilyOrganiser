import { useState, useMemo } from "react";
import {
  Plus,
  TrendingUp,
  PiggyBank,
  Banknote,
  Calculator,
  Trash2,
  Calendar,
  Percent,
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
import { api } from "@/api/client";
import { useGroupStore } from "@/stores/groupStore";
import { formatCurrency } from "@/utils/currency";
import { cn } from "@/utils/cn";
import { format, addMonths, differenceInDays } from "date-fns";
import { pl } from "date-fns/locale";

// ── Types ──

interface Investment {
  id: string;
  name: string;
  investment_type: string;
  principal_amount: number;
  interest_rate: number;
  interest_period: string;
  duration_value: number;
  duration_unit: string;
  start_date: string;
  end_date: string;
  projected_profit: number;
  projected_total: number;
  created_at: string;
}

const typeLabels: Record<string, string> = {
  deposit: "Lokata",
  bonds: "Obligacje",
  stocks: "Akcje",
  other: "Inne",
};

// ── Helpers ──

function calculateInvestment(
  amount: number,
  rate: number,
  durationMonths: number,
  startDate: string
) {
  const profit = (amount * (rate / 100) * durationMonths) / 12;
  const total = amount + profit;
  const endDate = addMonths(new Date(startDate), durationMonths);
  const daysLeft = differenceInDays(endDate, new Date());
  return {
    projected_profit: Math.round(profit * 100) / 100,
    projected_total: Math.round(total * 100) / 100,
    end_date: endDate.toISOString().slice(0, 10),
    days_left: Math.max(0, daysLeft),
  };
}

// ── Main Component ──

export function InvestmentList() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const { activeGroup } = useGroupStore();
  const [addOpen, setAddOpen] = useState(false);
  const [form, setForm] = useState({
    name: "",
    investment_type: "deposit",
    amount: "",
    rate: "",
    duration_months: "",
    currency: "PLN",
    start_date: new Date().toISOString().slice(0, 10),
  });

  const { data: investments, isLoading } = useQuery<Investment[]>({
    queryKey: ["investments"],
    queryFn: () => api.get("/v1/simple-investments/", { params: { family_group_id: activeGroup?.id } }).then((r) => r.data),
  });

  const createInv = useMutation({
    mutationFn: (data: {
      name: string;
      investment_type: string;
      amount: number;
      currency: string;
      rate: number;
      duration_months: number;
      start_date: string;
    }) => api.post("/v1/simple-investments/", {
        ...data,
        family_group_id: activeGroup?.id,
        interest_period: "yearly",
        duration_unit: "months",
        principal_amount: data.amount,
        interest_rate: data.rate,
        duration_value: data.duration_months,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["investments"] });
      setAddOpen(false);
      setForm({
        name: "",
        investment_type: "deposit",
        amount: "",
        rate: "",
        duration_months: "",
        currency: "PLN",
        start_date: new Date().toISOString().slice(0, 10),
      });
      toast("success", "Dodano", "Inwestycja została dodana.");
    },
    onError: () => toast("error", "Błąd", "Nie udało się dodać inwestycji."),
  });

  const deleteInv = useMutation({
    mutationFn: (id: string) => api.delete(`/v1/simple-investments/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["investments"] });
      toast("success", "Usunięto", "Inwestycja została usunięta.");
    },
  });

  // ── Compute preview ──

  const preview = useMemo(() => {
    const amt = parseFloat(form.amount);
    const rate = parseFloat(form.rate);
    const dur = parseInt(form.duration_months);
    if (!amt || !rate || !dur || amt <= 0 || rate <= 0 || dur <= 0)
      return null;
    return calculateInvestment(amt, rate, dur, form.start_date);
  }, [form.amount, form.rate, form.duration_months, form.start_date]);

  // ── Summary ──

  const totals = useMemo(() => {
    if (!investments) return null;
    const totalInvested = investments.reduce((s, i) => s + i.principal_amount, 0);
    const totalProfit = investments.reduce((s, i) => s + i.projected_profit, 0);
    const totalProjected = investments.reduce((s, i) => s + i.projected_total, 0);
    return { totalInvested, totalProfit, totalProjected };
  }, [investments]);

  const handleAdd = () => {
    const amt = parseFloat(form.amount);
    const rate = parseFloat(form.rate);
    const dur = parseInt(form.duration_months);
    if (!amt || !rate || !dur) return;
    createInv.mutate({
      name: form.name,
      investment_type: form.investment_type,
      amount: amt,
      currency: form.currency,
      rate,
      duration_months: dur,
      start_date: form.start_date,
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-20 rounded-xl" />
        <Skeleton className="h-8 w-32" />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary bar */}
      {totals && (
        <Card className="bg-gradient-to-br from-primary-light/30 to-accent/20">
          <CardContent className="py-4">
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="text-center">
                <p className="text-xs text-gray-500 flex items-center gap-1 justify-center">
                  <Banknote className="h-3.5 w-3.5" /> Zainwestowano
                </p>
                <p className="text-xl font-bold text-gray-900">
                  {formatCurrency(totals.totalInvested)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 flex items-center gap-1 justify-center">
                  <TrendingUp className="h-3.5 w-3.5" /> Projekcja zysku
                </p>
                <p className="text-xl font-bold text-emerald-600">
                  {formatCurrency(totals.totalProfit)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 flex items-center gap-1 justify-center">
                  <PiggyBank className="h-3.5 w-3.5" /> Projekcja łącznie
                </p>
                <p className="text-xl font-bold text-primary">
                  {formatCurrency(totals.totalProjected)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Inwestycje</h2>
        <Button size="sm" onClick={() => setAddOpen(true)}>
          <Plus className="h-4 w-4" /> Dodaj inwestycję
        </Button>
      </div>

      {/* Empty state */}
      {!investments || investments.length === 0 ? (
        <EmptyState
          icon={TrendingUp}
          title="Brak inwestycji"
          description="Dodaj pierwszą inwestycję, aby śledzić swój portfel."
          action={{ label: "Dodaj inwestycję", onClick: () => setAddOpen(true) }}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {investments.map((inv) => {
            const profitPercent = (inv.projected_profit / inv.principal_amount) * 100;
            const now = new Date();
            const endDate = new Date(inv.end_date);
            const isActive = endDate >= now;
            const daysRemaining = differenceInDays(endDate, now);

            return (
              <Card
                key={inv.id}
                className={cn(!isActive && "opacity-70")}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle>{inv.name}</CardTitle>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {typeLabels[inv.investment_type] || inv.investment_type}
                      </p>
                    </div>
                    <Badge variant={isActive ? "success" : "default"}>
                      {isActive
                        ? `Pozostało ${daysRemaining} dni`
                        : "Zakończona"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* Amount */}
                  <div>
                    <p className="text-xs text-gray-500">Kwota</p>
                    <p className="text-lg font-bold text-gray-900">
                      {formatCurrency(inv.principal_amount)}
                    </p>
                  </div>

                  {/* Details row */}
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <Percent className="h-3 w-3" />
                      {inv.interest_rate}%
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {inv.duration_value}{" "}
                      {inv.duration_unit === "years"
                        ? "lat"
                        : inv.duration_unit === "quarters"
                          ? "kw."
                          : "mies."}
                    </div>
                    <div className="flex items-center gap-1 col-span-2">
                      <Calendar className="h-3 w-3" />
                      {format(new Date(inv.end_date), "dd.MM.yyyy", { locale: pl })}
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-400">Zysk</span>
                      <span className="text-emerald-600 font-semibold">
                        +{formatCurrency(inv.projected_profit)} ({profitPercent.toFixed(1)}%)
                      </span>
                    </div>
                    <Progress
                      value={inv.projected_profit}
                      max={inv.principal_amount || 1}
                      className="h-1.5"
                      indicatorClassName="bg-emerald-500"
                    />
                  </div>

                  {/* Projected total */}
                  <p className="text-sm font-semibold text-primary">
                    Projekcja łącznie: {formatCurrency(inv.projected_total)}
                  </p>

                  {/* Delete */}
                  <div className="flex justify-end pt-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-500 hover:bg-red-50"
                      onClick={() => deleteInv.mutate(inv.id)}
                    >
                      <Trash2 className="h-4 w-4" /> Usuń
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Add investment modal */}
      <Modal
        open={addOpen}
        onClose={() => setAddOpen(false)}
        title="Nowa inwestycja"
        className="max-w-lg"
      >
        <div className="space-y-4">
          <Input
            label="Nazwa"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="np. Lokata 6-miesięczna"
          />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">
              Typ inwestycji
            </label>
            <select
              className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm"
              value={form.investment_type}
              onChange={(e) =>
                setForm({ ...form, investment_type: e.target.value })
              }
            >
              {Object.entries(typeLabels).map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Kwota"
              type="number"
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              placeholder="0.00"
            />
            <Input
              label="Waluta"
              value={form.currency}
              onChange={(e) =>
                setForm({ ...form, currency: e.target.value.toUpperCase() })
              }
              maxLength={3}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Oprocentowanie (%)"
              type="number"
              step="0.01"
              value={form.rate}
              onChange={(e) => setForm({ ...form, rate: e.target.value })}
              placeholder="np. 5.0"
            />
            <Input
              label="Okres (miesięcy)"
              type="number"
              value={form.duration_months}
              onChange={(e) =>
                setForm({ ...form, duration_months: e.target.value })
              }
              placeholder="np. 12"
            />
          </div>
          <Input
            label="Data rozpoczęcia"
            type="date"
            value={form.start_date}
            onChange={(e) => setForm({ ...form, start_date: e.target.value })}
          />

          {/* Preview */}
          {preview && (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 space-y-2">
              <p className="text-sm font-semibold text-emerald-800 flex items-center gap-2">
                <Calculator className="h-4 w-4" /> Podgląd kalkulacji
              </p>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-emerald-600/70">Data zakończenia</p>
                  <p className="font-semibold text-emerald-900">
                    {format(new Date(preview.end_date), "dd.MM.yyyy", {
                      locale: pl,
                    })}
                  </p>
                </div>
                <div>
                  <p className="text-emerald-600/70">Pozostało dni</p>
                  <p className="font-semibold text-emerald-900">
                    {preview.days_left}
                  </p>
                </div>
                <div>
                  <p className="text-emerald-600/70">Projekcja zysku</p>
                  <p className="font-semibold text-emerald-900">
                    +{formatCurrency(preview.projected_profit)}
                  </p>
                </div>
                <div>
                  <p className="text-emerald-600/70">Łącznie</p>
                  <p className="font-semibold text-emerald-900">
                    {formatCurrency(preview.projected_total)}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setAddOpen(false)}>
              Anuluj
            </Button>
            <Button
              onClick={handleAdd}
              loading={createInv.isPending}
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
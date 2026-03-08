import { useState } from "react";
import { Plus, PiggyBank } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Progress } from "@/components/ui/Progress";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useSavingsGoals, useCreateGoal, useDeleteGoal, useAddContribution } from "@/hooks/useSavings";
import { formatCurrency } from "@/utils/currency";
import type { SavingsGoal } from "@/types";

function GoalCard({ goal, onContribute, onDelete }: {
  goal: SavingsGoal;
  onContribute: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{goal.icon || "🎯"}</span>
            <div>
              <CardTitle>{goal.name}</CardTitle>
              {goal.target_date && (
                <p className="text-xs text-gray-500 mt-0.5">
                  Do: {new Date(goal.target_date).toLocaleDateString("pl-PL")}
                </p>
              )}
            </div>
          </div>
          <Badge variant={goal.is_completed ? "success" : "default"}>
            {goal.is_completed ? "Ukończony" : "W toku"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-2">
          <div className="flex justify-between text-sm mb-1">
            <span className="font-medium text-gray-900">{formatCurrency(goal.current_amount, goal.currency)}</span>
            <span className="text-gray-400">/ {formatCurrency(goal.target_amount, goal.currency)}</span>
          </div>
          <Progress value={goal.progress_percent} max={100} />
          <p className="text-xs text-gray-400 mt-1">{goal.progress_percent.toFixed(1)}% ukończone</p>
        </div>
        {goal.monthly_contribution && (
          <p className="text-xs text-gray-500">
            Miesięczna wpłata: {formatCurrency(goal.monthly_contribution, goal.currency)}
          </p>
        )}
        <div className="mt-3 flex justify-end gap-2">
          <Button variant="outline" size="sm" onClick={() => onContribute(goal.id)}>
            Wpłać
          </Button>
          <Button variant="ghost" size="sm" className="text-red-500 hover:bg-red-50" onClick={() => onDelete(goal.id)}>
            Usuń
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function ContributeModal({ goalId, onClose }: { goalId: string; onClose: () => void }) {
  const addContrib = useAddContribution(goalId);
  const [form, setForm] = useState({
    amount: "",
    contribution_date: new Date().toISOString().split("T")[0],
    note: "",
    is_withdrawal: false,
  });

  const handle = async () => {
    await addContrib.mutateAsync({ amount: parseFloat(form.amount), contribution_date: form.contribution_date, note: form.note || undefined, is_withdrawal: form.is_withdrawal });
    onClose();
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <label className="flex items-center gap-2 text-sm">
          <input type="radio" checked={!form.is_withdrawal} onChange={() => setForm({ ...form, is_withdrawal: false })} />
          Wpłata
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="radio" checked={form.is_withdrawal} onChange={() => setForm({ ...form, is_withdrawal: true })} />
          Wypłata
        </label>
      </div>
      <Input label="Kwota" type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
      <Input label="Data" type="date" value={form.contribution_date} onChange={(e) => setForm({ ...form, contribution_date: e.target.value })} />
      <Input label="Notatka (opcjonalnie)" value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Anuluj</Button>
        <Button onClick={handle} loading={addContrib.isPending} disabled={!form.amount}>
          {form.is_withdrawal ? "Wypłać" : "Wpłać"}
        </Button>
      </div>
    </div>
  );
}

export function SavingsGoalList() {
  const { data: goals, isLoading } = useSavingsGoals();
  const createGoal = useCreateGoal();
  const deleteGoal = useDeleteGoal();
  const [createOpen, setCreateOpen] = useState(false);
  const [contributeGoalId, setContributeGoalId] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", target_amount: "", currency: "PLN", target_date: "", icon: "" });

  const handleCreate = async () => {
    await createGoal.mutateAsync({
      name: form.name,
      target_amount: parseFloat(form.target_amount),
      currency: form.currency,
      target_date: form.target_date || undefined,
      icon: form.icon || undefined,
    });
    setCreateOpen(false);
  };

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Cele oszczędnościowe</h2>
        <Button size="sm" onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" /> Nowy cel
        </Button>
      </div>

      {!goals || goals.length === 0 ? (
        <EmptyState icon={PiggyBank} title="Brak celów" description="Ustaw cel oszczędnościowy i śledź postęp." action={{ label: "Dodaj cel", onClick: () => setCreateOpen(true) }} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {goals.map((g) => (
            <GoalCard key={g.id} goal={g} onContribute={setContributeGoalId} onDelete={(id) => deleteGoal.mutate(id)} />
          ))}
        </div>
      )}

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="Nowy cel oszczędnościowy">
        <div className="space-y-4">
          <Input label="Nazwa celu" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="np. Wakacje 2026" />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Kwota docelowa" type="number" step="100" value={form.target_amount} onChange={(e) => setForm({ ...form, target_amount: e.target.value })} />
            <Input label="Waluta" value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value.toUpperCase() })} maxLength={3} />
          </div>
          <Input label="Data docelowa (opcjonalnie)" type="date" value={form.target_date} onChange={(e) => setForm({ ...form, target_date: e.target.value })} />
          <Input label="Emoji ikona (opcjonalnie)" value={form.icon} onChange={(e) => setForm({ ...form, icon: e.target.value })} placeholder="np. 🏖️" />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreate} loading={createGoal.isPending} disabled={!form.name || !form.target_amount}>
              Utwórz
            </Button>
          </div>
        </div>
      </Modal>

      <Modal open={!!contributeGoalId} onClose={() => setContributeGoalId(null)} title="Wpłata / wypłata">
        {contributeGoalId && <ContributeModal goalId={contributeGoalId} onClose={() => setContributeGoalId(null)} />}
      </Modal>
    </div>
  );
}

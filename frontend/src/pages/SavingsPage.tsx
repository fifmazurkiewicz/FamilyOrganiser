import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import { Plus, PiggyBank, Target } from "lucide-react";

export default function SavingsPage() {
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();

  const { data: goals = [], isLoading } = useQuery({
    queryKey: ["savings-goals"],
    queryFn: () => api.get("/savings/goals").then((r) => r.data),
  });

  const [form, setForm] = useState({
    name: "",
    description: "",
    target_amount: "",
    currency: "PLN",
    goal_type: "personal",
    visibility: "private",
    target_date: "",
    monthly_contribution: "",
    icon: "🎯",
    color: "#4472C4",
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/savings/goals", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["savings-goals"] });
      setShowForm(false);
      setForm({ name: "", description: "", target_amount: "", currency: "PLN", goal_type: "personal", visibility: "private", target_date: "", monthly_contribution: "", icon: "🎯", color: "#4472C4" });
    },
  });

  const totalSaved = goals.reduce((sum: number, g: any) => sum + parseFloat(g.current_amount || "0"), 0);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Oszczędności i cele</h1>
          <p className="text-gray-500 text-sm">Łącznie odłożono: {formatCurrency(totalSaved)}</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Nowy cel
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Dodaj cel oszczędnościowy</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nazwa</label>
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Wakacje Grecja 2027"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ikona / Emoji</label>
              <input
                value={form.icon}
                onChange={(e) => setForm((f) => ({ ...f, icon: e.target.value }))}
                placeholder="🎯"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Kwota docelowa</label>
              <input
                type="number"
                step="0.01"
                value={form.target_amount}
                onChange={(e) => setForm((f) => ({ ...f, target_amount: e.target.value }))}
                placeholder="5000.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Waluta</label>
              <select
                value={form.currency}
                onChange={(e) => setForm((f) => ({ ...f, currency: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {["PLN", "EUR", "USD", "GBP"].map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Typ celu</label>
              <select
                value={form.goal_type}
                onChange={(e) => setForm((f) => ({ ...f, goal_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="personal">Osobisty</option>
                <option value="family">Rodzinny</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Data realizacji</label>
              <input
                type="date"
                value={form.target_date}
                onChange={(e) => setForm((f) => ({ ...f, target_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Miesięczna wpłata</label>
              <input
                type="number"
                step="0.01"
                value={form.monthly_contribution}
                onChange={(e) => setForm((f) => ({ ...f, monthly_contribution: e.target.value }))}
                placeholder="500.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Widoczność</label>
              <select
                value={form.visibility}
                onChange={(e) => setForm((f) => ({ ...f, visibility: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="private">Prywatny</option>
                <option value="public">Publiczny (widoczny dla rodziny)</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Opis</label>
              <input
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="Krótki opis celu..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={() =>
                createMutation.mutate({
                  ...form,
                  target_amount: parseFloat(form.target_amount || "0"),
                  monthly_contribution: form.monthly_contribution ? parseFloat(form.monthly_contribution) : undefined,
                  target_date: form.target_date || undefined,
                })
              }
              disabled={createMutation.isPending || !form.name || !form.target_amount}
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {createMutation.isPending ? "Zapisywanie..." : "Dodaj cel"}
            </button>
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-100"
            >
              Anuluj
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <p className="text-gray-400">Ładowanie...</p>
      ) : goals.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <PiggyBank className="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p>Brak celów oszczędnościowych. Ustaw pierwszy cel!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {goals.map((goal: any) => {
            const percent = Math.min(100, goal.progress_percent || 0);
            const monthsLeft =
              goal.target_date && goal.monthly_contribution
                ? Math.ceil(
                    (parseFloat(goal.target_amount) - parseFloat(goal.current_amount)) /
                      parseFloat(goal.monthly_contribution)
                  )
                : null;

            return (
              <div
                key={goal.id}
                className="bg-white rounded-xl shadow-sm border border-gray-100 p-5"
                style={{ borderTopColor: goal.color || "#4472C4", borderTopWidth: 4 }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">{goal.icon || "🎯"}</span>
                  <div>
                    <p className="font-semibold text-gray-900">{goal.name}</p>
                    {goal.description && (
                      <p className="text-xs text-gray-400 mt-0.5">{goal.description}</p>
                    )}
                  </div>
                </div>

                <div className="mb-2">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-500">{formatCurrency(goal.current_amount, goal.currency)}</span>
                    <span className="font-medium">{formatCurrency(goal.target_amount, goal.currency)}</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                  <p className="text-right text-xs text-gray-400 mt-0.5">{percent.toFixed(1)}%</p>
                </div>

                {goal.is_completed && (
                  <span className="inline-flex items-center gap-1 bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full">
                    ✓ Cel osiągnięty!
                  </span>
                )}

                {monthsLeft !== null && monthsLeft > 0 && !goal.is_completed && (
                  <p className="text-xs text-gray-400 mt-1">
                    Osiągniesz cel za ~{monthsLeft} mies.
                  </p>
                )}

                {goal.target_date && (
                  <p className="text-xs text-gray-400 mt-1">
                    Termin: {new Date(goal.target_date).toLocaleDateString("pl-PL")}
                  </p>
                )}

                <div className="mt-2">
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      goal.goal_type === "family"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {goal.goal_type === "family" ? "Rodzinny" : "Osobisty"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

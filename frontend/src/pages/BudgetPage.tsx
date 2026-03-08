import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import { Plus, BarChart2 } from "lucide-react";

export default function BudgetPage() {
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();
  const now = new Date();

  const { data: budgets = [], isLoading } = useQuery({
    queryKey: ["budgets"],
    queryFn: () =>
      api.get(`/budgets/?year=${now.getFullYear()}&month=${now.getMonth() + 1}`).then((r) => r.data),
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/transactions/categories").then((r) => r.data),
  });

  const [name, setName] = useState("Budżet miesięczny");
  const [catAmounts, setCatAmounts] = useState<Record<string, string>>({});

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/budgets/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      setShowForm(false);
    },
  });

  const handleCreate = () => {
    const categories_data = Object.entries(catAmounts)
      .filter(([, amount]) => amount && parseFloat(amount) > 0)
      .map(([cat_id, amount]) => ({
        category_id: cat_id,
        planned_amount: parseFloat(amount),
        currency: "PLN",
      }));

    createMutation.mutate({
      name,
      scope: "personal",
      year: now.getFullYear(),
      month: now.getMonth() + 1,
      alert_threshold_percent: 80,
      categories: categories_data,
    });
  };

  const topCategories = categories.filter((c: any) => !c.parent_id);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Budżet</h1>
          <p className="text-gray-500 text-sm">
            {now.toLocaleDateString("pl-PL", { month: "long", year: "numeric" })}
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Nowy budżet
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Utwórz budżet miesięczny</h2>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Nazwa</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div className="space-y-2 mb-4">
            <label className="block text-sm font-medium text-gray-700">Limity per kategoria (PLN)</label>
            {topCategories.map((cat: any) => (
              <div key={cat.id} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-32 flex-shrink-0">
                  {cat.icon} {cat.name}
                </span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  value={catAmounts[cat.id] || ""}
                  onChange={(e) => setCatAmounts((prev) => ({ ...prev, [cat.id]: e.target.value }))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCreate}
              disabled={createMutation.isPending}
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {createMutation.isPending ? "Zapisywanie..." : "Utwórz budżet"}
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
      ) : budgets.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <BarChart2 className="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p>Brak budżetów na ten miesiąc. Utwórz pierwszy budżet!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {budgets.map((budget: any) => (
            <div key={budget.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h2 className="font-semibold text-gray-900 mb-4">{budget.name}</h2>
              <div className="space-y-3">
                {budget.categories.map((bc: any) => {
                  const planned = parseFloat(bc.planned_amount);
                  const actual = parseFloat(bc.actual_amount || "0");
                  const pct = planned > 0 ? Math.min(100, (actual / planned) * 100) : 0;
                  const overBudget = actual > planned;
                  const nearLimit = pct >= budget.alert_threshold_percent;

                  return (
                    <div key={bc.id}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Kategoria</span>
                        <span className={overBudget ? "text-red-600 font-medium" : "text-gray-900"}>
                          {formatCurrency(actual)} / {formatCurrency(planned)}
                        </span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            overBudget ? "bg-red-500" : nearLimit ? "bg-yellow-500" : "bg-green-500"
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      {nearLimit && !overBudget && (
                        <p className="text-xs text-yellow-600 mt-0.5">
                          Zbliżasz się do limitu ({pct.toFixed(0)}%)
                        </p>
                      )}
                      {overBudget && (
                        <p className="text-xs text-red-600 mt-0.5">
                          Przekroczono limit o {formatCurrency(actual - planned)}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

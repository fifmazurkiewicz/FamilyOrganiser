import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import { Plus, DollarSign } from "lucide-react";

const INCOME_CATEGORIES: Record<string, string> = {
  salary: "Wynagrodzenie etatowe",
  bonus: "Premia / nadgodziny",
  freelance: "Freelance / zlecenie",
  rental: "Wynajem nieruchomości",
  dividend: "Dywidenda / zyski",
  sale: "Sprzedaż",
  other: "Inne",
};

export default function IncomePage() {
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();
  const now = new Date();

  const { data: incomes = [], isLoading } = useQuery({
    queryKey: ["incomes"],
    queryFn: () =>
      api.get(`/income/?year=${now.getFullYear()}&month=${now.getMonth() + 1}`).then((r) => r.data),
  });

  const { data: accounts = [] } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => api.get("/accounts/").then((r) => r.data),
  });

  const [form, setForm] = useState({
    account_id: "",
    name: "",
    amount: "",
    currency: "PLN",
    category: "salary",
    income_date: now.toISOString().split("T")[0],
    description: "",
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/income/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["incomes"] });
      qc.invalidateQueries({ queryKey: ["accounts"] });
      setShowForm(false);
    },
  });

  const totalIncome = incomes
    .filter((i: any) => !i.is_skipped)
    .reduce((sum: number, i: any) => sum + parseFloat(i.amount || "0"), 0);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Przychody</h1>
          <p className="text-gray-500 text-sm">
            {now.toLocaleDateString("pl-PL", { month: "long", year: "numeric" })} — razem:{" "}
            {formatCurrency(totalIncome)}
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Dodaj przychód
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Nowy przychód</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nazwa</label>
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Wynagrodzenie marzec"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Kategoria</label>
              <select
                value={form.category}
                onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {Object.entries(INCOME_CATEGORIES).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Kwota</label>
              <input
                type="number"
                step="0.01"
                value={form.amount}
                onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
                placeholder="8000.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Konto</label>
              <select
                value={form.account_id}
                onChange={(e) => setForm((f) => ({ ...f, account_id: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Wybierz konto...</option>
                {accounts.map((acc: any) => (
                  <option key={acc.id} value={acc.id}>{acc.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Data</label>
              <input
                type="date"
                value={form.income_date}
                onChange={(e) => setForm((f) => ({ ...f, income_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Opis</label>
              <input
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="Opcjonalny opis..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={() =>
                createMutation.mutate({
                  ...form,
                  amount: parseFloat(form.amount),
                })
              }
              disabled={createMutation.isPending || !form.name || !form.amount || !form.account_id}
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {createMutation.isPending ? "Zapisywanie..." : "Dodaj"}
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

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {isLoading ? (
          <p className="p-8 text-center text-gray-400">Ładowanie...</p>
        ) : incomes.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <DollarSign className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p>Brak przychodów w tym miesiącu</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Data</th>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Nazwa</th>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Kategoria</th>
                <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">Kwota</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {incomes.map((income: any) => (
                <tr key={income.id} className={`hover:bg-gray-50 ${income.is_skipped ? "opacity-50" : ""}`}>
                  <td className="px-4 py-3 text-sm text-gray-500">{income.income_date}</td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {income.name}
                    {income.is_modified && (
                      <span className="ml-1 text-xs text-orange-500">*zmodyfikowana</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {INCOME_CATEGORIES[income.category] || income.category}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-green-600 text-right">
                    {income.is_skipped ? (
                      <span className="text-gray-400 text-xs">Pominięto</span>
                    ) : (
                      `+${formatCurrency(income.amount, income.currency)}`
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import { Plus, TrendingUp, TrendingDown, Minus } from "lucide-react";

const INVESTMENT_TYPE_LABELS: Record<string, string> = {
  stock: "Akcja",
  etf: "ETF",
  fund: "Fundusz",
  real_estate: "Nieruchomość",
  crypto: "Kryptowaluta",
  polish_bond: "Obligacja skarbowa",
  bank_deposit: "Lokata bankowa",
};

export default function InvestmentsPage() {
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();

  const { data: investments = [], isLoading } = useQuery({
    queryKey: ["investments"],
    queryFn: () => api.get("/investments/").then((r) => r.data),
  });

  const { data: bonds = [] } = useQuery({
    queryKey: ["bonds"],
    queryFn: () => api.get("/investments/bonds").then((r) => r.data),
  });

  const [form, setForm] = useState({
    investment_type: "stock",
    name: "",
    ticker: "",
    quantity: "",
    purchase_price: "",
    current_price: "",
    currency: "PLN",
    purchase_date: "",
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/investments/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["investments"] });
      setShowForm(false);
    },
  });

  const totalValue = investments.reduce(
    (sum: number, inv: any) => sum + parseFloat(inv.total_value || "0"),
    0
  );

  const bondsTotalValue = bonds.reduce(
    (sum: number, b: any) => sum + parseFloat(b.current_value || "0"),
    0
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inwestycje</h1>
          <p className="text-gray-500 text-sm">
            Wartość portfela: {formatCurrency(totalValue + bondsTotalValue)}
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Dodaj inwestycję
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Dodaj inwestycję</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Typ</label>
              <select
                value={form.investment_type}
                onChange={(e) => setForm((f) => ({ ...f, investment_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {Object.entries(INVESTMENT_TYPE_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nazwa</label>
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Apple Inc."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
              <input
                value={form.ticker}
                onChange={(e) => setForm((f) => ({ ...f, ticker: e.target.value }))}
                placeholder="AAPL"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ilość</label>
              <input
                type="number"
                step="0.00001"
                value={form.quantity}
                onChange={(e) => setForm((f) => ({ ...f, quantity: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cena zakupu</label>
              <input
                type="number"
                step="0.0001"
                value={form.purchase_price}
                onChange={(e) => setForm((f) => ({ ...f, purchase_price: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cena bieżąca</label>
              <input
                type="number"
                step="0.0001"
                value={form.current_price}
                onChange={(e) => setForm((f) => ({ ...f, current_price: e.target.value }))}
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Data zakupu</label>
              <input
                type="date"
                value={form.purchase_date}
                onChange={(e) => setForm((f) => ({ ...f, purchase_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={() =>
                createMutation.mutate({
                  ...form,
                  quantity: parseFloat(form.quantity) || undefined,
                  purchase_price: parseFloat(form.purchase_price) || undefined,
                  current_price: parseFloat(form.current_price) || undefined,
                  purchase_date: form.purchase_date || undefined,
                })
              }
              disabled={createMutation.isPending || !form.name}
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {createMutation.isPending ? "Zapisywanie..." : "Dodaj"}
            </button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-100">
              Anuluj
            </button>
          </div>
        </div>
      )}

      {/* Investments table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Portfel inwestycyjny</h2>
        </div>
        {investments.length === 0 ? (
          <p className="p-8 text-center text-gray-400">Brak inwestycji</p>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Nazwa</th>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Typ</th>
                <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">Wartość</th>
                <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">ROI</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {investments.map((inv: any) => (
                <tr key={inv.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {inv.name}
                    {inv.ticker && <span className="ml-1 text-gray-400 text-xs">{inv.ticker}</span>}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {INVESTMENT_TYPE_LABELS[inv.investment_type]}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-right">
                    {inv.total_value ? formatCurrency(inv.total_value, inv.currency) : "-"}
                  </td>
                  <td className="px-4 py-3 text-sm text-right">
                    {inv.roi_percent !== null && inv.roi_percent !== undefined ? (
                      <span
                        className={`flex items-center justify-end gap-1 ${
                          inv.roi_percent >= 0 ? "text-green-600" : "text-red-600"
                        }`}
                      >
                        {inv.roi_percent >= 0 ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                        {inv.roi_percent.toFixed(2)}%
                      </span>
                    ) : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Polish bonds */}
      {bonds.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Polskie Obligacje Skarbowe</h2>
          </div>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Seria</th>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Typ</th>
                <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">Ilość</th>
                <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">Wartość bieżąca</th>
                <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">Zapadalność</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {bonds.map((bond: any) => (
                <tr key={bond.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{bond.series}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{bond.bond_type}</td>
                  <td className="px-4 py-3 text-sm text-right">{bond.quantity}</td>
                  <td className="px-4 py-3 text-sm font-medium text-right">
                    {formatCurrency(bond.current_value)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 text-right">{bond.maturity_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

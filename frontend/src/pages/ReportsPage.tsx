import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { Download } from "lucide-react";

export default function ReportsPage() {
  const { data: trend } = useQuery({
    queryKey: ["monthly-trend-12"],
    queryFn: () => api.get("/reports/monthly-trend?months=12").then((r) => r.data),
  });

  const { data: byCategory } = useQuery({
    queryKey: ["expenses-by-category-all"],
    queryFn: () => api.get("/reports/expenses-by-category").then((r) => r.data),
  });

  const handleExport = async () => {
    const response = await api.get("/reports/export/transactions", { responseType: "blob" });
    const url = URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "transakcje.xlsx";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Raporty i analityki</h1>
          <p className="text-gray-500 text-sm">Szczegółowy przegląd Twoich finansów</p>
        </div>
        <button
          onClick={handleExport}
          className="flex items-center gap-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-50"
        >
          <Download className="h-4 w-4" />
          Eksport do Excel
        </button>
      </div>

      {/* Monthly cashflow bar chart */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Przychody vs Wydatki (12 miesięcy)</h2>
        {trend && trend.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(val: any) => formatCurrency(val)} />
              <Legend />
              <Bar dataKey="income" name="Przychody" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="expenses" name="Wydatki" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-400 text-sm text-center py-10">Brak danych</p>
        )}
      </div>

      {/* Expenses by category table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Wydatki wg kategorii</h2>
        {byCategory && byCategory.length > 0 ? (
          <div className="space-y-2">
            {byCategory.slice(0, 10).map((row: any, i: number) => {
              const maxAmount = Math.max(...byCategory.map((r: any) => parseFloat(r.amount)));
              const width = (parseFloat(row.amount) / maxAmount) * 100;
              return (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 w-36 flex-shrink-0 truncate">
                    {row.category}
                  </span>
                  <div className="flex-1 h-6 bg-gray-100 rounded overflow-hidden">
                    <div
                      className="h-full bg-blue-400 rounded"
                      style={{ width: `${width}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-28 text-right flex-shrink-0">
                    {formatCurrency(row.amount)}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-gray-400 text-sm text-center py-6">Brak wydatków</p>
        )}
      </div>
    </div>
  );
}

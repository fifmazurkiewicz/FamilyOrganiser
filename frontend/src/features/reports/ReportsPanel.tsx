import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { reportsApi } from "@/lib/api/reports";
import { formatCurrency } from "@/utils/currency";
import { CHART_COLORS } from "@/utils/colors";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  PieChart, Pie,
} from "recharts";

export function ReportsPanel() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  const { data: categories, isLoading: catsLoading } = useQuery({
    queryKey: ["expenses-by-category", year, month],
    queryFn: () => reportsApi.expensesByCategory(year, month),
  });

  const { data: trend, isLoading: trendLoading } = useQuery({
    queryKey: ["monthly-trend", 12],
    queryFn: () => reportsApi.monthlyTrend(12),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-gray-900">Raporty finansowe</h2>
        <div className="flex items-center gap-2">
          <select
            className="rounded-lg border border-gray-300 px-2 py-1 text-sm"
            value={month}
            onChange={(e) => setMonth(parseInt(e.target.value))}
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>{m.toString().padStart(2, "0")}</option>
            ))}
          </select>
          <input
            type="number"
            className="w-20 rounded-lg border border-gray-300 px-2 py-1 text-sm"
            value={year}
            onChange={(e) => setYear(parseInt(e.target.value))}
          />
        </div>
      </div>
      <p className="text-sm text-gray-500">
        Dane z budżetów miesięcznych Twoich grup. Eksport Excel jest dostępny w module Budżet miesięczny.
      </p>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Wydatki wg kategorii</CardTitle></CardHeader>
          <CardContent>
            {catsLoading ? <Spinner /> : !categories || categories.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-8">Brak danych</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={categories}
                    dataKey="amount"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {categories.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => formatCurrency(v)} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Trend miesięczny (12 mies.)</CardTitle></CardHeader>
          <CardContent>
            {trendLoading ? <Spinner /> : !trend || trend.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-8">Brak danych</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={trend}>
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: number) => formatCurrency(v)} />
                  <Bar dataKey="income" name="Przychody" fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
                  <Bar dataKey="expenses" name="Wydatki" fill={CHART_COLORS[1]} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

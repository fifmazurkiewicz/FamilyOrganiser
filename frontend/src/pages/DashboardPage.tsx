import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from "recharts";
import { TrendingUp, TrendingDown, Wallet, PiggyBank } from "lucide-react";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A28FD0", "#FF6B6B", "#4ECDC4", "#B0C4DE"];

export default function DashboardPage() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.get("/reports/dashboard").then((r) => r.data),
  });

  const { data: trend } = useQuery({
    queryKey: ["monthly-trend"],
    queryFn: () => api.get("/reports/monthly-trend?months=6").then((r) => r.data),
  });

  const { data: byCategory } = useQuery({
    queryKey: ["expenses-by-category"],
    queryFn: () => api.get("/reports/expenses-by-category").then((r) => r.data),
  });

  if (isLoading) {
    return <div className="p-8 text-center text-gray-400">Ładowanie...</div>;
  }

  const stats = [
    {
      label: "Łączne saldo",
      value: dashboard?.total_balance || "0",
      icon: Wallet,
      color: "bg-blue-500",
    },
    {
      label: "Wydatki (mies.)",
      value: dashboard?.month_expenses || "0",
      icon: TrendingDown,
      color: "bg-red-500",
    },
    {
      label: "Przychody (mies.)",
      value: dashboard?.month_income || "0",
      icon: TrendingUp,
      color: "bg-green-500",
    },
    {
      label: "Oszczędności",
      value: dashboard?.total_savings || "0",
      icon: PiggyBank,
      color: "bg-purple-500",
    },
  ];

  const cashflow = parseFloat(dashboard?.cashflow || "0");

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm">Przegląd Twoich finansów</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-500">{stat.label}</span>
              <div className={`${stat.color} rounded-lg p-2`}>
                <stat.icon className="h-4 w-4 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(stat.value)}
            </p>
          </div>
        ))}
      </div>

      {/* Cashflow badge */}
      <div
        className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
          cashflow >= 0 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
        }`}
      >
        {cashflow >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
        Cashflow w tym miesiącu: {formatCurrency(cashflow)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly trend chart */}
        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Trendy (ostatnie 6 miesięcy)</h2>
          {trend && trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(val: any) => formatCurrency(val)} />
                <Area
                  type="monotone"
                  dataKey="income"
                  name="Przychody"
                  stroke="#22c55e"
                  fill="#dcfce7"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="expenses"
                  name="Wydatki"
                  stroke="#ef4444"
                  fill="#fee2e2"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm text-center py-10">Brak danych</p>
          )}
        </div>

        {/* Expenses by category */}
        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Wydatki wg kategorii</h2>
          {byCategory && byCategory.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={byCategory.map((d: any) => ({ name: d.category, value: parseFloat(d.amount) }))}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {byCategory.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(val: any) => formatCurrency(val)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm text-center py-10">Brak wydatków w tym miesiącu</p>
          )}
        </div>
      </div>
    </div>
  );
}

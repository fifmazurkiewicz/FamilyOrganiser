import { TrendingUp, TrendingDown, Wallet, PiggyBank } from "lucide-react";
import { format } from "date-fns";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { useDashboard, useMonthlyTrend } from "@/hooks/useDashboard";
import { formatCurrency } from "@/utils/currency";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";

function StatCard({
  title, value, icon: Icon, color,
}: {
  title: string;
  value: string;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 py-5">
        <div className={`rounded-full p-3 ${color}`}>
          <Icon className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-xl font-bold text-gray-900">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function DashboardSummary() {
  const { data: dash, isLoading } = useDashboard();
  const { data: trend } = useMonthlyTrend(6);

  if (isLoading) return <Spinner />;
  if (!dash) return null;

  const netWorth = dash.net_worth ?? 0;
  const monthlyIncome = dash.monthly_income ?? 0;
  const monthlyExpenses = dash.monthly_expenses ?? 0;
  const savingsRate = dash.savings_rate ?? 0;
  const topExpenses = dash.top_expenses ?? [];
  const recentTransactions = dash.recent_transactions ?? [];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Majątek netto" value={formatCurrency(netWorth)} icon={Wallet} color="bg-primary" />
        <StatCard title="Przychody (mies.)" value={formatCurrency(monthlyIncome)} icon={TrendingUp} color="bg-success" />
        <StatCard title="Wydatki (mies.)" value={formatCurrency(monthlyExpenses)} icon={TrendingDown} color="bg-destructive" />
        <StatCard title="Stopa oszczędności" value={`${Number(savingsRate).toFixed(1)}%`} icon={PiggyBank} color="bg-warning" />
      </div>

      {trend && trend.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Trend przychodów i wydatków</CardTitle>
          </CardHeader>
          <CardContent className="pt-2">
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="income" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="expenses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--chart-2))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--chart-2))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v: number) => formatCurrency(v)} />
                <Area type="monotone" dataKey="income" stroke="hsl(var(--chart-1))" fill="url(#income)" name="Przychody" />
                <Area type="monotone" dataKey="expenses" stroke="hsl(var(--chart-2))" fill="url(#expenses)" name="Wydatki" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top wydatki wg kategorii</CardTitle>
          </CardHeader>
          <CardContent>
            {topExpenses.length === 0 ? (
              <p className="text-sm text-gray-500">Brak danych</p>
            ) : (
              <ul className="space-y-2">
                {topExpenses.map((e) => (
                  <li key={e.category} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{e.category}</span>
                    <span className="font-medium">{formatCurrency(e.amount)}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Ostatnie transakcje</CardTitle>
          </CardHeader>
          <CardContent>
            {recentTransactions.length === 0 ? (
              <p className="text-sm text-gray-500">Brak transakcji</p>
            ) : (
              <ul className="divide-y divide-gray-50">
                {recentTransactions.slice(0, 5).map((t) => (
                  <li key={t.id} className="flex items-center justify-between gap-3 py-2 text-sm">
                    <div className="min-w-0 flex-1">
                      <p className="text-gray-700 truncate">{t.description || t.merchant || "Transakcja"}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {t.transaction_date ? format(new Date(t.transaction_date), "dd.MM.yyyy") : ""}
                      </p>
                    </div>
                    <span className={`shrink-0 font-medium ${t.transaction_type === "expense" ? "text-destructive" : "text-success"}`}>
                      {t.transaction_type === "expense" ? "-" : "+"}{formatCurrency(t.amount)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

import { TrendingUp, TrendingDown, Wallet, PiggyBank } from "lucide-react";
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

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Majątek netto" value={formatCurrency(dash.net_worth)} icon={Wallet} color="bg-primary" />
        <StatCard title="Przychody (mies.)" value={formatCurrency(dash.monthly_income)} icon={TrendingUp} color="bg-emerald-500" />
        <StatCard title="Wydatki (mies.)" value={formatCurrency(dash.monthly_expenses)} icon={TrendingDown} color="bg-rose-500" />
        <StatCard title="Stopa oszczędności" value={`${dash.savings_rate.toFixed(1)}%`} icon={PiggyBank} color="bg-amber-500" />
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
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="expenses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v: number) => formatCurrency(v)} />
                <Area type="monotone" dataKey="income" stroke="#10b981" fill="url(#income)" name="Przychody" />
                <Area type="monotone" dataKey="expenses" stroke="#f43f5e" fill="url(#expenses)" name="Wydatki" />
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
            {dash.top_expenses.length === 0 ? (
              <p className="text-sm text-gray-500">Brak danych</p>
            ) : (
              <ul className="space-y-2">
                {dash.top_expenses.map((e) => (
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
            {dash.recent_transactions.length === 0 ? (
              <p className="text-sm text-gray-500">Brak transakcji</p>
            ) : (
              <ul className="divide-y divide-gray-50">
                {dash.recent_transactions.slice(0, 5).map((t) => (
                  <li key={t.id} className="flex items-center justify-between py-2 text-sm">
                    <span className="text-gray-700 truncate max-w-[60%]">
                      {t.description || t.merchant || "Transakcja"}
                    </span>
                    <span className={t.transaction_type === "expense" ? "text-red-600 font-medium" : "text-emerald-600 font-medium"}>
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

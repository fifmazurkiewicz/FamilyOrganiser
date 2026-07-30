import { TrendingUp, TrendingDown, Wallet, PiggyBank, ArrowUp, ArrowDown, Receipt } from "lucide-react";
import { format } from "date-fns";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { Skeleton } from "@/components/ui/Skeleton";
import { useDashboard, useMonthlyTrend } from "@/hooks/useDashboard";
import { formatCurrency } from "@/utils/currency";
import { cn } from "@/utils/cn";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";

function StatCard({
  title, value, subtitle, icon: Icon, trend, trendUp,
}: {
  title: string;
  value: string;
  subtitle?: string;
  icon: React.ElementType;
  trend?: string;
  trendUp?: boolean;
}) {
  return (
    <Card className="group hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 hover:-translate-y-0.5">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-1.5">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold text-foreground tracking-tight">{value}</p>
            {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
            {trend && (
              <div className={cn("flex items-center gap-1 text-xs font-medium", trendUp ? "text-success" : "text-destructive")}>
                {trendUp ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                {trend}
              </div>
            )}
          </div>
          <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300">
            <Icon className="h-5 w-5 text-primary group-hover:text-white transition-colors" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function DashboardSummary() {
  const { data: dash, isLoading } = useDashboard();
  const { data: trend } = useMonthlyTrend(6);

  if (isLoading) return <DashboardSkeleton />;
  if (!dash) {
    return (
      <div className="rounded-xl border border-dashed border-border bg-muted/50 p-8 text-center text-sm text-muted-foreground">
        Nie udało się załadować danych dashboardu. Odśwież stronę lub sprawdź połączenie z API.
      </div>
    );
  }

  const netWorth = dash.net_worth ?? dash.total_balance ?? 0;
  const monthlyIncome = dash.monthly_income ?? dash.month_income ?? 0;
  const monthlyExpenses = dash.monthly_expenses ?? dash.month_expenses ?? 0;
  const savingsRate = dash.savings_rate ?? 0;
  const topExpenses = dash.top_expenses ?? [];
  const recentTransactions = dash.recent_transactions ?? [];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-3 duration-500">
      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Majątek netto"
          value={formatCurrency(netWorth)}
          icon={Wallet}
        />
        <StatCard
          title="Przychody (mies.)"
          value={formatCurrency(monthlyIncome)}
          subtitle="Ten miesiąc"
          icon={TrendingUp}
          trend={monthlyIncome > 0 ? `${formatCurrency(monthlyIncome)}` : undefined}
          trendUp
        />
        <StatCard
          title="Wydatki (mies.)"
          value={formatCurrency(monthlyExpenses)}
          subtitle="Ten miesiąc"
          icon={TrendingDown}
          trend={monthlyExpenses > 0 ? `${formatCurrency(monthlyExpenses)}` : undefined}
        />
        <StatCard
          title="Stopa oszczędności"
          value={`${Number(savingsRate).toFixed(1)}%`}
          subtitle={Number(savingsRate) > 20 ? "Świetny wynik!" : "Do poprawy"}
          icon={PiggyBank}
          trend={Number(savingsRate) > 0 ? "oszczędzasz" : undefined}
          trendUp={Number(savingsRate) > 0}
        />
      </div>

      {/* Trend chart */}
      {trend && trend.length > 0 && (
        <Card className="overflow-hidden">
          <CardHeader className="pb-3">
            <CardTitle>Trend przychodów i wydatków</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">Ostatnie {trend.length} miesięcy</p>
          </CardHeader>
          <CardContent className="pt-0">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="income" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="expenses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--chart-2))" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="hsl(var(--chart-2))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" strokeOpacity={0.4} />
                <XAxis dataKey="month" tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
                <Tooltip
                  formatter={(v: number) => [formatCurrency(v), ""]}
                  contentStyle={{
                    borderRadius: "12px",
                    border: "1px solid hsl(var(--border))",
                    boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
                  }}
                />
                <Area type="monotone" dataKey="income" stroke="hsl(var(--chart-1))" strokeWidth={2} fill="url(#income)" name="Przychody" />
                <Area type="monotone" dataKey="expenses" stroke="hsl(var(--chart-2))" strokeWidth={2} fill="url(#expenses)" name="Wydatki" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Bottom cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Top expenses */}
        <Card>
          <CardHeader>
            <CardTitle>Top wydatki wg kategorii</CardTitle>
          </CardHeader>
          <CardContent>
            {topExpenses.length === 0 ? (
              <div className="py-8 text-center">
                <Receipt className="h-8 w-8 text-muted-foreground/40 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Brak danych o wydatkach</p>
              </div>
            ) : (
              <div className="space-y-3">
                {topExpenses.map((e: { category: string; amount: number; percent?: number }, i: number) => (
                  <div key={e.category} className="flex items-center justify-between gap-3 group">
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <span className="text-xs font-semibold text-muted-foreground w-5">{i + 1}.</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{e.category}</p>
                        <div className="mt-1 h-1.5 w-full rounded-full bg-muted overflow-hidden">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-primary to-emerald-400 transition-all duration-500"
                            style={{ width: `${e.percent ?? Math.min(100, (e.amount / (topExpenses[0]?.amount || 1)) * 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-foreground shrink-0">{formatCurrency(e.amount)}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Ostatnie transakcje</CardTitle>
          </CardHeader>
          <CardContent>
            {recentTransactions.length === 0 ? (
              <div className="py-8 text-center">
                <Receipt className="h-8 w-8 text-muted-foreground/40 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Brak transakcji</p>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {recentTransactions.slice(0, 5).map((t: { id: string; description?: string; merchant?: string; transaction_date?: string; transaction_type: string; amount: number }) => (
                  <div key={t.id} className="flex items-center justify-between gap-3 py-2.5 group hover:bg-muted/50 -mx-2 px-2 rounded-lg transition-colors">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-foreground truncate">{t.description || t.merchant || "Transakcja"}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {t.transaction_date ? format(new Date(t.transaction_date), "dd.MM.yyyy") : ""}
                      </p>
                    </div>
                    <span className={cn(
                      "shrink-0 text-sm font-semibold",
                      t.transaction_type === "expense" ? "text-destructive" : "text-success"
                    )}>
                      {t.transaction_type === "expense" ? "−" : "+"}{formatCurrency(t.amount)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="p-5 space-y-3">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-32" />
              <Skeleton className="h-3 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[260px] w-full rounded-lg" />
        </CardContent>
      </Card>
    </div>
  );
}
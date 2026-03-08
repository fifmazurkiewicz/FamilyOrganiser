import { useState } from "react";
import { Plus, TrendingUp } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { investmentsApi } from "@/lib/api/investments";
import { formatCurrency } from "@/utils/currency";
import type { InvestmentType } from "@/types";

const typeLabels: Record<InvestmentType, string> = {
  stock: "Akcja",
  etf: "ETF",
  fund: "Fundusz",
  real_estate: "Nieruchomość",
  crypto: "Kryptowaluta",
  polish_bond: "Obligacja PL",
  bank_deposit: "Lokata",
};

export function InvestmentList() {
  const qc = useQueryClient();
  const { data: investments, isLoading } = useQuery({
    queryKey: ["investments"],
    queryFn: investmentsApi.list,
  });
  const createInv = useMutation({
    mutationFn: investmentsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["investments"] }),
  });
  const deleteInv = useMutation({
    mutationFn: investmentsApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["investments"] }),
  });

  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    name: "",
    investment_type: "stock" as InvestmentType,
    ticker: "",
    quantity: "",
    purchase_price: "",
    current_price: "",
    currency: "PLN",
    purchase_date: "",
  });

  const handleCreate = async () => {
    await createInv.mutateAsync({
      name: form.name,
      investment_type: form.investment_type,
      ticker: form.ticker || undefined,
      quantity: form.quantity ? parseFloat(form.quantity) : undefined,
      purchase_price: form.purchase_price ? parseFloat(form.purchase_price) : undefined,
      current_price: form.current_price ? parseFloat(form.current_price) : undefined,
      currency: form.currency,
      purchase_date: form.purchase_date || undefined,
    });
    setOpen(false);
  };

  if (isLoading) return <Spinner />;

  const totalValue = investments?.reduce((s, i) => s + (i.total_value ?? 0), 0) ?? 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Inwestycje</h2>
          {totalValue > 0 && (
            <p className="text-sm text-gray-500">Łączna wartość: <strong>{formatCurrency(totalValue)}</strong></p>
          )}
        </div>
        <Button size="sm" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> Dodaj
        </Button>
      </div>

      {!investments || investments.length === 0 ? (
        <EmptyState icon={TrendingUp} title="Brak inwestycji" description="Dodaj inwestycje, aby śledzić portfel." action={{ label: "Dodaj inwestycję", onClick: () => setOpen(true) }} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {investments.map((inv) => (
            <Card key={inv.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle>{inv.name}</CardTitle>
                    {inv.ticker && <p className="text-xs text-gray-400 mt-0.5">{inv.ticker}</p>}
                  </div>
                  <Badge variant="info">{typeLabels[inv.investment_type]}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                {inv.total_value != null && (
                  <p className="text-xl font-bold text-gray-900">{formatCurrency(inv.total_value, inv.currency)}</p>
                )}
                {inv.roi_percent != null && (
                  <p className={`text-sm font-medium ${inv.roi_percent >= 0 ? "text-emerald-600" : "text-red-600"}`}>
                    {inv.roi_percent >= 0 ? "+" : ""}{inv.roi_percent.toFixed(2)}% ROI
                  </p>
                )}
                {inv.quantity && inv.current_price && (
                  <p className="text-xs text-gray-500 mt-1">
                    {inv.quantity} szt. × {formatCurrency(inv.current_price, inv.currency)}
                  </p>
                )}
                <div className="mt-3 flex justify-end">
                  <Button variant="ghost" size="sm" className="text-red-500 hover:bg-red-50" onClick={() => deleteInv.mutate(inv.id)}>
                    Usuń
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="Nowa inwestycja">
        <div className="space-y-4">
          <Input label="Nazwa" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="np. Apple Inc." />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Typ inwestycji</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={form.investment_type} onChange={(e) => setForm({ ...form, investment_type: e.target.value as InvestmentType })}>
              {Object.entries(typeLabels).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Ticker" value={form.ticker} onChange={(e) => setForm({ ...form, ticker: e.target.value })} placeholder="AAPL" />
            <Input label="Waluta" value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value.toUpperCase() })} maxLength={3} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Liczba sztuk" type="number" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
            <Input label="Data zakupu" type="date" value={form.purchase_date} onChange={(e) => setForm({ ...form, purchase_date: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Cena zakupu" type="number" value={form.purchase_price} onChange={(e) => setForm({ ...form, purchase_price: e.target.value })} />
            <Input label="Cena bieżąca" type="number" value={form.current_price} onChange={(e) => setForm({ ...form, current_price: e.target.value })} />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreate} loading={createInv.isPending} disabled={!form.name}>Dodaj</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

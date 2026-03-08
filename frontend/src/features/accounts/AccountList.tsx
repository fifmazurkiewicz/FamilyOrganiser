import { useState } from "react";
import { Plus, CreditCard } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAccounts, useCreateAccount, useDeactivateAccount } from "@/hooks/useAccounts";
import { formatCurrency } from "@/utils/currency";
// Typy kont zgodne z backendem (app.models.account.AccountType)
type BackendAccountType =
  | "bank_individual"
  | "bank_joint"
  | "prepaid_ewallet"
  | "cash"
  | "credit_card"
  | "savings"
  | "crypto_exchange";

const accountTypeLabels: Record<BackendAccountType, string> = {
  bank_individual: "Konto bieżące",
  bank_joint: "Konto wspólne",
  prepaid_ewallet: "Portfel przedpłacony",
  cash: "Gotówka",
  credit_card: "Karta kredytowa",
  savings: "Konto oszczędnościowe",
  crypto_exchange: "Giełda kryptowalut",
};

function AccountCard({ account, onDeactivate }: { account: import("@/types").Account; onDeactivate: (id: string) => void }) {
  const isNegative = account.balance < 0;
  return (
    <Card className="flex flex-col gap-2">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{account.name}</CardTitle>
            <p className="text-xs text-gray-500 mt-0.5">{accountTypeLabels[account.account_type as BackendAccountType] ?? account.account_type}</p>
          </div>
          {account.bank_name && (
            <Badge variant="default">{account.bank_name}</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <p className={`text-2xl font-bold ${isNegative ? "text-red-600" : "text-gray-900"}`}>
          {formatCurrency(account.balance, account.currency)}
        </p>
        {account.credit_limit && (
          <p className="text-xs text-gray-500 mt-1">
            Limit: {formatCurrency(account.credit_limit, account.currency)}
          </p>
        )}
        <div className="mt-3 flex justify-end">
          <Button
            variant="ghost"
            size="sm"
            className="text-red-500 hover:text-red-700 hover:bg-red-50"
            onClick={() => onDeactivate(account.id)}
          >
            Dezaktywuj
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function AccountList() {
  const { data: accounts, isLoading } = useAccounts();
  const createAccount = useCreateAccount();
  const deactivateAccount = useDeactivateAccount();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", account_type: "bank_individual" as BackendAccountType, currency: "PLN", balance: "0" });

  const handleCreate = async () => {
    await createAccount.mutateAsync({
      name: form.name,
      account_type: form.account_type,
      currency: form.currency,
      initial_balance: parseFloat(form.balance) || 0,
    });
    setOpen(false);
    setForm({ name: "", account_type: "bank_individual", currency: "PLN", balance: "0" });
  };

  if (isLoading) return <Spinner />;

  const active = accounts?.filter((a) => a.is_active) ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Konta ({active.length})</h2>
        <Button size="sm" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> Dodaj konto
        </Button>
      </div>

      {active.length === 0 ? (
        <EmptyState icon={CreditCard} title="Brak kont" description="Dodaj pierwsze konto, aby śledzić finanse." action={{ label: "Dodaj konto", onClick: () => setOpen(true) }} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {active.map((a) => (
            <AccountCard key={a.id} account={a} onDeactivate={(id) => deactivateAccount.mutate(id)} />
          ))}
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="Nowe konto">
        <div className="space-y-4">
          <Input label="Nazwa konta" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="np. Konto PKO" />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Typ konta</label>
            <select
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              value={form.account_type}
              onChange={(e) => setForm({ ...form, account_type: e.target.value as BackendAccountType })}
            >
              {Object.entries(accountTypeLabels).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Waluta" value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value.toUpperCase() })} maxLength={3} />
            <Input label="Saldo początkowe" type="number" value={form.balance} onChange={(e) => setForm({ ...form, balance: e.target.value })} />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreate} loading={createAccount.isPending} disabled={!form.name}>
              Utwórz konto
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

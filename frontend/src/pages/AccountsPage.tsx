import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import { Plus, CreditCard, Wallet, Banknote, TrendingDown } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  bank_individual: "Konto bankowe (indywidualne)",
  bank_joint: "Konto bankowe (wspólne)",
  prepaid_ewallet: "Karta prepaid / e-portfel",
  cash: "Gotówka",
  credit_card: "Karta kredytowa",
  savings: "Konto oszczędnościowe",
  crypto_exchange: "Kryptogiełda",
};

const ACCOUNT_TYPE_ICONS: Record<string, React.ElementType> = {
  bank_individual: CreditCard,
  bank_joint: CreditCard,
  prepaid_ewallet: Wallet,
  cash: Banknote,
  credit_card: CreditCard,
  savings: Wallet,
  crypto_exchange: TrendingDown,
};

const schema = z.object({
  name: z.string().min(1, "Nazwa jest wymagana"),
  account_type: z.string(),
  currency: z.string().default("PLN"),
  initial_balance: z.string().default("0"),
  color: z.string().optional(),
  is_joint: z.boolean().default(false),
  is_visible_to_family: z.boolean().default(false),
});

type FormData = z.infer<typeof schema>;

export default function AccountsPage() {
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();

  const { data: accounts = [], isLoading } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => api.get("/accounts/").then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/accounts/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      setShowForm(false);
      reset();
    },
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { currency: "PLN", initial_balance: "0", is_joint: false, is_visible_to_family: false },
  });

  const onSubmit = (data: FormData) => {
    createMutation.mutate({
      ...data,
      initial_balance: parseFloat(data.initial_balance || "0"),
    });
  };

  const totalBalance = accounts.reduce(
    (sum: number, acc: any) => sum + parseFloat(acc.current_balance || "0"),
    0
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Konta</h1>
          <p className="text-gray-500 text-sm">Łączne saldo: {formatCurrency(totalBalance)}</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Nowe konto
        </button>
      </div>

      {/* Add account form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Dodaj nowe konto</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nazwa</label>
              <input
                {...register("name")}
                placeholder="mBank konto osobiste"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Typ konta</label>
              <select
                {...register("account_type")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {Object.entries(ACCOUNT_TYPE_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Waluta</label>
              <select
                {...register("currency")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {["PLN", "EUR", "USD", "GBP", "JPY"].map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Saldo początkowe</label>
              <input
                {...register("initial_balance")}
                type="number"
                step="0.01"
                placeholder="0.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div className="flex items-center gap-2">
              <input {...register("is_joint")} type="checkbox" id="is_joint" className="h-4 w-4" />
              <label htmlFor="is_joint" className="text-sm text-gray-700">Konto wspólne</label>
            </div>

            <div className="flex items-center gap-2">
              <input {...register("is_visible_to_family")} type="checkbox" id="visible" className="h-4 w-4" />
              <label htmlFor="visible" className="text-sm text-gray-700">Widoczne dla rodziny</label>
            </div>

            <div className="md:col-span-2 flex gap-2">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
              >
                {createMutation.isPending ? "Zapisywanie..." : "Dodaj konto"}
              </button>
              <button
                type="button"
                onClick={() => { setShowForm(false); reset(); }}
                className="px-4 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-100"
              >
                Anuluj
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Account list */}
      {isLoading ? (
        <p className="text-gray-400">Ładowanie...</p>
      ) : accounts.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <CreditCard className="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p>Brak kont. Dodaj pierwsze konto finansowe.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {accounts.map((account: any) => {
            const Icon = ACCOUNT_TYPE_ICONS[account.account_type] || CreditCard;
            const isNegative = parseFloat(account.current_balance) < 0;
            return (
              <div
                key={account.id}
                className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow"
                style={{ borderLeftColor: account.color || "#3b82f6", borderLeftWidth: 4 }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <Icon className="h-5 w-5 text-gray-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-900 truncate">{account.name}</p>
                    <p className="text-xs text-gray-400">{ACCOUNT_TYPE_LABELS[account.account_type]}</p>
                  </div>
                  {account.is_joint && (
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                      Wspólne
                    </span>
                  )}
                </div>
                <p className={`text-2xl font-bold ${isNegative ? "text-red-600" : "text-gray-900"}`}>
                  {formatCurrency(account.current_balance, account.currency)}
                </p>
                <p className="text-xs text-gray-400 mt-1">{account.currency}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

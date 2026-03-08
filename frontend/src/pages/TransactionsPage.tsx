import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { formatCurrency } from "@/utils/currency";
import { Plus, ArrowUpCircle, ArrowDownCircle, Filter, Download } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  account_id: z.string().min(1, "Wybierz konto"),
  category_id: z.string().optional(),
  transaction_type: z.enum(["expense", "income"]),
  amount: z.string().min(1),
  currency: z.string().default("PLN"),
  transaction_date: z.string(),
  description: z.string().optional(),
  scope: z.enum(["personal", "family", "shared"]).default("personal"),
});

type FormData = z.infer<typeof schema>;

export default function TransactionsPage() {
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();

  const { data: transactions = [], isLoading } = useQuery({
    queryKey: ["transactions"],
    queryFn: () => api.get("/transactions/?limit=100").then((r) => r.data),
  });

  const { data: accounts = [] } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => api.get("/accounts/").then((r) => r.data),
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/transactions/categories").then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/transactions/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["accounts"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      setShowForm(false);
      reset();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/transactions/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["accounts"] });
    },
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      transaction_type: "expense",
      currency: "PLN",
      scope: "personal",
      transaction_date: new Date().toISOString().split("T")[0],
    },
  });

  const onSubmit = (data: FormData) => {
    createMutation.mutate({
      ...data,
      amount: parseFloat(data.amount),
      category_id: data.category_id || undefined,
    });
  };

  const handleExport = async () => {
    const response = await api.get("/reports/export/transactions", { responseType: "blob" });
    const url = URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "transakcje.xlsx";
    a.click();
    URL.revokeObjectURL(url);
  };

  const topCategories = categories.filter((c: any) => !c.parent_id);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Transakcje</h1>
          <p className="text-gray-500 text-sm">{transactions.length} transakcji</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleExport}
            className="flex items-center gap-2 border border-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm hover:bg-gray-50"
          >
            <Download className="h-4 w-4" />
            Eksport
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90"
          >
            <Plus className="h-4 w-4" />
            Nowa transakcja
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-semibold text-gray-900 mb-4">Dodaj transakcję</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Typ</label>
              <select
                {...register("transaction_type")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="expense">Wydatek</option>
                <option value="income">Przychód</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Konto</label>
              <select
                {...register("account_id")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Wybierz konto...</option>
                {accounts.map((acc: any) => (
                  <option key={acc.id} value={acc.id}>{acc.name}</option>
                ))}
              </select>
              {errors.account_id && <p className="text-red-500 text-xs mt-1">{errors.account_id.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Kwota</label>
              <input
                {...register("amount")}
                type="number"
                step="0.01"
                min="0.01"
                placeholder="0.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Kategoria</label>
              <select
                {...register("category_id")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Brak kategorii</option>
                {topCategories.map((cat: any) => (
                  <option key={cat.id} value={cat.id}>{cat.icon} {cat.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Data</label>
              <input
                {...register("transaction_date")}
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Zakres</label>
              <select
                {...register("scope")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="personal">Osobisty</option>
                <option value="family">Rodzinny</option>
                <option value="shared">Wspólny</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Opis</label>
              <input
                {...register("description")}
                placeholder="Opcjonalny opis..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div className="md:col-span-2 flex gap-2">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
              >
                {createMutation.isPending ? "Zapisywanie..." : "Dodaj"}
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

      {/* Transactions list */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {isLoading ? (
          <p className="p-8 text-center text-gray-400">Ładowanie...</p>
        ) : transactions.length === 0 ? (
          <p className="p-8 text-center text-gray-400">Brak transakcji</p>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Data</th>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Opis</th>
                <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Kategoria</th>
                <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">Kwota</th>
                <th className="text-right text-xs font-medium text-gray-500 px-4 py-3">Akcje</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {transactions.map((tx: any) => (
                <tr key={tx.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-500">{tx.transaction_date}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {tx.description || (tx.transaction_type === "expense" ? "Wydatek" : "Przychód")}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">-</td>
                  <td className="px-4 py-3 text-sm font-medium text-right">
                    <span
                      className={`flex items-center justify-end gap-1 ${
                        tx.transaction_type === "expense" ? "text-red-600" : "text-green-600"
                      }`}
                    >
                      {tx.transaction_type === "expense" ? (
                        <ArrowDownCircle className="h-3.5 w-3.5" />
                      ) : (
                        <ArrowUpCircle className="h-3.5 w-3.5" />
                      )}
                      {formatCurrency(tx.amount, tx.currency)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => deleteMutation.mutate(tx.id)}
                      className="text-xs text-red-500 hover:text-red-700"
                    >
                      Usuń
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

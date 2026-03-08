import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useAuthStore } from "@/stores/authStore";
import { User, Lock, Save } from "lucide-react";

export default function ProfilePage() {
  const { user, setUser } = useAuthStore();
  const qc = useQueryClient();

  const [name, setName] = useState(user?.full_name || "");
  const [currency, setCurrency] = useState(user?.default_currency || "PLN");
  const [oldPwd, setOldPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [pwdMsg, setPwdMsg] = useState<string | null>(null);
  const [profileMsg, setProfileMsg] = useState<string | null>(null);

  const updateMutation = useMutation({
    mutationFn: (data: any) => api.patch("/users/me", data).then((r) => r.data),
    onSuccess: (data) => {
      setUser(data);
      qc.invalidateQueries({ queryKey: ["me"] });
      setProfileMsg("Profil zaktualizowany");
    },
  });

  const changePwdMutation = useMutation({
    mutationFn: (data: any) => api.post("/auth/change-password", data),
    onSuccess: () => {
      setPwdMsg("Hasło zostało zmienione");
      setOldPwd("");
      setNewPwd("");
    },
    onError: (err: any) => {
      setPwdMsg(err.response?.data?.detail || "Błąd zmiany hasła");
    },
  });

  return (
    <div className="p-6 space-y-6 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900">Profil użytkownika</h1>

      {/* Profile section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div className="flex items-center gap-3 mb-4">
          <User className="h-5 w-5 text-primary" />
          <h2 className="font-semibold text-gray-900">Dane osobowe</h2>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
            <input
              value={user?.email || ""}
              disabled
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Imię i nazwisko</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Domyślna waluta</label>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {["PLN", "EUR", "USD", "GBP", "JPY"].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>
          {profileMsg && (
            <p className="text-sm text-green-600">{profileMsg}</p>
          )}
          <button
            onClick={() => updateMutation.mutate({ full_name: name, default_currency: currency })}
            disabled={updateMutation.isPending}
            className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            {updateMutation.isPending ? "Zapisywanie..." : "Zapisz zmiany"}
          </button>
        </div>
      </div>

      {/* Password change */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div className="flex items-center gap-3 mb-4">
          <Lock className="h-5 w-5 text-primary" />
          <h2 className="font-semibold text-gray-900">Zmiana hasła</h2>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Aktualne hasło</label>
            <input
              type="password"
              value={oldPwd}
              onChange={(e) => setOldPwd(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nowe hasło</label>
            <input
              type="password"
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <p className="text-xs text-gray-400 mt-1">Minimum 8 znaków</p>
          </div>
          {pwdMsg && (
            <p className={`text-sm ${pwdMsg.includes("Błąd") ? "text-red-600" : "text-green-600"}`}>
              {pwdMsg}
            </p>
          )}
          <button
            onClick={() =>
              changePwdMutation.mutate({
                current_password: oldPwd,
                new_password: newPwd,
              })
            }
            disabled={changePwdMutation.isPending || !oldPwd || newPwd.length < 8}
            className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            <Lock className="h-4 w-4" />
            {changePwdMutation.isPending ? "Zmienianie..." : "Zmień hasło"}
          </button>
        </div>
      </div>
    </div>
  );
}

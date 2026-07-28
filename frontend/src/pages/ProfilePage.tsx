import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { clearClientSession } from "@/lib/session";
import { usersApi } from "@/lib/api/users";
import { authApi } from "@/lib/api/auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, setUser } = useAuthStore();
  const [name, setName] = useState(user?.full_name ?? "");
  const [currency, setCurrency] = useState(user?.default_currency ?? "PLN");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const [oldPwd, setOldPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [pwdError, setPwdError] = useState("");
  const [pwdLoading, setPwdLoading] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await usersApi.update({ full_name: name, default_currency: currency });
      setUser(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  const handleChangePwd = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwdError("");
    setPwdLoading(true);
    try {
      await authApi.changePassword(oldPwd, newPwd);
      setOldPwd("");
      setNewPwd("");
    } catch {
      setPwdError("Nieprawidłowe hasło lub błąd serwera.");
    } finally {
      setPwdLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Profil użytkownika</h1>

      <Card>
        <CardHeader><CardTitle>Dane profilu</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <Input label="Imię i nazwisko" value={name} onChange={(e) => setName(e.target.value)} />
          <Input label="Email" value={user?.email ?? ""} disabled />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Domyślna waluta</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={currency} onChange={(e) => setCurrency(e.target.value)}>
              {["PLN", "EUR", "USD", "GBP", "CHF", "CZK"].map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={handleSave} loading={saving}>Zapisz</Button>
            {saved && <span className="text-sm text-emerald-600">Zapisano!</span>}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Zmiana hasła</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleChangePwd} className="space-y-4">
            <Input label="Obecne hasło" type="password" value={oldPwd} onChange={(e) => setOldPwd(e.target.value)} required />
            <Input label="Nowe hasło" type="password" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} required minLength={8} />
            {pwdError && <p className="text-sm text-red-600">{pwdError}</p>}
            <Button type="submit" variant="secondary" loading={pwdLoading}>Zmień hasło</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <Button
            variant="danger"
            onClick={() => {
              clearClientSession();
              navigate("/login");
            }}
          >
            Wyloguj się
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

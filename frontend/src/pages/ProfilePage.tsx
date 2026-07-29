import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { clearClientSession } from "@/lib/session";
import { usersApi } from "@/lib/api/users";
import { supabase } from "@/lib/supabase";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, setUser } = useAuthStore();
  const [name, setName] = useState(user?.full_name ?? "");
  const [currency, setCurrency] = useState(user?.default_currency ?? "PLN");
  const [sessionEmail, setSessionEmail] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (user?.full_name) setName(user.full_name);
    if (user?.default_currency) setCurrency(user.default_currency);
  }, [user?.full_name, user?.default_currency]);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setSessionEmail(data.user?.email ?? "");
    });
  }, []);

  const displayEmail = user?.email || sessionEmail;

  const handleSave = async () => {
    setSaving(true);
    setError("");
    setSaved(false);
    try {
      const updated = await usersApi.update({ full_name: name, default_currency: currency });
      setUser(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      setError(
        "Nie udało się zapisać profilu. Sprawdź VITE_API_URL na Vercel i CORS na API."
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Profil użytkownika</h1>

      {!user?.id && (
        <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-sm text-amber-900">
          Profil nie został jeszcze zsynchronizowany z API. Zapis może nie działać, dopóki backend
          nie rozpozna konta Supabase.
        </div>
      )}

      <Card>
        <CardHeader><CardTitle>Dane profilu</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <Input label="Imię i nazwisko" value={name} onChange={(e) => setName(e.target.value)} />
          <Input label="Email" value={displayEmail} disabled />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Domyślna waluta</label>
            <select className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" value={currency} onChange={(e) => setCurrency(e.target.value)}>
              {["PLN", "EUR", "USD", "GBP", "CHF", "CZK"].map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <p className="text-xs text-gray-500">
            Logowanie przez Supabase (magic link / Google). Zarządzanie sesją w panelu konta Google lub linku z maila.
          </p>
          {error && (
            <div className="p-3 rounded-lg bg-destructive-muted border border-destructive/20 text-sm text-destructive">
              {error}
            </div>
          )}
          <div className="flex items-center gap-3">
            <Button onClick={handleSave} loading={saving}>Zapisz</Button>
            {saved && <span className="text-sm text-emerald-600">Zapisano!</span>}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <Button
            variant="danger"
            onClick={() => {
              void clearClientSession().then(() => navigate("/login"));
            }}
          >
            Wyloguj się
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

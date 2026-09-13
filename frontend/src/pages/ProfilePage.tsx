import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { usersApi } from "@/lib/api/users";
import { supabase } from "@/lib/supabase";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { clearClientSession } from "@/lib/session";
import { Link, useNavigate } from "react-router-dom";
import { Download, Trash2 } from "lucide-react";

export default function ProfilePage() {
  const { user, setUser } = useAuthStore();
  const navigate = useNavigate();
  const [name, setName] = useState(user?.full_name ?? "");
  const [currency, setCurrency] = useState(user?.default_currency ?? "PLN");
  const [sessionEmail, setSessionEmail] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState("");

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

  const handleExport = async () => {
    setExporting(true);
    setError("");
    try {
      const response = await usersApi.exportMyData();
      const url = URL.createObjectURL(response.data);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `familyorganiser-dane-${new Date().toISOString().slice(0, 10)}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("Nie udało się przygotować eksportu danych.");
    } finally {
      setExporting(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (confirmDelete !== "USUŃ KONTO") return;
    setDeleting(true);
    setError("");
    try {
      await usersApi.deleteMyAccount();
      await clearClientSession();
      navigate("/", { replace: true });
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail === "Transfer admin role in all groups before deleting your account"
        ? "Najpierw przekaż rolę administratora we wszystkich grupach rodzinnych."
        : detail === "account_deletion_not_configured"
          ? "Usuwanie konta nie zostało jeszcze skonfigurowane przez administratora."
          : "Nie udało się usunąć konta. Spróbuj ponownie lub skontaktuj się z administratorem.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-foreground">Profil użytkownika</h1>

      {!user?.id && (
        <div className="p-3 rounded-lg bg-warning-muted border border-warning/30 text-sm text-warning-foreground dark:text-warning">
          Profil nie został jeszcze zsynchronizowany z API. Zapis może nie działać, dopóki backend
          nie rozpozna konta Supabase.
        </div>
      )}

      <Card>
        <CardHeader><CardTitle>Wygląd</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">Motyw interfejsu — jasny, ciemny lub zgodny z systemem.</p>
          <ThemeToggle />
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Dane profilu</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <Input label="Imię i nazwisko" value={name} onChange={(e) => setName(e.target.value)} />
          <Input label="Email" value={displayEmail} disabled />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-foreground">Domyślna waluta</label>
            <select className="block w-full rounded-lg border border-input bg-background text-foreground px-3 py-2 text-sm" value={currency} onChange={(e) => setCurrency(e.target.value)}>
              {["PLN", "EUR", "USD", "GBP", "CHF", "CZK"].map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <p className="text-xs text-muted-foreground">
            Logowanie przez Supabase (magic link / Google). Zarządzanie sesją w panelu konta Google lub linku z maila.
          </p>
          {error && (
            <div className="p-3 rounded-lg bg-destructive-muted border border-destructive/20 text-sm text-destructive">
              {error}
            </div>
          )}
          <div className="flex items-center gap-3">
            <Button onClick={handleSave} loading={saving}>Zapisz</Button>
            {saved && <span className="text-sm text-success">Zapisano!</span>}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Prywatność i dane</CardTitle></CardHeader>
        <CardContent className="space-y-5">
          <p className="text-sm text-muted-foreground">
            Pobierz kopię danych zapisanych w FamilyOrganiser lub przeczytaj, jak je przetwarzamy.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button variant="secondary" onClick={handleExport} loading={exporting}>
              <Download className="h-4 w-4" /> Pobierz moje dane
            </Button>
            <Link to="/privacy" className="inline-flex min-h-11 items-center text-sm font-semibold text-primary underline">
              Polityka prywatności
            </Link>
          </div>
          <div className="space-y-3 border-t border-border pt-5">
            <h3 className="font-semibold text-destructive">Usuń konto</h3>
            <p className="text-sm text-muted-foreground">
              Prywatne dane zostaną usunięte lub zanonimizowane. Wspólne wpisy mogą pozostać w grupie bez Twojego imienia, aby nie usuwać danych innych członków. Administrator grupy musi najpierw przekazać swoją rolę.
            </p>
            <Input
              label='Wpisz „USUŃ KONTO”, aby potwierdzić'
              value={confirmDelete}
              onChange={(e) => setConfirmDelete(e.target.value)}
              autoComplete="off"
            />
            <Button variant="danger" onClick={handleDeleteAccount} loading={deleting} disabled={confirmDelete !== "USUŃ KONTO"}>
              <Trash2 className="h-4 w-4" /> Usuń konto bezpowrotnie
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

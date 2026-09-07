import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Clock } from "lucide-react";
import { usersApi } from "@/lib/api/users";
import { clearClientSession } from "@/lib/session";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";

const POLL_MS = 15_000;

export default function WaitingScreen() {
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const [checking, setChecking] = useState(false);

  const { data, refetch } = useQuery({
    queryKey: ["me-approval-gate"],
    queryFn: usersApi.me,
    refetchInterval: POLL_MS,
  });

  useEffect(() => {
    if (data) setUser(data);
  }, [data, setUser]);

  const handleCheck = async () => {
    setChecking(true);
    try {
      const result = await refetch();
      if (result.data) setUser(result.data);
    } finally {
      setChecking(false);
    }
  };

  const handleLogout = () => {
    void clearClientSession().then(() => navigate("/login"));
  };

  return (
    <div className="min-h-[100dvh] flex items-center justify-center bg-gradient-to-br from-background via-background to-primary-light/20 p-4 pt-[max(1rem,env(safe-area-inset-top))] pb-[max(1rem,env(safe-area-inset-bottom))]">
      <Card className="w-full max-w-md hover:shadow-sm">
        <CardContent className="py-8 space-y-6">
          <div className="flex flex-col items-center text-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
              <Clock className="h-6 w-6 text-primary" aria-hidden />
            </div>
            <h1 className="text-xl font-bold text-foreground tracking-tight">
              Konto oczekuje na akceptację
            </h1>
            <p className="text-sm text-muted-foreground max-w-[42ch] leading-relaxed">
              Administrator musi zaakceptować konto, zanim zobaczysz aplikację.
              Status sprawdzamy co 15 sekund.
            </p>
          </div>
          <div className="flex flex-col gap-2">
            <Button
              type="button"
              size="lg"
              className="w-full"
              loading={checking}
              onClick={() => void handleCheck()}
            >
              Sprawdź status
            </Button>
            <Button type="button" variant="outline" size="lg" className="w-full" onClick={handleLogout}>
              Wyloguj
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

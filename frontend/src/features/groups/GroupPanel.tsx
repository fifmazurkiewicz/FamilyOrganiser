import { useState } from "react";
import { Plus, Users, Copy, UserPlus } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { familyApi } from "@/lib/api/family";

export function GroupPanel() {
  const qc = useQueryClient();
  const { data: groups, isLoading } = useQuery({
    queryKey: ["groups"],
    queryFn: familyApi.listGroups,
  });
  const createGroup = useMutation({
    mutationFn: familyApi.createGroup,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["groups"] }),
  });
  const createInvite = useMutation({
    mutationFn: familyApi.createInvitation,
  });
  const joinGroup = useMutation({
    mutationFn: familyApi.joinGroup,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["groups"] });
      setJoinToken("");
      setJoinOpen(false);
    },
  });

  const [open, setOpen] = useState(false);
  const [joinOpen, setJoinOpen] = useState(false);
  const [joinToken, setJoinToken] = useState("");
  const [inviteData, setInviteData] = useState<{ display: string; copyValue: string } | null>(null);
  const [form, setForm] = useState({ name: "", description: "" });

  const handleCreate = async () => {
    await createGroup.mutateAsync({ name: form.name, description: form.description || undefined });
    setOpen(false);
    setForm({ name: "", description: "" });
  };

  const handleInvite = async (groupId: string) => {
    const data = await createInvite.mutateAsync(groupId);
    const copyValue = data.url ?? data.token;
    const display = data.url ?? `Kod zaproszenia: ${data.token}`;
    setInviteData({ display, copyValue });
  };

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">Grupy rodzinne</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setJoinOpen(true)}>
            <UserPlus className="h-4 w-4" /> Dołącz do grupy
          </Button>
          <Button size="sm" onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" /> Utwórz grupę
          </Button>
        </div>
      </div>

      <Modal open={joinOpen} onClose={() => { setJoinOpen(false); setJoinToken(""); }} title="Dołącz do grupy">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Wklej kod zaproszenia, który otrzymałeś od administratora grupy:</p>
          <Input
            label="Kod zaproszenia"
            value={joinToken}
            onChange={(e) => setJoinToken(e.target.value.trim())}
            placeholder="np. n9_jv40J8fBn0NdAFNzP9qzWHY11FMt88Nc7pl4qdjM"
          />
          {joinGroup.error && (
            <p className="text-sm text-destructive">
              {(joinGroup.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail
                ?? (joinGroup.error as Error).message}
            </p>
          )}
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => { setJoinOpen(false); setJoinToken(""); }}>Anuluj</Button>
            <Button onClick={() => joinGroup.mutate(joinToken)} loading={joinGroup.isPending} disabled={!joinToken}>
              Dołącz
            </Button>
          </div>
        </div>
      </Modal>

      {!groups || groups.length === 0 ? (
        <EmptyState icon={Users} title="Brak grup" description="Utwórz grupę rodzinną, aby dzielić finanse z bliskimi." action={{ label: "Utwórz grupę", onClick: () => setOpen(true) }} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {groups.map((g) => (
            <Card key={g.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle>{g.name}</CardTitle>
                  <Badge variant="info">{g.member_count} czł.</Badge>
                </div>
              </CardHeader>
              <CardContent>
                {g.description && <p className="text-sm text-muted-foreground mb-3">{g.description}</p>}
                <Button variant="outline" size="sm" onClick={() => handleInvite(g.id)} loading={createInvite.isPending}>
                  <Copy className="h-4 w-4" /> Zaproś
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="Nowa grupa rodzinna">
        <div className="space-y-4">
          <Input label="Nazwa grupy" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="np. Rodzina Kowalskich" />
          <Input label="Opis (opcjonalnie)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => setOpen(false)}>Anuluj</Button>
            <Button onClick={handleCreate} loading={createGroup.isPending} disabled={!form.name}>Utwórz</Button>
          </div>
        </div>
      </Modal>

      <Modal open={!!inviteData} onClose={() => setInviteData(null)} title="Link zaproszenia">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Wyślij ten link osobie, którą chcesz zaprosić do grupy:</p>
          <div className="flex gap-2">
            <code className="flex-1 rounded-lg bg-gray-100 px-3 py-2 text-xs break-all">{inviteData?.display}</code>
            <Button variant="outline" size="sm" onClick={() => navigator.clipboard.writeText(inviteData?.copyValue ?? "")} title="Kopiuj link">
              <Copy className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex justify-end">
            <Button onClick={() => setInviteData(null)}>Zamknij</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

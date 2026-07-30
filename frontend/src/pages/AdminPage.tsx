import { useState } from "react";
import { Shield, Users, Trash2, Lock, Unlock, Key } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "@/lib/api/users";
import { familyApi } from "@/lib/api/family";
import { authApi } from "@/lib/api/auth";

export default function AdminPage() {
  const qc = useQueryClient();
  const [tab, setTab] = useState<"users" | "families">("users");
  const [resetPwdUser, setResetPwdUser] = useState<{ id: string; email: string } | null>(null);
  const [newPassword, setNewPassword] = useState("");

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ["admin-users"],
    queryFn: usersApi.listUsers,
  });

  const { data: groups, isLoading: groupsLoading } = useQuery({
    queryKey: ["admin-groups"],
    queryFn: familyApi.adminListAllGroups,
  });

  const lockUser = useMutation({
    mutationFn: usersApi.lockUser,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-users"] }),
  });
  const unlockUser = useMutation({
    mutationFn: usersApi.unlockUser,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-users"] }),
  });
  const deleteUser = useMutation({
    mutationFn: usersApi.deleteUser,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-users"] }),
  });
  const deleteGroup = useMutation({
    mutationFn: familyApi.adminDeleteGroup,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-groups"] });
      qc.invalidateQueries({ queryKey: ["groups"] });
    },
  });
  const resetPassword = useMutation({
    mutationFn: ({ userId, password }: { userId: string; password: string }) =>
      authApi.adminResetPassword(userId, password),
    onSuccess: () => {
      setResetPwdUser(null);
      setNewPassword("");
    },
  });

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Shield className="h-8 w-8 text-primary" />
          Panel administratora
        </h1>
        <p className="text-muted-foreground mt-1">Zarządzaj użytkownikami i grupami rodzinnymi</p>
      </div>

      <div className="flex gap-2 border-b border-border">
        <button
          onClick={() => setTab("users")}
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${
            tab === "users" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Użytkownicy
        </button>
        <button
          onClick={() => setTab("families")}
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${
            tab === "families" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Grupy rodzinne
        </button>
      </div>

      {tab === "users" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Wszyscy użytkownicy</CardTitle>
          </CardHeader>
          <CardContent>
            {usersLoading ? (
              <Spinner />
            ) : !users || users.length === 0 ? (
              <p className="text-sm text-muted-foreground">Brak użytkowników</p>
            ) : (
              <div className="divide-y divide-border">
                {users.map((u) => (
                  <div key={u.id} className="flex flex-col gap-3 py-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="min-w-0">
                      <p className="font-medium truncate">{u.full_name}</p>
                      <p className="text-sm text-muted-foreground truncate">{u.email}</p>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {u.is_app_admin && <Badge variant="info">Admin</Badge>}
                        {u.is_locked && <Badge variant="danger">Zablokowany</Badge>}
                        {!u.is_active && <Badge variant="default">Nieaktywny</Badge>}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2 shrink-0">
                      {u.is_locked ? (
                        <Button variant="outline" size="sm" onClick={() => unlockUser.mutate(u.id)}>
                          <Unlock className="h-4 w-4" /> Odblokuj
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm" onClick={() => lockUser.mutate(u.id)} disabled={u.is_app_admin}>
                          <Lock className="h-4 w-4" /> Zablokuj
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setResetPwdUser({ id: u.id, email: u.email })}
                        disabled={!u.is_active}
                      >
                        <Key className="h-4 w-4" /> Reset hasła
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-destructive hover:bg-destructive-muted"
                        onClick={() => deleteUser.mutate(u.id)}
                        disabled={u.is_app_admin}
                      >
                        <Trash2 className="h-4 w-4" /> Usuń
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "families" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Wszystkie grupy rodzinne</CardTitle>
          </CardHeader>
          <CardContent>
            {groupsLoading ? (
              <Spinner />
            ) : !groups || groups.length === 0 ? (
              <p className="text-sm text-muted-foreground">Brak grup</p>
            ) : (
              <div className="divide-y divide-border">
                {groups.map((g) => (
                  <div key={g.id} className="flex items-center justify-between py-3">
                    <div>
                      <p className="font-medium">{g.name}</p>
                      <p className="text-sm text-muted-foreground">{g.member_count} członków</p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-destructive hover:bg-destructive-muted"
                      onClick={() => {
                        if (window.confirm(`Czy na pewno usunąć grupę "${g.name}"?`)) {
                          deleteGroup.mutate(g.id);
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4" /> Usuń
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Modal open={!!resetPwdUser} onClose={() => { setResetPwdUser(null); setNewPassword(""); }} title="Reset hasła">
        {resetPwdUser && (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">Nowe hasło dla: {resetPwdUser.email}</p>
            <Input
              label="Nowe hasło"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
            />
            {resetPassword.error && (
              <p className="text-sm text-destructive">{(resetPassword.error as Error).message}</p>
            )}
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setResetPwdUser(null)}>Anuluj</Button>
              <Button onClick={() => resetPassword.mutate({ userId: resetPwdUser.id, password: newPassword })} loading={resetPassword.isPending} disabled={!newPassword || newPassword.length < 6}>
                Zapisz
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

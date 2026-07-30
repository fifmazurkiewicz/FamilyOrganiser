import { useState } from "react";
import { Plus, CheckSquare, Trash2, Check, User, Calendar, History } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { useToast } from "@/components/ui/Toast";
import { useGroupStore } from "@/stores/groupStore";
import { api } from "@/api/client";
import { cn } from "@/utils/cn";
import { format } from "date-fns";
import { pl } from "date-fns/locale";

// ── Types ──

interface TaskItem {
  id: string;
  title: string;
  is_done: boolean;
  assigned_to?: string;
  assignee_name?: string;
  due_date?: string;
  done_by?: string;
  done_at?: string;
}

interface TaskList {
  id: string;
  name: string;
  items: TaskItem[];
  created_at: string;
}

interface FamilyMember {
  id: string;
  user_id: string;
  full_name: string;
}

// ── Components ──

function TaskListCard({
  list,
  selected,
  onSelect,
  onDelete,
}: {
  list: TaskList;
  selected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}) {
  const doneCount = list.items.filter((i) => i.is_done).length;
  return (
    <Card
      className={cn(
        "cursor-pointer transition-all duration-200",
        selected && "ring-2 ring-primary shadow-md"
      )}
      onClick={onSelect}
    >
      <CardContent className="flex items-center justify-between py-3 px-4">
        <div className="flex-1 min-w-0">
          <p className="font-medium text-foreground truncate">{list.name}</p>
          <p className="text-xs text-muted-foreground">
            {doneCount}/{list.items.length} wykonanych
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="text-red-500 hover:bg-red-50 shrink-0"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  );
}

function TaskItemsView({
  listId,
  items,
  showHistory,
  groupId,
}: {
  listId: string;
  items: TaskItem[];
  showHistory: boolean;
  groupId: string;
}) {
  const qc = useQueryClient();
  const { toast } = useToast();
  const [newTitle, setNewTitle] = useState("");

  const { data: historyData } = useQuery<TaskItem[]>({
    queryKey: ["task-items", listId, showHistory],
    queryFn: () =>
      api
        .get(`/v1/tasks/lists/${listId}/items`, {
          params: { include_done: showHistory },
        })
        .then((r) => r.data),
    enabled: showHistory,
  });

  const displayItems = showHistory ? historyData ?? items : items;

  const { data: members } = useQuery<FamilyMember[]>({
    queryKey: ["family-members", groupId],
    queryFn: () =>
      api.get(`/v1/groups/${groupId}/members`).then((r) => r.data),
    staleTime: 60000,
    enabled: !!groupId,
  });

  const invalidateTasks = () => {
    qc.invalidateQueries({ queryKey: ["task-lists"] });
    qc.invalidateQueries({ queryKey: ["task-items", listId] });
  };

  const toggleDone = useMutation({
    mutationFn: (itemId: string) => api.post(`/v1/tasks/items/${itemId}/toggle`),
    onSuccess: () => invalidateTasks(),
    onError: () => toast("error", "Błąd", "Nie udało się zaktualizować zadania."),
  });

  const assignUser = useMutation({
    mutationFn: ({
      itemId,
      assigned_to,
    }: {
      itemId: string;
      assigned_to: string | null;
    }) => api.patch(`/v1/tasks/items/${itemId}`, { assigned_to }),
    onSuccess: () => invalidateTasks(),
  });

  const addItem = useMutation({
    mutationFn: (title: string) =>
      api.post(`/v1/tasks/lists/${listId}/items`, { title }),
    onSuccess: () => {
      invalidateTasks();
      setNewTitle("");
      toast("success", "Dodano", "Zadanie zostało dodane.");
    },
    onError: () => toast("error", "Błąd", "Nie udało się dodać zadania."),
  });

  const removeItem = useMutation({
    mutationFn: (itemId: string) => api.delete(`/v1/tasks/items/${itemId}`),
    onSuccess: () => invalidateTasks(),
  });

  const sortedItems = [...displayItems].sort((a, b) => {
    if (a.is_done === b.is_done) return 0;
    return a.is_done ? 1 : -1;
  });

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || addItem.isPending) return;
    addItem.mutate(newTitle.trim());
  };

  return (
    <div className="space-y-3">
      <form onSubmit={handleAdd} className="flex gap-2">
        <Input
          placeholder="Dodaj zadanie..."
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          className="flex-1"
        />
        <Button
          type="submit"
          size="sm"
          disabled={!newTitle.trim()}
          loading={addItem.isPending}
        >
          <Plus className="h-4 w-4" /> Dodaj
        </Button>
      </form>

      {sortedItems.length === 0 ? (
        <p className="text-center text-sm text-muted-foreground py-6">
          Brak zadań. Dodaj pierwsze zadanie.
        </p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {sortedItems.map((item) => (
            <li
              key={item.id}
              className="flex items-start gap-3 py-3 group"
            >
              <button
                type="button"
                onClick={() => toggleDone.mutate(item.id)}
                className={cn(
                  "w-5 h-5 mt-0.5 rounded border-2 flex items-center justify-center shrink-0 transition-colors",
                  item.is_done
                    ? "bg-emerald-500 border-emerald-500 text-white"
                    : "border-border hover:border-primary"
                )}
              >
                {item.is_done && <Check className="h-3 w-3" />}
              </button>

              <div className="flex-1 min-w-0 space-y-1">
                <p
                  className={cn(
                    "text-sm",
                    item.is_done
                      ? "line-through text-muted-foreground"
                      : "text-foreground font-medium"
                  )}
                >
                  {item.title}
                </p>
                <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                  {item.due_date && (
                    <span className="inline-flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {format(new Date(item.due_date), "dd.MM.yyyy", { locale: pl })}
                    </span>
                  )}
                  {item.is_done && item.done_by && (
                    <span className="inline-flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {item.done_by}
                    </span>
                  )}
                </div>
              </div>

              {!item.is_done && (
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {members && members.length > 0 && (
                    <select
                      value={item.assigned_to ?? ""}
                      onChange={(e) =>
                        assignUser.mutate({
                          itemId: item.id,
                          assigned_to: e.target.value || null,
                        })
                      }
                      className="text-xs border border-border rounded px-1.5 py-1 bg-card text-muted-foreground"
                    >
                      <option value="">Przypisz...</option>
                      {members.map((m) => (
                        <option key={m.user_id} value={m.user_id}>
                          {m.full_name}
                        </option>
                      ))}
                    </select>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-400 hover:text-red-600"
                    onClick={() => removeItem.mutate(item.id)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Main Component ──

export function TaskList() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const { activeGroup } = useGroupStore();
  const [selectedListId, setSelectedListId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [newListName, setNewListName] = useState("");
  const [showHistory, setShowHistory] = useState(false);

  const { data: lists, isLoading } = useQuery<TaskList[]>({
    queryKey: ["task-lists", activeGroup?.id],
    queryFn: () =>
      api
        .get("/v1/tasks/lists", {
          params: { family_group_id: activeGroup!.id },
        })
        .then((r) => r.data),
    enabled: !!activeGroup?.id,
  });

  const createList = useMutation({
    mutationFn: (name: string) =>
      api.post("/v1/tasks/lists", {
        name,
        family_group_id: activeGroup!.id,
      }),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["task-lists"] });
      setCreateOpen(false);
      setNewListName("");
      setSelectedListId(res.data.id);
      toast("success", "Utworzono", `Lista "${res.data.name}" została utworzona.`);
    },
    onError: () => toast("error", "Błąd", "Nie udało się utworzyć listy."),
  });

  const deleteList = useMutation({
    mutationFn: (id: string) => api.delete(`/v1/tasks/lists/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["task-lists"] });
      if (selectedListId) setSelectedListId(null);
      toast("success", "Usunięto", "Lista zadań została usunięta.");
    },
  });

  const selectedList = lists?.find((l) => l.id === selectedListId);

  const handleCreateList = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newListName.trim() || !activeGroup?.id || createList.isPending) return;
    createList.mutate(newListName.trim());
  };

  if (!activeGroup) {
    return (
      <EmptyState
        icon={CheckSquare}
        title="Wybierz grupę rodzinną"
        description="Aby korzystać z list zadań, wybierz aktywną grupę w menu."
      />
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-7 w-28" />
          <Skeleton className="h-8 w-36" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">Zadania</h2>
        <Button size="sm" onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" /> Nowa lista
        </Button>
      </div>

      {!lists || lists.length === 0 ? (
        <EmptyState
          icon={CheckSquare}
          title="Brak zadań"
          description="Utwórz listę zadań, aby zorganizować pracę."
          action={{ label: "Utwórz listę", onClick: () => setCreateOpen(true) }}
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1fr_2fr]">
          <div className="space-y-2">
            {lists.map((list) => (
              <TaskListCard
                key={list.id}
                list={list}
                selected={list.id === selectedListId}
                onSelect={() =>
                  setSelectedListId(list.id === selectedListId ? null : list.id)
                }
                onDelete={() => deleteList.mutate(list.id)}
              />
            ))}
          </div>
          <div>
            {selectedList ? (
                          <Card className="h-full">
                            <CardHeader>
                              <div className="flex items-center justify-between">
                                <CardTitle>{selectedList.name}</CardTitle>
                                <button
                                  onClick={() => setShowHistory(!showHistory)}
                                  className={cn(
                                    "flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg border transition-all",
                                    showHistory
                                      ? "bg-primary/10 border-primary/30 text-primary"
                                      : "border-border text-muted-foreground hover:text-foreground hover:border-border"
                                  )}
                                >
                                  <History className="h-3.5 w-3.5" />
                                  Pokaż historię
                                </button>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <TaskItemsView
                                listId={selectedList.id}
                                items={selectedList.items}
                                showHistory={showHistory}
                                groupId={activeGroup.id}
                              />
                </CardContent>
              </Card>
            ) : (
              <div className="flex items-center justify-center h-48 border-2 border-dashed border-border rounded-xl">
                <p className="text-sm text-muted-foreground">Wybierz listę z lewej strony</p>
              </div>
            )}
          </div>
        </div>
      )}

      <Modal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Nowa lista zadań"
      >
        <form onSubmit={handleCreateList} className="space-y-4">
          <Input
            label="Nazwa listy"
            value={newListName}
            onChange={(e) => setNewListName(e.target.value)}
            placeholder="np. Prace domowe"
            autoFocus
          />
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="outline" onClick={() => setCreateOpen(false)}>
              Anuluj
            </Button>
            <Button
              type="submit"
              loading={createList.isPending}
              disabled={!newListName.trim()}
            >
              Utwórz
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
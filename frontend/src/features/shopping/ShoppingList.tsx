import { useState } from "react";
import { Plus, ShoppingCart, Trash2, Check, Undo2, History } from "lucide-react";
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

// ── Types ──

interface ShoppingItem {
  id: string;
  name: string;
  quantity: number;
  is_bought: boolean;
  bought_by?: string;
  bought_at?: string;
}

interface ShoppingList {
  id: string;
  name: string;
  items: ShoppingItem[];
  created_at: string;
}

// ── Components ──

function ShoppingListCard({
  list,
  selected,
  onSelect,
  onDelete,
}: {
  list: ShoppingList;
  selected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}) {
  const boughtCount = list.items.filter((i) => i.is_bought).length;
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
          <p className="font-medium text-gray-900 truncate">{list.name}</p>
          <p className="text-xs text-gray-500">
            {boughtCount}/{list.items.length} kupionych
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

function ShoppingItemsView({
  listId,
  items,
  showHistory,
}: {
  listId: string;
  items: ShoppingItem[];
  showHistory: boolean;
}) {
  const qc = useQueryClient();
  const { toast } = useToast();
  const [newItem, setNewItem] = useState("");

  const { data: historyData } = useQuery<ShoppingItem[]>({
    queryKey: ["shopping-items", listId, showHistory],
    queryFn: () =>
      api
        .get(`/v1/shopping/lists/${listId}/items`, {
          params: { include_done: showHistory },
        })
        .then((r) => r.data),
    enabled: showHistory,
  });

  const displayItems = showHistory ? historyData ?? items : items;

  const invalidateShopping = () => {
    qc.invalidateQueries({ queryKey: ["shopping-lists"] });
    qc.invalidateQueries({ queryKey: ["shopping-items", listId] });
  };

  const toggleItem = useMutation({
    mutationFn: (itemId: string) =>
      api.post(`/v1/shopping/items/${itemId}/toggle`),
    onSuccess: () => invalidateShopping(),
    onError: () => toast("error", "Błąd", "Nie udało się zaktualizować pozycji."),
  });

  const addItem = useMutation({
    mutationFn: (name: string) =>
      api.post(`/v1/shopping/lists/${listId}/items`, { name, quantity: 1 }),
    onSuccess: () => {
      invalidateShopping();
      setNewItem("");
    },
    onError: () => toast("error", "Błąd", "Nie udało się dodać pozycji."),
  });

  const removeItem = useMutation({
    mutationFn: (itemId: string) => api.delete(`/v1/shopping/items/${itemId}`),
    onSuccess: () => invalidateShopping(),
    onError: () => toast("error", "Błąd", "Nie udało się usunąć pozycji."),
  });

  const sortedItems = [...displayItems].sort((a, b) => {
    if (a.is_bought === b.is_bought) return 0;
    return a.is_bought ? 1 : -1;
  });

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItem.trim() || addItem.isPending) return;
    addItem.mutate(newItem.trim());
  };

  return (
    <div className="space-y-3">
      <form onSubmit={handleAdd} className="flex gap-2">
        <Input
          placeholder="Dodaj produkt..."
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          className="flex-1"
        />
        <Button type="submit" size="sm" disabled={!newItem.trim()} loading={addItem.isPending}>
          <Plus className="h-4 w-4" /> Dodaj
        </Button>
      </form>
      {sortedItems.length === 0 ? (
        <p className="text-center text-sm text-gray-400 py-6">
          Lista jest pusta. Dodaj pierwszy produkt.
        </p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {sortedItems.map((item) => (
            <li key={item.id} className="flex items-center gap-3 py-2.5 group">
              <button
                type="button"
                onClick={() => toggleItem.mutate(item.id)}
                className={cn(
                  "w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-colors",
                  item.is_bought
                    ? "bg-emerald-500 border-emerald-500 text-white"
                    : "border-gray-300 hover:border-primary"
                )}
              >
                {item.is_bought && <Check className="h-3 w-3" />}
              </button>
              <div className="flex-1 min-w-0">
                <p
                  className={cn(
                    "text-sm text-gray-900",
                    item.is_bought && "line-through text-gray-400"
                  )}
                >
                  {item.name}
                </p>
                {item.is_bought && item.bought_by && (
                  <p className="text-xs text-gray-400">Kupione przez: {item.bought_by}</p>
                )}
              </div>
              {item.is_bought ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-gray-400 hover:text-primary opacity-0 group-hover:opacity-100"
                  onClick={() => toggleItem.mutate(item.id)}
                  title="Cofnij kupienie"
                >
                  <Undo2 className="h-3.5 w-3.5" />
                </Button>
              ) : (
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100"
                  onClick={() => removeItem.mutate(item.id)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Main Component ──

export function ShoppingList() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const { activeGroup } = useGroupStore();
  const [selectedListId, setSelectedListId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [newListName, setNewListName] = useState("");
  const [showHistory, setShowHistory] = useState(false);

  const {
    data: lists,
    isLoading,
  } = useQuery<ShoppingList[]>({
    queryKey: ["shopping-lists", activeGroup?.id],
    queryFn: () =>
      api
        .get("/v1/shopping/lists", {
          params: { family_group_id: activeGroup!.id },
        })
        .then((r) => r.data),
    enabled: !!activeGroup?.id,
  });

  const createList = useMutation({
    mutationFn: (name: string) =>
      api.post("/v1/shopping/lists", {
        name,
        family_group_id: activeGroup!.id,
      }),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["shopping-lists"] });
      setCreateOpen(false);
      setNewListName("");
      setSelectedListId(res.data.id);
      toast("success", "Utworzono", `Lista "${res.data.name}" została utworzona.`);
    },
    onError: () => toast("error", "Błąd", "Nie udało się utworzyć listy."),
  });

  const deleteList = useMutation({
    mutationFn: (id: string) => api.delete(`/v1/shopping/lists/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["shopping-lists"] });
      if (selectedListId) setSelectedListId(null);
      toast("success", "Usunięto", "Lista zakupów została usunięta.");
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
        icon={ShoppingCart}
        title="Wybierz grupę rodzinną"
        description="Aby korzystać z list zakupów, wybierz aktywną grupę w menu."
      />
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-7 w-32" />
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
        <h2 className="text-lg font-semibold text-gray-900">Listy zakupów</h2>
        <Button size="sm" onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" /> Nowa lista
        </Button>
      </div>

      {!lists || lists.length === 0 ? (
        <EmptyState
          icon={ShoppingCart}
          title="Brak list zakupów"
          description="Utwórz pierwszą listę zakupów, aby zacząć."
          action={{ label: "Utwórz listę", onClick: () => setCreateOpen(true) }}
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1fr_2fr]">
          <div className="space-y-2">
            {lists.map((list) => (
              <ShoppingListCard
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
                      type="button"
                      onClick={() => setShowHistory(!showHistory)}
                      className={cn(
                        "flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg border transition-all",
                        showHistory
                          ? "bg-primary/10 border-primary/30 text-primary"
                          : "border-gray-200 text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      )}
                    >
                      <History className="h-3.5 w-3.5" />
                      Pokaż historię
                    </button>
                  </div>
                </CardHeader>
                <CardContent>
                  <ShoppingItemsView
                    listId={selectedList.id}
                    items={selectedList.items}
                    showHistory={showHistory}
                  />
                </CardContent>
              </Card>
            ) : (
              <div className="flex items-center justify-center h-48 border-2 border-dashed border-gray-200 rounded-xl">
                <p className="text-sm text-gray-400">Wybierz listę z lewej strony</p>
              </div>
            )}
          </div>
        </div>
      )}

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="Nowa lista zakupów">
        <form onSubmit={handleCreateList} className="space-y-4">
          <Input
            label="Nazwa listy"
            value={newListName}
            onChange={(e) => setNewListName(e.target.value)}
            placeholder="np. Zakupy na weekend"
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

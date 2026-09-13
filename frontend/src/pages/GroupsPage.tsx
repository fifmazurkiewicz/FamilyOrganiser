import { GroupPanel } from "@/features/groups/GroupPanel";

export default function GroupsPage() {
  return (
    <div className="p-6 space-y-4">
      <p className="rounded-xl border border-primary/20 bg-primary-light/40 p-3 text-sm text-muted-foreground">
        Dane zapisane w grupie mogą być widoczne dla jej członków zgodnie z ustawieniami udostępniania. Nie dodawaj niepotrzebnych danych innych osób.
      </p>
      <GroupPanel />
    </div>
  );
}

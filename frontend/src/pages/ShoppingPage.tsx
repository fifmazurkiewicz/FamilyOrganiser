import { ShoppingList } from "@/features/shopping/ShoppingList";

export default function ShoppingPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Lista zakupów</h1>
      <ShoppingList />
    </div>
  );
}
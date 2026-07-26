import { ExpenseList } from "@/features/expenses/ExpenseList";

export default function ExpensesPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Wydatki</h1>
      <ExpenseList />
    </div>
  );
}
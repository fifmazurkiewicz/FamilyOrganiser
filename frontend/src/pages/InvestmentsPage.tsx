import { InvestmentList } from "@/features/investments/InvestmentList";

export default function InvestmentsPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Inwestycje</h1>
      <InvestmentList />
    </div>
  );
}
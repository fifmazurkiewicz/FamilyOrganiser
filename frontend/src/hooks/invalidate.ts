import type { QueryClient } from "@tanstack/react-query";

/**
 * Operacje pieniężne (transakcje, przychody) zmieniają salda kont oraz dane
 * dashboardu i trendu miesięcznego — odświeżamy je wszystkie jednym wywołaniem.
 */
export function invalidateFinanceViews(qc: QueryClient, ...extraKeys: readonly (readonly string[])[]) {
  const keys = [["accounts"], ["dashboard"], ["monthly-trend"], ...extraKeys];
  keys.forEach((queryKey) => qc.invalidateQueries({ queryKey }));
}

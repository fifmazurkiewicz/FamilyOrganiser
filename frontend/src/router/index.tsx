import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import Layout from "@/components/layout/Layout";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import AccountsPage from "@/pages/AccountsPage";
import TransactionsPage from "@/pages/TransactionsPage";
import ShoppingPage from "@/pages/ShoppingPage";
import TasksPage from "@/pages/TasksPage";
import ExpensesPage from "@/pages/ExpensesPage";
import BudgetMonthlyPage from "@/pages/BudgetMonthlyPage";
import SavingsPage from "@/pages/SavingsPage";
import InvestmentsPage from "@/pages/InvestmentsPage";
import IncomePage from "@/pages/IncomePage";
import ReportsPage from "@/pages/ReportsPage";
import GroupsPage from "@/pages/GroupsPage";
import ProfilePage from "@/pages/ProfilePage";
import NotificationsPage from "@/pages/NotificationsPage";
import AdminPage from "@/pages/AdminPage";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function RequireAdmin({ children }: { children: React.ReactNode }) {
  const isAdmin = useAuthStore((s) => s.user?.is_app_admin);
  if (!isAdmin) return <Navigate to="/app" replace />;
  return <>{children}</>;
}

function HomeRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (isAuthenticated) return <Navigate to="/app" replace />;
  return <LandingPage />;
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomeRoute />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Authenticated app routes */}
        <Route
          path="/app"
          element={
            <RequireAuth>
              <Layout />
            </RequireAuth>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="accounts" element={<AccountsPage />} />
          <Route path="transactions" element={<TransactionsPage />} />
          <Route path="shopping" element={<ShoppingPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="expenses" element={<ExpensesPage />} />
          <Route path="budget" element={<Navigate to="/app/budget-monthly" replace />} />
          <Route path="budget-monthly" element={<BudgetMonthlyPage />} />
          <Route path="savings" element={<SavingsPage />} />
          <Route path="investments" element={<InvestmentsPage />} />
          <Route path="income" element={<IncomePage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="groups" element={<GroupsPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="admin" element={<RequireAdmin><AdminPage /></RequireAdmin>} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
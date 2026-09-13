import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import Layout from "@/components/layout/Layout";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import AuthCallbackPage from "@/pages/AuthCallbackPage";
import DashboardPage from "@/pages/DashboardPage";
import ShoppingPage from "@/pages/ShoppingPage";
import TasksPage from "@/pages/TasksPage";
import BudgetMonthlyPage from "@/pages/BudgetMonthlyPage";
import InvestmentsPage from "@/pages/InvestmentsPage";
import ReportsPage from "@/pages/ReportsPage";
import GroupsPage from "@/pages/GroupsPage";
import ProfilePage from "@/pages/ProfilePage";
import NotificationsPage from "@/pages/NotificationsPage";
import AdminPage from "@/pages/AdminPage";
import WaitingScreen from "@/pages/WaitingScreen";
import PrivacyPage from "@/pages/PrivacyPage";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function RequireApproved({ children }: { children: React.ReactNode }) {
  const isApproved = useAuthStore((s) => s.user?.is_approved);
  if (!isApproved) return <WaitingScreen />;
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
        <Route path="/" element={<HomeRoute />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />

        <Route
          path="/app"
          element={
            <RequireAuth>
              <RequireApproved>
                <Layout />
              </RequireApproved>
            </RequireAuth>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="shopping" element={<ShoppingPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="budget" element={<Navigate to="/app/budget-monthly" replace />} />
          <Route path="budget-monthly" element={<BudgetMonthlyPage />} />
          <Route path="investments" element={<InvestmentsPage />} />
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

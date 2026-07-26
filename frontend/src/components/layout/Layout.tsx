import { useState, useEffect } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { useGroupStore } from "@/stores/groupStore";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import {
  LayoutDashboard, CreditCard, Receipt, PiggyBank, TrendingUp,
  DollarSign, BarChart2, Users, Bell, User, LogOut, ChevronDown,
  Shield, Menu, X, Home, ChevronRight, ShoppingCart, CheckSquare,
  PieChart
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useMediaQuery } from "@/hooks/useMediaQuery";

const navItems = [
  { to: "/app", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/app/accounts", icon: CreditCard, label: "Konta" },
  { to: "/app/transactions", icon: Receipt, label: "Transakcje" },
  { to: "/app/shopping", icon: ShoppingCart, label: "Lista zakupów" },
  { to: "/app/tasks", icon: CheckSquare, label: "Zadania" },
  { to: "/app/expenses", icon: Receipt, label: "Wydatki" },
  { to: "/app/budget-monthly", icon: PieChart, label: "Budżet miesięczny" },
  { to: "/app/savings", icon: PiggyBank, label: "Oszczędności" },
  { to: "/app/investments", icon: TrendingUp, label: "Inwestycje" },
  { to: "/app/income", icon: DollarSign, label: "Przychody" },
  { to: "/app/reports", icon: BarChart2, label: "Raporty" },
  { to: "/app/groups", icon: Users, label: "Grupy rodzinne" },
];

function UserAvatar({ name, size = "sm" }: { name?: string; size?: "sm" | "md" }) {
  const initials = name
    ? name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "?";
  return (
    <div
      className={cn(
        "rounded-full bg-primary-light text-primary-dark font-semibold flex items-center justify-center shrink-0",
        size === "sm" ? "w-8 h-8 text-xs" : "w-10 h-10 text-sm"
      )}
    >
      {initials}
    </div>
  );
}

export default function Layout() {
  const { logout, user, setUser } = useAuthStore();
  const { activeGroup, groups, setGroups, setActiveGroup } = useGroupStore();
  const navigate = useNavigate();
  const isDesktop = useMediaQuery("(min-width: 1024px)");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [groupMenuOpen, setGroupMenuOpen] = useState(false);

  // Auto-close sidebar on desktop
  useEffect(() => {
    if (isDesktop) setSidebarOpen(true);
    else setSidebarOpen(false);
  }, [isDesktop]);

  // Close sidebar on navigate (mobile)
  const handleNav = (to: string) => {
    if (!isDesktop) setSidebarOpen(false);
    navigate(to);
  };

  const { data: userData } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get("/v1/users/me").then((r) => r.data),
  });

  useEffect(() => {
    if (userData) setUser(userData);
  }, [userData, setUser]);

  const { data: groupsData } = useQuery({
    queryKey: ["groups"],
    queryFn: () => api.get("/v1/groups/").then((r) => r.data),
  });

  useEffect(() => {
    if (groupsData) {
      setGroups(groupsData);
      if (groupsData.length === 0) {
        setActiveGroup(null);
      } else if (!activeGroup || !groupsData.some((g: { id: string }) => g.id === activeGroup.id)) {
        setActiveGroup(groupsData[0]);
      }
    }
  }, [groupsData, activeGroup, setGroups, setActiveGroup]);

  const { data: notifData } = useQuery({
    queryKey: ["notif-count"],
    queryFn: () => api.get("/v1/notifications/count").then((r) => r.data),
    refetchInterval: 30000,
  });

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Overlay for mobile
  const overlay = !isDesktop && sidebarOpen && (
    <div
      className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden"
      onClick={() => setSidebarOpen(false)}
    />
  );

  return (
    <div className="flex h-screen overflow-hidden bg-gradient-to-br from-gray-50 via-white to-primary-light/30">
      {overlay}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 flex-shrink-0 bg-white/90 backdrop-blur-md border-r border-gray-200/60 flex flex-col shadow-xl shadow-gray-200/20 transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0",
          !sidebarOpen && !isDesktop && "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="p-5 border-b border-gray-100/80 flex items-center justify-between">
          <button onClick={() => navigate("/")} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center group-hover:bg-primary-dark transition-colors">
              <Home className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-900 tracking-tight">
              Family<span className="text-primary">Organiser</span>
            </span>
          </button>
          {!isDesktop && (
            <button onClick={() => setSidebarOpen(false)} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400">
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Group selector */}
        <div className="px-4 py-3 border-b border-gray-100/80">
          {groups.length === 0 ? (
            <button
              onClick={() => handleNav("/groups")}
              className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg border border-dashed border-gray-300 text-sm text-gray-500 hover:border-primary hover:text-primary hover:bg-primary-light/50 transition-all"
            >
              <Users className="h-4 w-4" />
              <span>Utwórz grupę rodzinną</span>
              <ChevronRight className="h-4 w-4 ml-auto" />
            </button>
          ) : (
            <div className="relative">
              <button
                onClick={() => setGroupMenuOpen(!groupMenuOpen)}
                className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
              >
                <div className="w-7 h-7 rounded-md bg-primary-light flex items-center justify-center">
                  <Users className="h-3.5 w-3.5 text-primary" />
                </div>
                <span className="flex-1 text-left truncate">{activeGroup?.name || "Wybierz grupę"}</span>
                <ChevronDown className={cn("h-4 w-4 text-gray-400 transition-transform", groupMenuOpen && "rotate-180")} />
              </button>
              {groupMenuOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-xl border border-gray-200 shadow-lg z-50 overflow-hidden animate-in fade-in slide-in-from-top-1 duration-200">
                  {groups.map((g: { id: string; name: string; member_count: number }) => (
                    <button
                      key={g.id}
                      onClick={() => { setActiveGroup(g); setGroupMenuOpen(false); }}
                      className={cn(
                        "w-full text-left px-4 py-2.5 text-sm hover:bg-primary-light/50 flex items-center gap-2 transition-colors",
                        activeGroup?.id === g.id && "bg-primary-light/70 font-semibold text-primary"
                      )}
                    >
                      {g.name}
                      <span className="text-gray-400 text-xs ml-auto">{g.member_count} os.</span>
                      {activeGroup?.id === g.id && <span className="text-primary text-xs">✓</span>}
                    </button>
                  ))}
                  <div className="border-t border-gray-100">
                    <button
                      onClick={() => { handleNav("/groups"); setGroupMenuOpen(false); }}
                      className="w-full text-left px-4 py-2.5 text-sm text-primary font-medium hover:bg-primary-light/50 transition-colors"
                    >
                      + Utwórz / zarządzaj grupami
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-0.5">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/app"}
              onClick={() => !isDesktop && setSidebarOpen(false)}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group",
                  isActive
                    ? "bg-primary text-white shadow-md shadow-primary/25"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )
              }
            >
              <item.icon className={cn("h-4.5 w-4.5 shrink-0")} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Bottom section */}
        <div className="p-3 border-t border-gray-100/80 space-y-1">
          <NavLink
            to="/notifications"
            onClick={() => !isDesktop && setSidebarOpen(false)}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive ? "bg-primary text-white shadow-md shadow-primary/25" : "text-gray-600 hover:bg-gray-100"
              )
            }
          >
            <Bell className="h-4.5 w-4.5 shrink-0" />
            <span>Powiadomienia</span>
            {notifData?.count > 0 && (
              <span className="ml-auto bg-destructive text-white text-xs font-bold rounded-full min-w-[20px] h-5 flex items-center justify-center px-1.5">
                {notifData.count}
              </span>
            )}
          </NavLink>

          <NavLink
            to="/profile"
            onClick={() => !isDesktop && setSidebarOpen(false)}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive ? "bg-primary text-white shadow-md shadow-primary/25" : "text-gray-600 hover:bg-gray-100"
              )
            }
          >
            <UserAvatar name={user?.full_name} />
            <span className="truncate">{user?.full_name || "Profil"}</span>
          </NavLink>

          {user?.is_app_admin && (
            <NavLink
              to="/admin"
              onClick={() => !isDesktop && setSidebarOpen(false)}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive ? "bg-primary text-white shadow-md shadow-primary/25" : "text-gray-600 hover:bg-gray-100"
                )
              }
            >
              <Shield className="h-4.5 w-4.5 shrink-0" />
              Panel admina
            </NavLink>
          )}

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-500 hover:text-destructive hover:bg-destructive-muted w-full transition-all duration-200"
          >
            <LogOut className="h-4.5 w-4.5 shrink-0" />
            <span>Wyloguj</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {/* Mobile top bar */}
        {!isDesktop && (
          <div className="sticky top-0 z-30 flex items-center justify-between px-4 py-3 bg-white/80 backdrop-blur-md border-b border-gray-200/60">
            <button onClick={() => setSidebarOpen(true)} className="p-1.5 -ml-1 rounded-lg hover:bg-gray-100 text-gray-600">
              <Menu className="h-5 w-5" />
            </button>
            <button onClick={() => navigate("/")} className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
                <Home className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="text-base font-bold text-gray-900 tracking-tight">
                Family<span className="text-primary">Organiser</span>
              </span>
            </button>
            <button onClick={() => navigate("/profile")} className="p-1 -mr-1">
              <UserAvatar name={user?.full_name} />
            </button>
          </div>
        )}
        <div className={cn(!isDesktop && "pt-0")}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
import { useState, useEffect } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { useGroupStore } from "@/stores/groupStore";
import { clearClientSession } from "@/lib/session";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import {
  LayoutDashboard, TrendingUp,
  BarChart2, Users, Bell, LogOut, ChevronDown,
  Shield, Menu, X, Home, ChevronRight, ShoppingCart, CheckSquare,
  PieChart
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { ThemeToggle } from "@/components/theme/ThemeToggle";

const navItems = [
  { to: "/app", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/app/shopping", icon: ShoppingCart, label: "Lista zakupów" },
  { to: "/app/tasks", icon: CheckSquare, label: "Zadania" },
  { to: "/app/budget-monthly", icon: PieChart, label: "Budżet miesięczny" },
  { to: "/app/investments", icon: TrendingUp, label: "Inwestycje" },
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
  const { user, setUser } = useAuthStore();
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
    queryKey: ["me", user?.id],
    queryFn: () => api.get("/v1/users/me").then((r) => r.data),
  });

  useEffect(() => {
    if (userData) setUser(userData);
  }, [userData, setUser]);

  const { data: groupsData } = useQuery({
    queryKey: ["groups", user?.id],
    queryFn: () => api.get("/v1/groups/").then((r) => r.data),
    enabled: !!user?.id,
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
    queryKey: ["notif-count", user?.id],
    queryFn: () => api.get("/v1/notifications/count").then((r) => r.data),
    enabled: !!user?.id,
    refetchInterval: 30000,
  });

  const handleLogout = () => {
    void clearClientSession().then(() => navigate("/login"));
  };

  // Overlay for mobile
  const overlay = !isDesktop && sidebarOpen && (
    <div
      className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden"
      onClick={() => setSidebarOpen(false)}
    />
  );

  return (
    <div className="flex h-dvh overflow-hidden bg-gradient-to-br from-background via-background to-primary-light/30">
      {overlay}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] flex-shrink-0 bg-card/90 backdrop-blur-md border-r border-border flex flex-col shadow-xl shadow-black/5 dark:shadow-black/20 transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0",
          "pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]",
          !sidebarOpen && !isDesktop && "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="p-5 border-b border-border flex items-center justify-between">
          <button onClick={() => navigate("/")} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center group-hover:bg-primary-dark transition-colors">
              <Home className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold text-foreground tracking-tight">
              Family<span className="text-primary">Organiser</span>
            </span>
          </button>
          {!isDesktop && (
            <button onClick={() => setSidebarOpen(false)} className="p-1.5 rounded-lg hover:bg-muted text-muted-foreground">
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Group selector */}
        <div className="px-4 py-3 border-b border-border">
          {groups.length === 0 ? (
            <button
              onClick={() => handleNav("/app/groups")}
              className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg border border-dashed border-border text-sm text-muted-foreground hover:border-primary hover:text-primary hover:bg-primary-light/50 transition-all"
            >
              <Users className="h-4 w-4" />
              <span>Utwórz grupę rodzinną</span>
              <ChevronRight className="h-4 w-4 ml-auto" />
            </button>
          ) : (
            <div className="relative">
              <button
                onClick={() => setGroupMenuOpen(!groupMenuOpen)}
                className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-sm font-medium text-foreground hover:bg-muted transition-colors"
              >
                <div className="w-7 h-7 rounded-md bg-primary-light flex items-center justify-center">
                  <Users className="h-3.5 w-3.5 text-primary" />
                </div>
                <span className="flex-1 text-left truncate">{activeGroup?.name || "Wybierz grupę"}</span>
                <ChevronDown className={cn("h-4 w-4 text-muted-foreground transition-transform", groupMenuOpen && "rotate-180")} />
              </button>
              {groupMenuOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-card rounded-xl border border-border shadow-lg z-50 overflow-hidden animate-in fade-in slide-in-from-top-1 duration-200">
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
                      <span className="text-muted-foreground text-xs ml-auto">{g.member_count} os.</span>
                      {activeGroup?.id === g.id && <span className="text-primary text-xs">✓</span>}
                    </button>
                  ))}
                  <div className="border-t border-border">
                    <button
                      onClick={() => { handleNav("/app/groups"); setGroupMenuOpen(false); }}
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
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )
              }
            >
              <item.icon className={cn("h-4.5 w-4.5 shrink-0")} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Bottom section */}
        <div className="p-3 border-t border-border space-y-1 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
          <div className="px-3 py-2 flex items-center justify-between gap-2">
            <span className="text-xs font-medium text-muted-foreground">Motyw</span>
            <ThemeToggle variant="compact" />
          </div>
          <NavLink
            to="/app/notifications"
            onClick={() => !isDesktop && setSidebarOpen(false)}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive ? "bg-primary text-white shadow-md shadow-primary/25" : "text-muted-foreground hover:bg-muted"
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
            to="/app/profile"
            onClick={() => !isDesktop && setSidebarOpen(false)}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive ? "bg-primary text-white shadow-md shadow-primary/25" : "text-muted-foreground hover:bg-muted"
              )
            }
          >
            <UserAvatar name={user?.full_name} />
            <span className="truncate">{user?.full_name || "Profil"}</span>
          </NavLink>

          {user?.is_app_admin && (
            <NavLink
              to="/app/admin"
              onClick={() => !isDesktop && setSidebarOpen(false)}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive ? "bg-primary text-white shadow-md shadow-primary/25" : "text-muted-foreground hover:bg-muted"
                )
              }
            >
              <Shield className="h-4.5 w-4.5 shrink-0" />
              Panel admina
            </NavLink>
          )}

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-muted-foreground hover:text-destructive hover:bg-destructive-muted w-full transition-all duration-200"
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
          <div className="sticky top-0 z-30 flex items-center justify-between px-4 py-3 pt-[max(0.75rem,env(safe-area-inset-top))] bg-card/80 backdrop-blur-md border-b border-border">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="p-2 -ml-1 rounded-lg hover:bg-muted text-muted-foreground min-h-11 min-w-11 flex items-center justify-center"
              aria-label="Otwórz menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            <button type="button" onClick={() => navigate("/")} className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
                <Home className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="text-base font-bold text-foreground tracking-tight">
                Family<span className="text-primary">Organiser</span>
              </span>
            </button>
            <button
              type="button"
              onClick={() => navigate("/app/profile")}
              className="p-1 -mr-1 min-h-11 min-w-11 flex items-center justify-center"
              aria-label="Profil"
            >
              <UserAvatar name={user?.full_name} />
            </button>
          </div>
        )}
        <div className={cn(!isDesktop && "pt-0 pb-[env(safe-area-inset-bottom)]")}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
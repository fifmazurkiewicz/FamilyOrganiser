import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { useGroupStore } from "@/stores/groupStore";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import {
  LayoutDashboard, CreditCard, Receipt, PiggyBank, TrendingUp,
  DollarSign, BarChart2, Users, Bell, User, LogOut, ChevronDown, Shield
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useEffect } from "react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/accounts", icon: CreditCard, label: "Konta" },
  { to: "/transactions", icon: Receipt, label: "Transakcje" },
  { to: "/budget", icon: BarChart2, label: "Budżet" },
  { to: "/savings", icon: PiggyBank, label: "Oszczędności" },
  { to: "/investments", icon: TrendingUp, label: "Inwestycje" },
  { to: "/income", icon: DollarSign, label: "Przychody" },
  { to: "/reports", icon: BarChart2, label: "Raporty" },
  { to: "/groups", icon: Users, label: "Grupy rodzinne" },
];

export default function Layout() {
  const { logout, user, setUser } = useAuthStore();
  const { activeGroup, groups, setGroups, setActiveGroup } = useGroupStore();
  const navigate = useNavigate();

  // Fetch current user profile
  const { data: userData } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get("/v1/users/me").then((r) => r.data),
  });

  useEffect(() => {
    if (userData) setUser(userData);
  }, [userData, setUser]);

  // Fetch groups
  const { data: groupsData } = useQuery({
    queryKey: ["groups"],
    queryFn: () => api.get("/v1/groups/").then((r) => r.data),
  });

  useEffect(() => {
    if (groupsData) {
      setGroups(groupsData);
      if (groupsData.length === 0) {
        setActiveGroup(null);
      } else if (!activeGroup || !groupsData.some((g) => g.id === activeGroup.id)) {
        setActiveGroup(groupsData[0]);
      }
    }
  }, [groupsData, activeGroup, setGroups, setActiveGroup]);

  // Fetch unread notification count
  const { data: notifData } = useQuery({
    queryKey: ["notif-count"],
    queryFn: () => api.get("/v1/notifications/count").then((r) => r.data),
    refetchInterval: 30000,
  });

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-primary">FamilyOrganiser</h1>
        </div>

        {/* Group selector */}
        <div className="px-4 py-3 border-b border-gray-200">
          {groups.length <= 1 ? (
            <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <Users className="h-4 w-4 text-primary" />
              <span>{activeGroup?.name || "Brak grupy"}</span>
            </div>
          ) : (
            <div className="relative group">
              <button className="flex items-center gap-2 text-sm font-medium text-gray-700 w-full hover:text-primary">
                <Users className="h-4 w-4 text-primary" />
                <span className="flex-1 text-left truncate">{activeGroup?.name || "Wybierz grupę"}</span>
                <ChevronDown className="h-4 w-4" />
              </button>
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 hidden group-hover:block">
                {groups.map((g) => (
                  <button
                    key={g.id}
                    onClick={() => setActiveGroup(g)}
                    className={cn(
                      "w-full text-left px-3 py-2 text-sm hover:bg-gray-50",
                      activeGroup?.id === g.id && "font-semibold text-primary"
                    )}
                  >
                    {g.name}
                    <span className="ml-1 text-gray-400 text-xs">({g.member_count})</span>
                    {activeGroup?.id === g.id && <span className="ml-1 text-primary">✓</span>}
                  </button>
                ))}
                <button
                  onClick={() => navigate("/groups")}
                  className="w-full text-left px-3 py-2 text-sm text-primary border-t border-gray-100 hover:bg-gray-50"
                >
                  + Utwórz nową grupę
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-white"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-gray-200 space-y-1">
          <NavLink
            to="/notifications"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive ? "bg-primary text-white" : "text-gray-600 hover:bg-gray-100"
              )
            }
          >
            <Bell className="h-4 w-4" />
            Powiadomienia
            {notifData?.count > 0 && (
              <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5">
                {notifData.count}
              </span>
            )}
          </NavLink>
          <NavLink
            to="/profile"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive ? "bg-primary text-white" : "text-gray-600 hover:bg-gray-100"
              )
            }
          >
            <User className="h-4 w-4" />
            {user?.full_name || "Profil"}
          </NavLink>
          {user?.is_app_admin && (
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive ? "bg-primary text-white" : "text-gray-600 hover:bg-gray-100"
                )
              }
            >
              <Shield className="h-4 w-4" />
              Panel admina
            </NavLink>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 w-full"
          >
            <LogOut className="h-4 w-4" />
            Wyloguj
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

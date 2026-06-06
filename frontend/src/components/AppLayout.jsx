import { BarChart3, ClipboardCheck, FileText, LayoutDashboard, LogOut, MapPinned, Star } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const items = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/placements", label: "Placements", icon: MapPinned },
  { to: "/weekly-logs", label: "Weekly Logs", icon: FileText },
  { to: "/reviews", label: "Reviews", icon: ClipboardCheck },
  { to: "/evaluations", label: "Evaluations", icon: Star },
  { to: "/dashboard", label: "Reports", icon: BarChart3 }
];

export default function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white lg:block">
        <div className="border-b border-slate-200 px-6 py-5">
          <p className="text-lg font-bold text-slate-950">ILES</p>
          <p className="text-sm text-slate-500">{user?.role || "Internship system"}</p>
        </div>
        <nav className="space-y-1 px-3 py-4">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={label}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${
                  isActive ? "bg-cyan-50 text-cyan-700" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur lg:px-8">
          <div>
            <p className="text-sm text-slate-500">Welcome back</p>
            <h1 className="text-lg font-semibold">{user?.full_name || user?.username || "User"}</h1>
          </div>
          <button className="btn-secondary" onClick={logout} type="button">
            <LogOut size={16} />
            Logout
          </button>
        </header>
        <div className="mx-auto max-w-7xl px-4 py-6 lg:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

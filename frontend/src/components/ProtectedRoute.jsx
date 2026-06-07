import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function ProtectedRoute({ allowedRoles = [] }) {
  const { checkingSession, isAuthenticated, user } = useAuth();

  if (checkingSession) {
    return <div className="flex min-h-screen items-center justify-center text-slate-500">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

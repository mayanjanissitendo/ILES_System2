import { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("iles_token"));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("iles_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [checkingSession, setCheckingSession] = useState(Boolean(token));

  useEffect(() => {
    if (!token) {
      setCheckingSession(false);
      return;
    }
    api.get("auth/me/")
      .then(({ data }) => {
        setUser(data);
        localStorage.setItem("iles_user", JSON.stringify(data));
      })
      .catch(() => logout())
      .finally(() => setCheckingSession(false));
  }, [token]);

  async function login(username, password) {
    const { data } = await api.post("auth/login/", { username, password });
    localStorage.setItem("iles_token", data.token);
    localStorage.setItem("iles_user", JSON.stringify(data.user));
    setToken(data.token);
    setUser(data.user);
  }

  function logout() {
    localStorage.removeItem("iles_token");
    localStorage.removeItem("iles_user");
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({ token, user, login, logout, checkingSession, isAuthenticated: Boolean(token) }),
    [token, user, checkingSession]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

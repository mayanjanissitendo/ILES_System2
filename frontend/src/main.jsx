import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Evaluations from "./pages/Evaluations.jsx";
import Login from "./pages/Login.jsx";
import Placements from "./pages/Placements.jsx";
import Reviews from "./pages/Reviews.jsx";
import WeeklyLogs from "./pages/WeeklyLogs.jsx";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/placements" element={<Placements />} />
              <Route path="/weekly-logs" element={<WeeklyLogs />} />
              <Route path="/reviews" element={<Reviews />} />
              <Route path="/evaluations" element={<Evaluations />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);

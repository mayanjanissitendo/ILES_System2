import { LogIn } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import loginInternshipImage from "../assets/login-internship.jpg";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(form.username, form.password);
      navigate("/dashboard");
    } catch {
      setError("Login failed. Check your username and password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-[#f7f8fb] lg:grid-cols-[1.05fr_0.95fr]">
      <section className="relative hidden overflow-hidden bg-cyan-700 lg:block">
        <img
          alt="Supervisor guiding interns during workplace training"
          className="h-full w-full object-cover opacity-90"
          src={loginInternshipImage}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/70 via-cyan-950/20 to-transparent" />
        <div className="absolute bottom-12 left-12 max-w-xl text-white">
          <p className="text-sm font-semibold uppercase tracking-wide text-cyan-100">Internship Logging & Evaluation System</p>
          <h1 className="mt-3 text-5xl font-bold leading-tight">ILES</h1>
          <p className="mt-4 text-lg text-cyan-50">Track placements, weekly logs, reviews, evaluations, and final scores in one workspace.</p>
        </div>
      </section>
      <section className="flex items-center justify-center px-5 py-10">
        <form className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm" onSubmit={handleSubmit}>
          <h2 className="text-2xl font-bold text-slate-950">Sign in</h2>
          <p className="mt-1 text-sm text-slate-500">Use your ILES account to continue.</p>
          <div className="mt-6 space-y-4">
            <label className="block">
              <span className="label">Username</span>
              <input className="field mt-1" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
            </label>
            <label className="block">
              <span className="label">Password</span>
              <input className="field mt-1" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            </label>
            {error && <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
            <button className="btn-primary w-full" disabled={loading} type="submit">
              <LogIn size={18} />
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

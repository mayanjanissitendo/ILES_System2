import { Send } from "lucide-react";
import { useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge.jsx";
import api from "../services/api.js";

const emptyForm = {
  placement: "",
  week_number: "",
  week_start_date: "",
  week_end_date: "",
  activities: "",
  skills_learned: "",
  challenges: "",
  hours_worked: ""
};

export default function WeeklyLogs() {
  const [logs, setLogs] = useState([]);
  const [placements, setPlacements] = useState([]);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    const [logResponse, placementResponse] = await Promise.all([api.get("weekly-logs/"), api.get("placements/")]);
    setLogs(logResponse.data);
    setPlacements(placementResponse.data);
  }

  async function save(event) {
    event.preventDefault();
    await api.post("weekly-logs/", form);
    setForm(emptyForm);
    load();
  }

  async function submitLog(id) {
    await api.post(`weekly-logs/${id}/submit/`);
    load();
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <form className="panel p-5" onSubmit={save}>
        <h2 className="text-xl font-bold">Weekly Logbook</h2>
        <div className="mt-5 grid gap-4">
          <label><span className="label">Placement</span><select className="field mt-1" value={form.placement} onChange={(e) => setForm({ ...form, placement: e.target.value })}><option value="">Select placement</option>{placements.map((placement) => <option key={placement.id} value={placement.id}>{placement.organization_name}</option>)}</select></label>
          <label><span className="label">Week number</span><input className="field mt-1" value={form.week_number} onChange={(e) => setForm({ ...form, week_number: e.target.value })} /></label>
          <div className="grid grid-cols-2 gap-3">
            <label><span className="label">Start</span><input className="field mt-1" type="date" value={form.week_start_date} onChange={(e) => setForm({ ...form, week_start_date: e.target.value })} /></label>
            <label><span className="label">End</span><input className="field mt-1" type="date" value={form.week_end_date} onChange={(e) => setForm({ ...form, week_end_date: e.target.value })} /></label>
          </div>
          <label><span className="label">Activities</span><textarea className="field mt-1 min-h-28" value={form.activities} onChange={(e) => setForm({ ...form, activities: e.target.value })} /></label>
          <label><span className="label">Skills learned</span><textarea className="field mt-1" value={form.skills_learned} onChange={(e) => setForm({ ...form, skills_learned: e.target.value })} /></label>
          <label><span className="label">Challenges</span><textarea className="field mt-1" value={form.challenges} onChange={(e) => setForm({ ...form, challenges: e.target.value })} /></label>
          <label><span className="label">Hours</span><input className="field mt-1" value={form.hours_worked} onChange={(e) => setForm({ ...form, hours_worked: e.target.value })} /></label>
          <button className="btn-primary" type="submit">Save Draft</button>
        </div>
      </form>
      <div className="panel p-5">
        <h2 className="text-xl font-bold">My Logs</h2>
        <div className="mt-4 grid gap-3">
          {logs.map((log) => (
            <article className="rounded-lg border border-slate-200 p-4" key={log.id}>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="font-semibold">Week {log.week_number}</h3>
                  <p className="text-sm text-slate-500">{log.week_start_date} to {log.week_end_date}</p>
                </div>
                <StatusBadge status={log.status} />
              </div>
              <p className="mt-3 text-sm text-slate-600">{log.activities}</p>
              {log.status === "draft" && <button className="btn-secondary mt-4" onClick={() => submitLog(log.id)} type="button"><Send size={16} />Submit</button>}
            </article>
          ))}
          {!logs.length && <p className="py-8 text-center text-slate-500">No weekly logs yet.</p>}
        </div>
      </div>
    </section>
  );
}

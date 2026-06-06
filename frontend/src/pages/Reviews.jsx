import { CheckCircle2, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge.jsx";
import api from "../services/api.js";

export default function Reviews() {
  const [logs, setLogs] = useState([]);
  const [comments, setComments] = useState({});

  useEffect(() => {
    load();
  }, []);

  async function load() {
    const { data } = await api.get("dashboards/pending-reviews/");
    setLogs(data);
  }

  async function review(id, status) {
    await api.post(`weekly-logs/${id}/review/`, { status, comments: comments[id] || "" });
    load();
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Supervisor Reviews</h2>
        <p className="mt-1 text-sm text-slate-500">Review submitted weekly logs and add supervisor comments.</p>
      </div>
      <div className="grid gap-4">
        {logs.map((log) => (
          <article className="panel p-5" key={log.id}>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-semibold">Week {log.week_number} - {log.student_name}</h3>
                <p className="text-sm text-slate-500">{log.organization_name}</p>
              </div>
              <StatusBadge status={log.status} />
            </div>
            <p className="mt-3 text-sm text-slate-700">{log.activities}</p>
            <textarea className="field mt-4 min-h-24" placeholder="Review comments" value={comments[log.id] || ""} onChange={(e) => setComments({ ...comments, [log.id]: e.target.value })} />
            <div className="mt-4 flex flex-wrap gap-3">
              <button className="btn-primary" onClick={() => review(log.id, "approved")} type="button"><CheckCircle2 size={16} />Approve</button>
              <button className="btn-secondary" onClick={() => review(log.id, "reviewed")} type="button">Mark Reviewed</button>
              <button className="btn-secondary" onClick={() => review(log.id, "rejected")} type="button"><XCircle size={16} />Reject</button>
            </div>
          </article>
        ))}
        {!logs.length && <p className="panel p-8 text-center text-slate-500">No pending reviews.</p>}
      </div>
    </section>
  );
}

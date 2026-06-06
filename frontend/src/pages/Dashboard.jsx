import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { useEffect, useState } from "react";
import MetricCard from "../components/MetricCard.jsx";
import api from "../services/api.js";

const colors = ["#0891b2", "#10b981", "#f59e0b", "#e11d48"];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [scores, setScores] = useState([]);

  useEffect(() => {
    Promise.all([api.get("dashboards/"), api.get("dashboards/scores/")])
      .then(([summaryResponse, scoreResponse]) => {
        setSummary(summaryResponse.data);
        setScores(scoreResponse.data);
      })
      .catch(() => {
        setSummary({ placements: 0, active_placements: 0, pending_reviews: 0, approved_logs: 0, average_score: 0 });
      });
  }, []);

  const chartData = [
    { name: "Active placements", value: summary?.active_placements || 0 },
    { name: "Pending reviews", value: summary?.pending_reviews || 0 },
    { name: "Approved logs", value: summary?.approved_logs || 0 }
  ];

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-950">Dashboard</h2>
        <p className="mt-1 text-sm text-slate-500">Progress, reviews, and scores across internship activity.</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Placements" value={summary?.placements} />
        <MetricCard label="Active" value={summary?.active_placements} tone="emerald" />
        <MetricCard label="Pending Reviews" value={summary?.pending_reviews} tone="amber" />
        <MetricCard label="Average Score" value={summary?.average_score || 0} tone="rose" />
      </div>
      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="panel p-5">
          <h3 className="font-semibold text-slate-950">Workflow Overview</h3>
          <div className="mt-4 h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={96}>
                  {chartData.map((entry, index) => (
                    <Cell key={entry.name} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="panel p-5">
          <h3 className="font-semibold text-slate-950">Score Breakdown</h3>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr>
                  <th className="py-2">Student</th>
                  <th>Workplace</th>
                  <th>Academic</th>
                  <th>Logbook</th>
                  <th>Final</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {scores.map((score) => (
                  <tr key={score.placement_id}>
                    <td className="py-3 font-medium">{score.student?.full_name || score.student?.username}</td>
                    <td>{score.workplace_average}</td>
                    <td>{score.academic_average}</td>
                    <td>{score.logbook_average}</td>
                    <td className="font-bold text-cyan-700">{score.final_score}</td>
                  </tr>
                ))}
                {!scores.length && (
                  <tr>
                    <td className="py-8 text-center text-slate-500" colSpan="5">No score data yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}

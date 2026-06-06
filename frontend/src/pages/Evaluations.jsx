import { Star } from "lucide-react";
import { useEffect, useState } from "react";
import api from "../services/api.js";

const emptyForm = { placement: "", evaluator: "", evaluation_type: "workplace", criteria: "", score: "", comments: "" };

export default function Evaluations() {
  const [placements, setPlacements] = useState([]);
  const [criteria, setCriteria] = useState([]);
  const [users, setUsers] = useState([]);
  const [evaluations, setEvaluations] = useState([]);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    const [placementResponse, criteriaResponse, userResponse, evaluationResponse] = await Promise.all([
      api.get("placements/"),
      api.get("evaluation-criteria/"),
      api.get("users/"),
      api.get("evaluations/")
    ]);
    setPlacements(placementResponse.data);
    setCriteria(criteriaResponse.data);
    setUsers(userResponse.data);
    setEvaluations(evaluationResponse.data);
  }

  async function save(event) {
    event.preventDefault();
    await api.post("evaluations/", form);
    setForm(emptyForm);
    load();
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <form className="panel p-5" onSubmit={save}>
        <h2 className="text-xl font-bold">Evaluation</h2>
        <div className="mt-5 grid gap-4">
          <Select label="Placement" value={form.placement} options={placements.map((p) => ({ id: p.id, name: p.organization_name }))} onChange={(value) => setForm({ ...form, placement: value })} />
          <Select label="Evaluator" value={form.evaluator} options={users.filter((u) => u.role !== "student").map((u) => ({ id: u.id, name: u.full_name || u.username }))} onChange={(value) => setForm({ ...form, evaluator: value })} />
          <label><span className="label">Type</span><select className="field mt-1" value={form.evaluation_type} onChange={(e) => setForm({ ...form, evaluation_type: e.target.value })}><option value="workplace">Workplace</option><option value="academic">Academic</option><option value="logbook">Logbook</option></select></label>
          <Select label="Criteria" value={form.criteria} options={criteria.filter((c) => c.category === form.evaluation_type).map((c) => ({ id: c.id, name: c.name }))} onChange={(value) => setForm({ ...form, criteria: value })} />
          <label><span className="label">Score</span><input className="field mt-1" value={form.score} onChange={(e) => setForm({ ...form, score: e.target.value })} /></label>
          <label><span className="label">Comments</span><textarea className="field mt-1" value={form.comments} onChange={(e) => setForm({ ...form, comments: e.target.value })} /></label>
          <button className="btn-primary" type="submit"><Star size={16} />Save Evaluation</button>
        </div>
      </form>
      <div className="panel p-5">
        <h2 className="text-xl font-bold">Scores</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[620px] text-left text-sm">
            <thead className="text-xs uppercase text-slate-500"><tr><th className="py-2">Type</th><th>Score</th><th>Weighted</th><th>Evaluator</th><th>Comments</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {evaluations.map((evaluation) => (
                <tr key={evaluation.id}>
                  <td className="py-3 capitalize">{evaluation.evaluation_type}</td>
                  <td>{evaluation.score}</td>
                  <td className="font-bold text-cyan-700">{evaluation.weighted_score}</td>
                  <td>{evaluation.evaluator_detail?.full_name || evaluation.evaluator_detail?.username}</td>
                  <td>{evaluation.comments}</td>
                </tr>
              ))}
              {!evaluations.length && <tr><td className="py-8 text-center text-slate-500" colSpan="5">No evaluations yet.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function Select({ label, value, options, onChange }) {
  return (
    <label className="block">
      <span className="label">{label}</span>
      <select className="field mt-1" value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Select</option>
        {options.map((option) => <option key={option.id} value={option.id}>{option.name}</option>)}
      </select>
    </label>
  );
}

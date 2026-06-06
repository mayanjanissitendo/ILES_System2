import { Plus } from "lucide-react";
import { useEffect, useState } from "react";
import api from "../services/api.js";

const emptyForm = {
  student: "",
  workplace_supervisor: "",
  academic_supervisor: "",
  organization_name: "",
  organization_address: "",
  department: "",
  position_title: "",
  start_date: "",
  end_date: ""
};

export default function Placements() {
  const [placements, setPlacements] = useState([]);
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");

  useEffect(() => {
    load();
  }, []);

  async function load() {
    const [placementResponse, userResponse] = await Promise.all([api.get("placements/"), api.get("users/")]);
    setPlacements(placementResponse.data);
    setUsers(userResponse.data);
  }

  async function submit(event) {
    event.preventDefault();
    setMessage("");
    try {
      await api.post("placements/", form);
      setForm(emptyForm);
      setMessage("Placement saved.");
      load();
    } catch {
      setMessage("Could not save placement. Check required fields and date overlap.");
    }
  }

  const students = users.filter((user) => user.role === "student");
  const workplaceSupervisors = users.filter((user) => user.role === "workplace_supervisor");
  const academicSupervisors = users.filter((user) => user.role === "academic_supervisor");

  return (
    <section className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <form className="panel p-5" onSubmit={submit}>
        <h2 className="text-xl font-bold">New Placement</h2>
        <div className="mt-5 grid gap-4">
          <Select label="Student" value={form.student} options={students} onChange={(value) => setForm({ ...form, student: value })} />
          <Select label="Workplace Supervisor" value={form.workplace_supervisor} options={workplaceSupervisors} onChange={(value) => setForm({ ...form, workplace_supervisor: value })} />
          <Select label="Academic Supervisor" value={form.academic_supervisor} options={academicSupervisors} onChange={(value) => setForm({ ...form, academic_supervisor: value })} />
          <Input label="Organization" value={form.organization_name} onChange={(value) => setForm({ ...form, organization_name: value })} />
          <Input label="Address" value={form.organization_address} onChange={(value) => setForm({ ...form, organization_address: value })} />
          <Input label="Department" value={form.department} onChange={(value) => setForm({ ...form, department: value })} />
          <Input label="Position" value={form.position_title} onChange={(value) => setForm({ ...form, position_title: value })} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Start" type="date" value={form.start_date} onChange={(value) => setForm({ ...form, start_date: value })} />
            <Input label="End" type="date" value={form.end_date} onChange={(value) => setForm({ ...form, end_date: value })} />
          </div>
          {message && <p className="text-sm text-slate-600">{message}</p>}
          <button className="btn-primary" type="submit"><Plus size={16} />Save Placement</button>
        </div>
      </form>
      <div className="panel p-5">
        <h2 className="text-xl font-bold">Placements</h2>
        <div className="mt-4 grid gap-3">
          {placements.map((placement) => (
            <article className="rounded-lg border border-slate-200 p-4" key={placement.id}>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="font-semibold">{placement.organization_name}</h3>
                  <p className="text-sm text-slate-500">{placement.student_detail?.full_name || placement.student_detail?.username}</p>
                </div>
                <p className="text-sm font-medium text-cyan-700">{placement.start_date} to {placement.end_date}</p>
              </div>
              <p className="mt-2 text-sm text-slate-600">{placement.position_title} {placement.department && `in ${placement.department}`}</p>
            </article>
          ))}
          {!placements.length && <p className="py-8 text-center text-slate-500">No placements yet.</p>}
        </div>
      </div>
    </section>
  );
}

function Input({ label, value, onChange, type = "text" }) {
  return <label className="block"><span className="label">{label}</span><input className="field mt-1" type={type} value={value} onChange={(event) => onChange(event.target.value)} /></label>;
}

function Select({ label, value, options, onChange }) {
  return (
    <label className="block">
      <span className="label">{label}</span>
      <select className="field mt-1" value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Select</option>
        {options.map((option) => <option key={option.id} value={option.id}>{option.full_name || option.username}</option>)}
      </select>
    </label>
  );
}

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getAllClients, createClient } from "../api/client";

export function Clients() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "", instantly_api_key: "" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const { data: clients = [], isLoading } = useQuery({
    queryKey: ["all-clients"],
    queryFn: getAllClients,
  });

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await createClient(form);
      queryClient.invalidateQueries({ queryKey: ["all-clients"] });
      setShowModal(false);
      setForm({ name: "", email: "", password: "", instantly_api_key: "" });
    } catch {
      setError("Failed to create client. Email may already be in use.");
    } finally {
      setSaving(false);
    }
  }

  const inputClass = "w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Clients</h1>
        <button onClick={() => setShowModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors">
          + Add Client
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100">
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Name</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Email</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Joined</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr><td colSpan={4} className="text-center py-8 text-slate-400 text-sm">Loading...</td></tr>
            )}
            {!isLoading && clients.length === 0 && (
              <tr><td colSpan={4} className="text-center py-8 text-slate-400 text-sm">No clients yet</td></tr>
            )}
            {clients.map((c: any) => (
              <tr key={c.id} className="border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors">
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center text-xs font-bold text-indigo-600">
                      {c.name?.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase()}
                    </div>
                    <span className="text-sm font-medium text-slate-900">{c.name}</span>
                  </div>
                </td>
                <td className="px-5 py-3.5 text-sm text-slate-500">{c.email}</td>
                <td className="px-5 py-3.5">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${c.is_active ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                    {c.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-xs text-slate-400">
                  {c.created_at ? new Date(c.created_at).toLocaleDateString() : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add client modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
            <h2 className="text-base font-semibold text-slate-900 mb-4">Add New Client</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div><label className="block text-xs font-medium text-slate-500 mb-1">Name</label>
                <input className={inputClass} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required /></div>
              <div><label className="block text-xs font-medium text-slate-500 mb-1">Email</label>
                <input type="email" className={inputClass} value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required /></div>
              <div><label className="block text-xs font-medium text-slate-500 mb-1">Password</label>
                <input type="password" className={inputClass} value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required /></div>
              <div><label className="block text-xs font-medium text-slate-500 mb-1">Instantly API Key (optional)</label>
                <input className={inputClass} value={form.instantly_api_key} onChange={e => setForm({ ...form, instantly_api_key: e.target.value })} /></div>
              {error && <p className="text-red-600 text-xs">{error}</p>}
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  {saving ? "Creating..." : "Create Client"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

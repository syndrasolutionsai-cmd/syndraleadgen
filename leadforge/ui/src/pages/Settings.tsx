import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getCurrentUser, updateCurrentUser } from "../api/client";

function MaskedInput({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  const [show, setShow] = useState(false);
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">{label}</label>
      <div className="relative">
        <input
          type={show ? "text" : "password"}
          className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 pr-16"
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder="Not set"
        />
        <button type="button" onClick={() => setShow(!show)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-600">
          {show ? "Hide" : "Show"}
        </button>
      </div>
    </div>
  );
}

export function Settings() {
  const queryClient = useQueryClient();
  const { data: me } = useQuery({ queryKey: ["me"], queryFn: getCurrentUser });
  const [instantlyKey, setInstantlyKey] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    await updateCurrentUser({ instantly_api_key: instantlyKey });
    queryClient.invalidateQueries({ queryKey: ["me"] });
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Settings</h1>

      {/* Account */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 mb-5">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Account</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Name</p>
            <p className="text-sm text-slate-800 font-medium">{me?.name || "—"}</p>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Email</p>
            <p className="text-sm text-slate-800 font-medium">{me?.email || "—"}</p>
          </div>
        </div>
      </div>

      {/* API Keys */}
      <form onSubmit={handleSave} className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">API Keys</h2>
        <div className="space-y-4">
          <MaskedInput label="Instantly API Key" value={instantlyKey} onChange={setInstantlyKey} />
          <p className="text-xs text-slate-400">Other API keys (Anthropic, Apify, Hunter, ZeroBounce) are set in the server <code className="bg-slate-100 px-1 rounded">.env</code> file.</p>
        </div>
        <div className="flex items-center gap-3 mt-5">
          <button type="submit" disabled={saving}
            className="px-5 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {saving ? "Saving..." : "Save Changes"}
          </button>
          {saved && <span className="text-xs text-emerald-600 font-medium">✓ Saved</span>}
        </div>
      </form>
    </div>
  );
}

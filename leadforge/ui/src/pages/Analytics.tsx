import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listCampaigns, getCampaignAnalytics } from "../api/client";
import { MetricsChart } from "../components/MetricsChart";
import { PipelineStatus } from "../components/PipelineStatus";

export function Analytics() {
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);

  const { data: campaigns = [] } = useQuery({ queryKey: ["campaigns"], queryFn: listCampaigns });
  const { data: stats } = useQuery({
    queryKey: ["campaign-analytics", selectedCampaign],
    queryFn: () => getCampaignAnalytics(selectedCampaign!),
    enabled: !!selectedCampaign,
  });

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>
        <select
          className="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={selectedCampaign || ""}
          onChange={e => setSelectedCampaign(e.target.value || null)}
        >
          <option value="">Select campaign...</option>
          {campaigns.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {!selectedCampaign && (
        <div className="text-center py-16 text-slate-400">
          <p className="text-4xl mb-3">📊</p>
          <p className="text-sm">Select a campaign to see its analytics</p>
        </div>
      )}

      {stats && (
        <>
          <div className="flex items-center gap-3 mb-6">
            <h2 className="text-base font-semibold text-slate-800">{stats.name}</h2>
            <PipelineStatus status={stats.pipeline_status} />
          </div>

          <div className="grid grid-cols-4 gap-4 mb-6">
            {[
              { label: "Total Emails", value: stats.total_emails },
              { label: "Approved", value: stats.approved, color: "text-emerald-600" },
              { label: "Pending Review", value: stats.pending_review, color: "text-amber-500" },
              { label: "Avg Quality Score", value: stats.avg_quality_score, color: "text-blue-600" },
            ].map(s => (
              <div key={s.label} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">{s.label}</p>
                <p className={`text-3xl font-bold ${s.color || "text-slate-900"}`}>{s.value ?? "—"}</p>
              </div>
            ))}
          </div>

          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 mb-6">
            <p className="text-sm font-semibold text-slate-900 mb-4">Open & Reply Rate Over Time</p>
            <MetricsChart data={[]} />
            <p className="text-xs text-slate-400 mt-3">Open/reply rate data populates after Instantly sends emails and the daily metrics poller runs.</p>
          </div>
        </>
      )}
    </div>
  );
}

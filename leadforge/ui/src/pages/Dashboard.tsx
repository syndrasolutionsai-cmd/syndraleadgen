import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { listCampaigns, getAnalyticsSummary } from "../api/client";
import { PipelineStatus } from "../components/PipelineStatus";
import { MetricsChart } from "../components/MetricsChart";

function StatCard({ label, value, sub, subColor = "text-emerald-600" }: {
  label: string; value: string | number; sub?: string; subColor?: string;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">{label}</p>
      <p className="text-3xl font-bold text-slate-900 mb-1">{value}</p>
      {sub && <p className={`text-xs ${subColor}`}>{sub}</p>}
    </div>
  );
}

export function Dashboard() {
  const navigate = useNavigate();

  const { data: campaigns = [] } = useQuery({
    queryKey: ["campaigns"],
    queryFn: listCampaigns,
    refetchInterval: 5000,
  });

  const { data: summary } = useQuery({
    queryKey: ["analytics-summary"],
    queryFn: getAnalyticsSummary,
    refetchInterval: 10000,
  });

  const activeCount = campaigns.filter((c: any) => c.pipeline_status !== "done" && c.pipeline_status !== "idle").length;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            {new Date().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
          </p>
        </div>
        <button
          onClick={() => navigate("/campaigns/new")}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <span>+</span> New Campaign
        </button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Active Campaigns" value={campaigns.filter((c: any) => c.is_active).length} sub={activeCount > 0 ? `${activeCount} running now` : "None running"} />
        <StatCard label="Emails Sent" value={summary?.emails_sent ?? "—"} sub="↑ across all campaigns" />
        <StatCard label="Avg Open Rate" value={summary?.avg_open_rate ? `${summary.avg_open_rate}%` : "—"} sub="From Instantly" />
        <StatCard label="Pending Review" value={summary?.pending_review ?? "—"} sub="Need your attention" subColor="text-amber-500" />
      </div>

      {/* Campaigns list */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm mb-6">
        <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-900">Campaigns</span>
          <button onClick={() => navigate("/campaigns/new")} className="text-xs text-blue-600 hover:underline">+ New</button>
        </div>
        {campaigns.length === 0 ? (
          <div className="py-12 text-center text-slate-400">
            <p className="text-sm">No campaigns yet.</p>
            <button onClick={() => navigate("/campaigns/new")} className="mt-2 text-blue-600 text-sm hover:underline">Create your first campaign →</button>
          </div>
        ) : (
          campaigns.map((c: any) => (
            <div key={c.id} className="px-5 py-4 border-b border-slate-50 last:border-0 flex items-center gap-4">
              <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-base flex-shrink-0">
                🎯
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-900 truncate">{c.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="bg-slate-100 rounded-full h-1.5 w-32 overflow-hidden">
                    <div className="bg-blue-500 h-full rounded-full" style={{ width: "60%" }} />
                  </div>
                  <span className="text-xs text-slate-400">{c.batch_size} prospects</span>
                </div>
              </div>
              <PipelineStatus status={c.pipeline_status || "idle"} />
            </div>
          ))
        )}
      </div>

      {/* Metrics chart */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">
        <p className="text-sm font-semibold text-slate-900 mb-4">Email Performance</p>
        <MetricsChart data={[]} />
      </div>
    </div>
  );
}

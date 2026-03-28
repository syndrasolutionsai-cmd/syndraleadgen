import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { listCampaigns, getReviewQueue } from "../api/client";
import { ProspectCard } from "../components/ProspectCard";

export function ReviewQueue() {
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: campaigns = [] } = useQuery({
    queryKey: ["campaigns"],
    queryFn: listCampaigns,
  });

  const { data: queue = [], isLoading } = useQuery({
    queryKey: ["review-queue", selectedCampaign],
    queryFn: () => getReviewQueue(selectedCampaign!),
    enabled: !!selectedCampaign,
    refetchInterval: 15000,
  });

  function onAction() {
    queryClient.invalidateQueries({ queryKey: ["review-queue", selectedCampaign] });
    queryClient.invalidateQueries({ queryKey: ["analytics-summary"] });
  }

  // Auto-expand first card when queue loads
  const firstId = (queue[0] as any)?.email_id;
  const activeId = expandedId ?? firstId ?? null;

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Review Queue</h1>
          {queue.length > 0 && (
            <p className="text-sm text-slate-400 mt-1">{queue.length} email{queue.length !== 1 ? "s" : ""} pending review</p>
          )}
        </div>
        <select
          className="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={selectedCampaign || ""}
          onChange={e => { setSelectedCampaign(e.target.value || null); setExpandedId(null); }}
        >
          <option value="">Select campaign...</option>
          {campaigns.map((c: any) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {!selectedCampaign && (
        <div className="text-center py-16 text-slate-400">
          <p className="text-4xl mb-3">📬</p>
          <p className="text-sm">Select a campaign above to see its review queue</p>
        </div>
      )}

      {isLoading && <p className="text-sm text-slate-400">Loading...</p>}

      {!isLoading && selectedCampaign && queue.length === 0 && (
        <div className="text-center py-16 text-slate-400">
          <p className="text-4xl mb-3">✅</p>
          <p className="text-sm font-medium text-slate-600">All caught up!</p>
          <p className="text-xs mt-1">No emails pending review for this campaign</p>
        </div>
      )}

      <div className="space-y-3">
        {(queue as any[]).map((item: any) => {
          const isExpanded = item.email_id === activeId;
          if (isExpanded) {
            return (
              <ProspectCard
                key={item.email_id}
                emailId={item.email_id}
                prospectName={item.prospect_name}
                company={item.company}
                role={item.role}
                emailAddress={item.email_address}
                subject={item.subject}
                body={item.body}
                icebreaker={item.icebreaker}
                signalType={item.signal_type}
                signalText={item.signal_text}
                qualityScore={item.quality_score}
                onAction={onAction}
              />
            );
          }
          // Collapsed row
          return (
            <button key={item.email_id} onClick={() => setExpandedId(item.email_id)}
              className="w-full bg-white border border-slate-200 rounded-xl px-5 py-3.5 flex items-center gap-4 hover:border-blue-300 transition-colors text-left shadow-sm">
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500 flex-shrink-0">
                {item.prospect_name?.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-900">{item.prospect_name}</p>
                <p className="text-xs text-slate-400 truncate">{item.role} · {item.company}</p>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                <span className={`text-xs font-bold ${item.quality_score >= 85 ? "text-emerald-600" : item.quality_score >= 70 ? "text-amber-500" : "text-red-500"}`}>
                  {item.quality_score}
                </span>
                <svg className="w-4 h-4 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path d="M9 18l6-6-6-6"/>
                </svg>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { listCampaigns, getReviewQueue } from "../api/client";
import { ProspectCard } from "../components/ProspectCard";

export function ReviewQueue() {
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: campaigns = [] } = useQuery({
    queryKey: ["campaigns"],
    queryFn: listCampaigns,
  });

  const { data: queue = [], isLoading } = useQuery({
    queryKey: ["review-queue", selectedCampaign],
    queryFn: () => getReviewQueue(selectedCampaign!),
    enabled: !!selectedCampaign,
  });

  function onAction() {
    queryClient.invalidateQueries({ queryKey: ["review-queue", selectedCampaign] });
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Review Queue</h1>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Campaign</label>
        <select
          className="border rounded px-3 py-2 w-full max-w-xs"
          value={selectedCampaign || ""}
          onChange={e => setSelectedCampaign(e.target.value || null)}
        >
          <option value="">Select a campaign...</option>
          {campaigns.map((c: any) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {isLoading && <p className="text-gray-500">Loading review queue...</p>}

      {!isLoading && selectedCampaign && queue.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg">No emails pending review</p>
          <p className="text-sm mt-1">All emails have been reviewed or no campaign has been run yet.</p>
        </div>
      )}

      <div className="space-y-6">
        {queue.map((item: any) => (
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
        ))}
      </div>
    </div>
  );
}

import { useState } from "react";
import { approveEmail, rejectEmail, editAndApproveEmail } from "../api/client";

interface ProspectCardProps {
  emailId: string; prospectName: string; company: string; role: string | null;
  emailAddress: string; subject: string; body: string; icebreaker: string;
  signalType: string; signalText: string; qualityScore: number; onAction: () => void;
}

export function ProspectCard({
  emailId, prospectName, company, role, emailAddress,
  subject, body, icebreaker, signalType, signalText, qualityScore, onAction,
}: ProspectCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editSubject, setEditSubject] = useState(subject);
  const [editBody, setEditBody] = useState(body);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState<"approved" | "rejected" | null>(null);

  const scoreColor = qualityScore >= 85 ? "text-emerald-600 bg-emerald-50" : qualityScore >= 70 ? "text-amber-600 bg-amber-50" : "text-red-600 bg-red-50";
  const initials = prospectName?.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();

  async function handleApprove() {
    setLoading(true);
    await approveEmail(emailId);
    setDone("approved");
    setTimeout(onAction, 600);
  }

  async function handleReject() {
    setLoading(true);
    await rejectEmail(emailId);
    setDone("rejected");
    setTimeout(onAction, 600);
  }

  async function handleEditSave() {
    setLoading(true);
    await editAndApproveEmail(emailId, editSubject, editBody);
    setDone("approved");
    setTimeout(onAction, 600);
  }

  if (done) {
    return (
      <div className={`bg-white border rounded-xl px-5 py-4 shadow-sm flex items-center gap-3 ${done === "approved" ? "border-emerald-200 bg-emerald-50" : "border-red-100 bg-red-50"}`}>
        <span className="text-lg">{done === "approved" ? "✅" : "🗑"}</span>
        <span className="text-sm font-medium text-slate-600">{prospectName} — {done === "approved" ? "Approved" : "Rejected"}</span>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-4">
        <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-sm font-bold text-blue-600 flex-shrink-0">
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-900">{prospectName}</p>
          <p className="text-xs text-slate-400">{role} · {company} · {emailAddress}</p>
        </div>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${scoreColor}`}>
          Score: {qualityScore}
        </span>
      </div>

      {/* Signal */}
      <div className="px-5 py-3 bg-blue-50 border-b border-blue-100">
        <span className="text-xs font-semibold text-blue-700">Signal ({signalType}): </span>
        <span className="text-xs text-blue-600 italic">"{signalText}"</span>
      </div>

      {/* Email content */}
      <div className="px-5 py-4">
        {isEditing ? (
          <div className="space-y-3">
            <input className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={editSubject} onChange={e => setEditSubject(e.target.value)} placeholder="Subject" />
            <textarea className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm h-40 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={editBody} onChange={e => setEditBody(e.target.value)} />
            <div className="flex gap-2">
              <button onClick={handleEditSave} disabled={loading}
                className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50">
                Save & Approve
              </button>
              <button onClick={() => setIsEditing(false)}
                className="bg-slate-100 text-slate-600 px-4 py-2 rounded-lg text-sm hover:bg-slate-200">
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Subject</p>
            <p className="text-sm font-medium text-slate-800 mb-3">{subject}</p>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Body</p>
            <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{body}</p>
          </>
        )}
      </div>

      {/* Actions */}
      {!isEditing && (
        <div className="px-5 py-3.5 border-t border-slate-100 flex gap-2">
          <button onClick={handleApprove} disabled={loading}
            className="flex-1 bg-emerald-600 text-white py-2 rounded-lg text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors">
            ✓ Approve
          </button>
          <button onClick={() => setIsEditing(true)}
            className="flex-1 bg-blue-50 text-blue-700 py-2 rounded-lg text-sm font-semibold hover:bg-blue-100 transition-colors border border-blue-100">
            ✏ Edit
          </button>
          <button onClick={handleReject} disabled={loading}
            className="flex-1 bg-red-50 text-red-600 py-2 rounded-lg text-sm font-semibold hover:bg-red-100 transition-colors border border-red-100">
            ✕ Reject
          </button>
        </div>
      )}
    </div>
  );
}

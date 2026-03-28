import { useState } from "react";
import { approveEmail, rejectEmail, editAndApproveEmail } from "../api/client";

interface ProspectCardProps {
  emailId: string;
  prospectName: string;
  company: string;
  role: string | null;
  emailAddress: string;
  subject: string;
  body: string;
  icebreaker: string;
  signalType: string;
  signalText: string;
  qualityScore: number;
  onAction: () => void;
}

export function ProspectCard({
  emailId, prospectName, company, role, emailAddress,
  subject, body, icebreaker, signalType, signalText,
  qualityScore, onAction,
}: ProspectCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editSubject, setEditSubject] = useState(subject);
  const [editBody, setEditBody] = useState(body);
  const [loading, setLoading] = useState(false);

  const scoreColor = qualityScore >= 85 ? "text-green-600" : qualityScore >= 70 ? "text-yellow-600" : "text-red-600";

  async function handleApprove() {
    setLoading(true);
    await approveEmail(emailId);
    onAction();
  }

  async function handleReject() {
    setLoading(true);
    await rejectEmail(emailId);
    onAction();
  }

  async function handleEditSave() {
    setLoading(true);
    await editAndApproveEmail(emailId, editSubject, editBody);
    onAction();
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 text-lg">{prospectName}</h3>
          <p className="text-gray-500 text-sm">{role} @ {company}</p>
          <p className="text-gray-400 text-xs">{emailAddress}</p>
        </div>
        <div className="text-right">
          <span className={`font-bold text-2xl ${scoreColor}`}>{qualityScore}</span>
          <p className="text-gray-400 text-xs">quality score</p>
        </div>
      </div>

      <div className="bg-blue-50 rounded p-3 mb-4 text-sm">
        <span className="font-medium text-blue-700">Signal ({signalType}):</span>
        <p className="text-blue-600 mt-1 italic">"{signalText}"</p>
      </div>

      {isEditing ? (
        <div className="space-y-3">
          <input
            className="w-full border rounded px-3 py-2 text-sm"
            value={editSubject}
            onChange={e => setEditSubject(e.target.value)}
            placeholder="Subject"
          />
          <textarea
            className="w-full border rounded px-3 py-2 text-sm h-40"
            value={editBody}
            onChange={e => setEditBody(e.target.value)}
          />
          <div className="flex gap-2">
            <button onClick={handleEditSave} disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50">
              Save & Approve
            </button>
            <button onClick={() => setIsEditing(false)}
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-300">
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-gray-50 rounded p-4 mb-4">
            <p className="text-xs font-medium text-gray-500 mb-1">SUBJECT: {subject}</p>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{body}</p>
          </div>
          <div className="flex gap-2">
            <button onClick={handleApprove} disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50">
              Approve
            </button>
            <button onClick={() => setIsEditing(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700">
              Edit
            </button>
            <button onClick={handleReject} disabled={loading}
              className="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700 disabled:opacity-50">
              Reject
            </button>
          </div>
        </>
      )}
    </div>
  );
}

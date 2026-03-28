const STEP_LABELS: Record<string, string> = {
  idle: "Not started",
  scraping: "Scraping leads...",
  verifying: "Verifying emails...",
  personalizing: "Writing emails...",
  saving: "Saving to queue...",
  done: "Complete",
  failed: "Failed",
};
const STEP_COLORS: Record<string, string> = {
  idle: "bg-slate-100 text-slate-500",
  scraping: "bg-blue-100 text-blue-700",
  verifying: "bg-indigo-100 text-indigo-700",
  personalizing: "bg-violet-100 text-violet-700",
  saving: "bg-cyan-100 text-cyan-700",
  done: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export function PipelineStatus({ status }: { status: string }) {
  const isRunning = status !== "idle" && status !== "done" && status !== "failed";
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${STEP_COLORS[status] || STEP_COLORS.idle}`}>
      {isRunning && (
        <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
      )}
      {STEP_LABELS[status] || status}
    </span>
  );
}

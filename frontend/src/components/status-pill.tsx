import { cn, statusLabel } from "@/lib/utils";

const toneByStatus: Record<string, string> = {
  active: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  archived: "bg-gray-50 text-gray-600 ring-gray-200",
  blocked: "bg-red-50 text-red-700 ring-red-200",
  declined: "bg-red-50 text-red-700 ring-red-200",
  deadline: "bg-amber-50 text-amber-700 ring-amber-200",
  done: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  document: "bg-sky-50 text-sky-700 ring-sky-200",
  draft: "bg-amber-50 text-amber-700 ring-amber-200",
  in_application: "bg-blue-50 text-blue-700 ring-blue-200",
  in_progress: "bg-blue-50 text-blue-700 ring-blue-200",
  needs_review: "bg-amber-50 text-amber-700 ring-amber-200",
  new: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  planned: "bg-sky-50 text-sky-700 ring-sky-200",
  processed: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  ready_to_submit: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  saved: "bg-sky-50 text-sky-700 ring-sky-200",
  skipped: "bg-gray-50 text-gray-600 ring-gray-200",
  submitted: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  todo: "bg-gray-50 text-gray-600 ring-gray-200",
  uploaded: "bg-sky-50 text-sky-700 ring-sky-200",
};

export function StatusPill({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex max-w-full items-center rounded px-2 py-1 text-xs font-medium ring-1 ring-inset",
        toneByStatus[status] ?? "bg-gray-50 text-gray-600 ring-gray-200",
      )}
    >
      <span className="truncate">{statusLabel(status)}</span>
    </span>
  );
}

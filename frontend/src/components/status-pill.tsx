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
  scanning: "bg-blue-50 text-blue-700 ring-blue-200",
  idle: "bg-gray-50 text-gray-600 ring-gray-200",
  completed: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  failed: "bg-red-50 text-red-700 ring-red-200",
  high: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  medium: "bg-amber-50 text-amber-700 ring-amber-200",
  low: "bg-gray-50 text-gray-600 ring-gray-200",
  professor: "bg-violet-50 text-violet-700 ring-violet-200",
  advisor: "bg-sky-50 text-sky-700 ring-sky-200",
  mentor: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  manager: "bg-blue-50 text-blue-700 ring-blue-200",
  simulated: "bg-sky-50 text-sky-700 ring-sky-200",
  scholarship_contact: "bg-amber-50 text-amber-700 ring-amber-200",
  program_director: "bg-violet-50 text-violet-700 ring-violet-200",
  department_head: "bg-blue-50 text-blue-700 ring-blue-200",
  recommendation_request: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  scholarship_inquiry: "bg-sky-50 text-sky-700 ring-sky-200",
  eligibility_question: "bg-amber-50 text-amber-700 ring-amber-200",
  follow_up: "bg-blue-50 text-blue-700 ring-blue-200",
  thank_you: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  draft_email: "bg-sky-50 text-sky-700 ring-sky-200",
  create_google_doc: "bg-violet-50 text-violet-700 ring-violet-200",
  create_calendar_reminder: "bg-amber-50 text-amber-700 ring-amber-200",
  save_document: "bg-blue-50 text-blue-700 ring-blue-200",
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

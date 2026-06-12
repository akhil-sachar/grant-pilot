"use client";

import { Loader2, Mail, Radio } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { generateApplicationOutreach, getComposioStatus } from "@/lib/api/client";
import type {
  ApplicationBundle,
  ComposioStatus,
  OutreachEmail,
  OutreachGenerateResult,
} from "@/lib/types";
import { statusLabel } from "@/lib/utils";

const RECIPIENT_ROLES = [
  { value: "professor", label: "Professor" },
  { value: "advisor", label: "Advisor" },
  { value: "scholarship_contact", label: "Scholarship Contact" },
  { value: "program_director", label: "Program Director" },
  { value: "department_head", label: "Department Head" },
] as const;

const EMAIL_TYPES = [
  { value: "recommendation_request", label: "Recommendation Request" },
  { value: "scholarship_inquiry", label: "Scholarship Inquiry" },
  { value: "eligibility_question", label: "Eligibility Question" },
  { value: "follow_up", label: "Follow-Up" },
  { value: "thank_you", label: "Thank You" },
] as const;

export function OutreachEditor({ initialBundle }: { initialBundle: ApplicationBundle }) {
  const [bundle, setBundle] = useState(initialBundle);
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);
  const [latestResult, setLatestResult] = useState<OutreachGenerateResult | null>(null);
  const [composioStatus, setComposioStatus] = useState<ComposioStatus | null>(null);
  const [recipientRole, setRecipientRole] =
    useState<(typeof RECIPIENT_ROLES)[number]["value"]>("professor");
  const [emailType, setEmailType] =
    useState<(typeof EMAIL_TYPES)[number]["value"]>("recommendation_request");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const emails = useMemo(
    () => [...bundle.outreach_emails].sort((a, b) => a.version_number - b.version_number),
    [bundle.outreach_emails],
  );
  const selected =
    emails.find((email) => email.id === selectedEmailId) ?? emails[emails.length - 1] ?? null;
  const composioActions = latestResult?.composio_actions ?? [];
  const suggestedFollowUp =
    latestResult?.suggested_follow_up ?? selected?.suggested_follow_up ?? "";

  useEffect(() => {
    void getComposioStatus().then(setComposioStatus).catch(() => null);
  }, []);

  async function handleGenerate() {
    setIsGenerating(true);
    setError(null);
    try {
      const result = await generateApplicationOutreach(bundle.application.id, {
        recipient_role: recipientRole,
        email_type: emailType,
      });
      setLatestResult(result);
      setBundle((current) => ({
        ...current,
        outreach_emails: [...current.outreach_emails, result.outreach_email],
      }));
      setSelectedEmailId(result.outreach_email.id);
      setComposioStatus({
        mode: result.composio_mode,
        api_key_configured: result.composio_mode === "live",
        connected_tools: ["gmail", "google_docs", "google_calendar", "google_drive"],
        message:
          result.composio_mode === "live"
            ? "Composio live mode enabled."
            : "Composio simulated mode active.",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Outreach generation failed");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <section className="mt-6 rounded-lg border border-line bg-panel shadow-soft">
      <div className="flex flex-col gap-4 border-b border-line px-5 py-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4 text-spruce" aria-hidden="true" />
            <h2 className="text-base font-semibold">Outreach editor</h2>
          </div>
          <p className="mt-1 text-sm text-muted">
            Generate personalized outreach emails and run Composio workflows for Gmail, Docs,
            Calendar, and Drive.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="text-sm">
            <span className="mb-1 block text-xs font-semibold uppercase text-muted">Recipient role</span>
            <select
              value={recipientRole}
              onChange={(event) =>
                setRecipientRole(event.target.value as typeof recipientRole)
              }
              className="rounded-md border border-line bg-white px-3 py-2 text-sm"
            >
              {RECIPIENT_ROLES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-xs font-semibold uppercase text-muted">Email type</span>
            <select
              value={emailType}
              onChange={(event) => setEmailType(event.target.value as typeof emailType)}
              className="rounded-md border border-line bg-white px-3 py-2 text-sm"
            >
              {EMAIL_TYPES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={() => void handleGenerate()}
            disabled={isGenerating}
            className="inline-flex items-center justify-center gap-2 rounded-md bg-spruce px-4 py-2 text-sm font-semibold text-white shadow-soft transition hover:bg-spruce/90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <Mail className="h-4 w-4" aria-hidden="true" />
            )}
            Generate Outreach Email
          </button>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 border-b border-line bg-canvas px-5 py-3">
        <Radio className="h-4 w-4 text-muted" aria-hidden="true" />
        <span className="text-sm font-medium">Composio</span>
        <StatusPill status={composioStatus?.mode === "live" ? "active" : "skipped"} />
        <span className="text-sm text-muted">
          {composioStatus?.mode === "live" ? "Live Mode" : "Simulated Mode"}
        </span>
        <span className="text-xs text-muted">{composioStatus?.message}</span>
      </div>

      {error ? <p className="px-5 pt-4 text-sm text-red-600">{error}</p> : null}

      {emails.length > 1 ? (
        <div className="border-b border-line px-5 py-3">
          <label className="text-xs font-semibold uppercase text-muted" htmlFor="outreach-version">
            Version history
          </label>
          <select
            id="outreach-version"
            value={selected?.id ?? ""}
            onChange={(event) => setSelectedEmailId(event.target.value)}
            className="mt-2 w-full max-w-md rounded-md border border-line bg-white px-3 py-2 text-sm"
          >
            {emails.map((email: OutreachEmail) => (
              <option key={email.id} value={email.id}>
                v{email.version_number} · {statusLabel(email.email_type)} · {email.recipient_email}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="border-b border-line p-5 lg:border-b-0 lg:border-r">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-semibold">Email draft</h3>
            {selected ? <StatusPill status={selected.status} /> : null}
            {selected ? <StatusPill status={selected.recipient_role} /> : null}
          </div>
          {selected ? (
            <p className="mb-3 text-sm font-medium text-ink">{selected.subject}</p>
          ) : null}
          <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-md border border-line bg-white p-4 text-sm leading-6 text-ink">
            {selected?.body ?? "Generate a personalized outreach email for this opportunity."}
          </pre>
        </div>
        <div className="grid gap-4 p-5">
          <div>
            <h3 className="text-sm font-semibold">Suggested follow-up</h3>
            <p className="mt-3 text-sm leading-6 text-muted">
              {suggestedFollowUp || "Follow-up guidance appears after generation."}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold">Composio action log</h3>
            {composioActions.length ? (
              <ul className="mt-3 space-y-2">
                {composioActions.map((action) => (
                  <li
                    key={`${action.action}-${action.provider}`}
                    className="rounded-md border border-line bg-canvas px-3 py-2 text-sm"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium">{statusLabel(action.action)}</span>
                      <StatusPill status={action.status} />
                    </div>
                    <p className="mt-1 text-xs text-muted">
                      {action.provider} · {action.mode} mode
                    </p>
                    <p className="mt-1 text-muted">{action.detail}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-3 text-sm text-muted">
                Gmail draft, Google Doc, calendar reminder, and Drive save actions log here.
              </p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

"use client";

import { Loader2, PlusCircle } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { createApplication } from "@/lib/api/client";
import type { MatchResult, Opportunity } from "@/lib/types";

export function CreateApplicationPanel({
  opportunities,
  matches,
  existingOpportunityIds,
}: {
  opportunities: Opportunity[];
  matches: MatchResult[];
  existingOpportunityIds: string[];
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [opportunityId, setOpportunityId] = useState("");
  const [notes, setNotes] = useState("");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const available = opportunities.filter(
    (item) => !existingOpportunityIds.includes(item.id),
  );

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    if (!opportunityId) {
      return;
    }
    setRunning(true);
    setError(null);
    try {
      const match = matches.find((item) => item.opportunity_id === opportunityId);
      const application = await createApplication({
        opportunity_id: opportunityId,
        match_result_id: match?.id ?? null,
        notes: notes.trim() || null,
      });
      setOpen(false);
      setOpportunityId("");
      setNotes("");
      router.push(`/applications/${application.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create application");
    } finally {
      setRunning(false);
    }
  }

  if (!available.length) {
    return (
      <section className="rounded-lg border border-dashed border-line bg-panel p-5 text-sm text-muted shadow-soft">
        All indexed opportunities already have application plans.
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-base font-semibold">Start a new application</h2>
          <p className="mt-1 text-sm text-muted">
            Create an application plan from a matched opportunity.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          className="inline-flex items-center gap-2 self-start rounded-md bg-spruce px-4 py-2 text-sm font-semibold text-white transition hover:bg-spruce/90"
        >
          <PlusCircle className="h-4 w-4" aria-hidden="true" />
          {open ? "Cancel" : "New application"}
        </button>
      </div>

      {open ? (
        <form onSubmit={(event) => void handleCreate(event)} className="mt-5 grid gap-4">
          <label className="grid gap-2 text-sm">
            <span className="font-medium">Opportunity</span>
            <select
              value={opportunityId}
              onChange={(event) => setOpportunityId(event.target.value)}
              required
              className="rounded-md border border-line bg-white px-3 py-2"
            >
              <option value="">Select an opportunity</option>
              {available.map((item) => {
                const match = matches.find((entry) => entry.opportunity_id === item.id);
                return (
                  <option key={item.id} value={item.id}>
                    {item.title}
                    {match ? ` · ${Math.round(match.score * 100)}% match` : ""}
                  </option>
                );
              })}
            </select>
          </label>
          <label className="grid gap-2 text-sm">
            <span className="font-medium">Notes (optional)</span>
            <textarea
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              rows={3}
              className="rounded-md border border-line bg-white px-3 py-2"
              placeholder="Strategy, deadlines, or materials to prioritize"
            />
          </label>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={running || !opportunityId}
              className="inline-flex items-center gap-2 rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink shadow-soft transition hover:border-spruce hover:text-spruce disabled:opacity-60"
            >
              {running ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Create application
            </button>
            {opportunityId ? (
              <Link href={`/opportunities`} className="text-sm text-spruce hover:underline">
                View opportunity details
              </Link>
            ) : null}
          </div>
        </form>
      ) : null}
    </section>
  );
}

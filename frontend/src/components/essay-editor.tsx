"use client";

import { Loader2, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { improveApplicationEssay } from "@/lib/api/client";
import type { ApplicationBundle, EssayImproveResult, EssayVersion } from "@/lib/types";

function originalVersion(versions: EssayVersion[]) {
  return (
    versions.find((version) => Boolean(version.metadata.is_original)) ??
    [...versions].sort((a, b) => a.version_number - b.version_number)[0]
  );
}

export function EssayEditor({ initialBundle }: { initialBundle: ApplicationBundle }) {
  const [bundle, setBundle] = useState(initialBundle);
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const [latestResult, setLatestResult] = useState<EssayImproveResult | null>(null);
  const [isImproving, setIsImproving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const versions = useMemo(
    () => [...bundle.essay_versions].sort((a, b) => a.version_number - b.version_number),
    [bundle.essay_versions],
  );
  const original = originalVersion(versions);
  const originalText = latestResult?.original_essay ?? original?.content ?? "";
  const revised =
    versions.find((version) => version.id === selectedVersionId) ??
    versions[versions.length - 1] ??
    null;
  const suggestions =
    latestResult?.improvement_suggestions ??
    revised?.feedback_notes ??
    [];
  const changeSummary = latestResult?.change_summary ?? revised?.change_summary ?? "";

  async function handleImprove() {
    setIsImproving(true);
    setError(null);
    try {
      const result = await improveApplicationEssay(bundle.application.id);
      setLatestResult(result);
      setBundle((current) => ({
        ...current,
        essay_versions: [...current.essay_versions, result.essay_version],
      }));
      setSelectedVersionId(result.essay_version.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Essay improvement failed");
    } finally {
      setIsImproving(false);
    }
  }

  return (
    <section className="rounded-lg border border-line bg-panel shadow-soft">
      <div className="flex flex-col gap-4 border-b border-line px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-base font-semibold">Essay editor</h2>
          <p className="mt-1 text-sm text-muted">
            Compare your original essay with opportunity-specific revisions. Original versions are
            never overwritten.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void handleImprove()}
          disabled={isImproving}
          className="inline-flex items-center gap-2 self-start rounded-md bg-spruce px-4 py-2 text-sm font-semibold text-white shadow-soft transition hover:bg-spruce/90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isImproving ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Sparkles className="h-4 w-4" aria-hidden="true" />
          )}
          Improve Essay for This Opportunity
        </button>
      </div>

      {error ? <p className="px-5 pt-4 text-sm text-red-600">{error}</p> : null}

      {versions.length > 1 ? (
        <div className="border-b border-line px-5 py-3">
          <label className="text-xs font-semibold uppercase text-muted" htmlFor="essay-version">
            Version history
          </label>
          <select
            id="essay-version"
            value={revised?.id ?? ""}
            onChange={(event) => setSelectedVersionId(event.target.value)}
            className="mt-2 w-full max-w-md rounded-md border border-line bg-white px-3 py-2 text-sm"
          >
            {versions.map((version) => (
              <option key={version.id} value={version.id}>
                v{version.version_number} · {version.status}
                {Boolean(version.metadata.is_original) ? " (original)" : ""}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div className="grid gap-0 lg:grid-cols-2">
        <div className="border-b border-line p-5 lg:border-b-0 lg:border-r">
          <div className="mb-3 flex items-center gap-2">
            <h3 className="text-sm font-semibold">Original version</h3>
            <StatusPill status="draft" />
          </div>
          <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-md border border-line bg-canvas p-4 text-sm leading-6 text-ink">
            {originalText || "Upload a personal essay in Documents to enable tailoring."}
          </pre>
        </div>
        <div className="p-5">
          <div className="mb-3 flex items-center gap-2">
            <h3 className="text-sm font-semibold">Revised version</h3>
            {revised ? <StatusPill status={revised.status} /> : null}
          </div>
          <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-md border border-line bg-white p-4 text-sm leading-6 text-ink">
            {revised?.content ?? "Generate a tailored draft with EssayAgent."}
          </pre>
        </div>
      </div>

      <div className="grid gap-4 border-t border-line px-5 py-4 lg:grid-cols-2">
        <div>
          <h3 className="text-sm font-semibold">Suggested improvements</h3>
          {suggestions.length ? (
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-muted">
              {suggestions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-muted">Run EssayAgent to receive targeted suggestions.</p>
          )}
        </div>
        <div>
          <h3 className="text-sm font-semibold">Change summary</h3>
          <p className="mt-3 text-sm leading-6 text-muted">
            {changeSummary || "No generated revision yet."}
          </p>
        </div>
      </div>
    </section>
  );
}

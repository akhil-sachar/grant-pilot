"use client";

import { Loader2, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { generateApplicationRecommendation } from "@/lib/api/client";
import type {
  ApplicationBundle,
  RecommendationDraft,
  RecommendationGenerateResult,
} from "@/lib/types";
import { statusLabel } from "@/lib/utils";

const RECOMMENDER_TYPES = [
  { value: "professor", label: "Professor" },
  { value: "advisor", label: "Advisor" },
  { value: "mentor", label: "Mentor" },
  { value: "manager", label: "Manager" },
] as const;

export function RecommendationEditor({ initialBundle }: { initialBundle: ApplicationBundle }) {
  const [bundle, setBundle] = useState(initialBundle);
  const [selectedDraftId, setSelectedDraftId] = useState<string | null>(null);
  const [latestResult, setLatestResult] = useState<RecommendationGenerateResult | null>(null);
  const [recommenderType, setRecommenderType] =
    useState<(typeof RECOMMENDER_TYPES)[number]["value"]>("professor");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const drafts = useMemo(
    () =>
      [...bundle.recommendation_drafts].sort((a, b) => a.version_number - b.version_number),
    [bundle.recommendation_drafts],
  );
  const selected =
    drafts.find((draft) => draft.id === selectedDraftId) ?? drafts[drafts.length - 1] ?? null;
  const talkingPoints =
    latestResult?.key_talking_points ?? selected?.key_talking_points ?? [];
  const whyItMatches = latestResult?.why_it_matches ?? selected?.why_it_matches ?? "";

  async function handleGenerate() {
    setIsGenerating(true);
    setError(null);
    try {
      const result = await generateApplicationRecommendation(bundle.application.id, {
        recommender_type: recommenderType,
      });
      setLatestResult(result);
      setBundle((current) => ({
        ...current,
        recommendation_drafts: [...current.recommendation_drafts, result.recommendation_draft],
      }));
      setSelectedDraftId(result.recommendation_draft.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Recommendation generation failed");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <section className="mt-6 rounded-lg border border-line bg-panel shadow-soft">
      <div className="flex flex-col gap-4 border-b border-line px-5 py-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-base font-semibold">Recommendation editor</h2>
          <p className="mt-1 text-sm text-muted">
            Generate drafts for your recommender to review and personalize. All outputs remain
            drafts until your recommender approves them.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="text-sm">
            <span className="mb-1 block text-xs font-semibold uppercase text-muted">
              Recommender type
            </span>
            <select
              value={recommenderType}
              onChange={(event) =>
                setRecommenderType(event.target.value as typeof recommenderType)
              }
              className="rounded-md border border-line bg-white px-3 py-2 text-sm"
            >
              {RECOMMENDER_TYPES.map((option) => (
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
              <Sparkles className="h-4 w-4" aria-hidden="true" />
            )}
            Generate Recommendation Draft
          </button>
        </div>
      </div>

      <div className="border-b border-amber-200 bg-amber-50 px-5 py-3 text-sm text-amber-900">
        Draft for recommender review — not for direct submission.
      </div>

      {error ? <p className="px-5 pt-4 text-sm text-red-600">{error}</p> : null}

      {drafts.length > 1 ? (
        <div className="border-b border-line px-5 py-3">
          <label className="text-xs font-semibold uppercase text-muted" htmlFor="rec-version">
            Version history
          </label>
          <select
            id="rec-version"
            value={selected?.id ?? ""}
            onChange={(event) => setSelectedDraftId(event.target.value)}
            className="mt-2 w-full max-w-md rounded-md border border-line bg-white px-3 py-2 text-sm"
          >
            {drafts.map((draft: RecommendationDraft) => (
              <option key={draft.id} value={draft.id}>
                v{draft.version_number} · {statusLabel(draft.recommender_type)} ·{" "}
                {draft.recommender_name}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="border-b border-line p-5 lg:border-b-0 lg:border-r">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-semibold">Recommendation draft</h3>
            {selected ? <StatusPill status={selected.status} /> : null}
            {selected ? <StatusPill status={selected.recommender_type} /> : null}
          </div>
          {selected ? (
            <p className="mb-3 text-sm text-muted">
              {selected.recommender_name} · {selected.relationship}
            </p>
          ) : null}
          <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-md border border-line bg-white p-4 text-sm leading-6 text-ink">
            {selected?.draft_body ?? "Generate a recommendation draft tailored to this opportunity."}
          </pre>
        </div>
        <div className="grid gap-4 p-5">
          <div>
            <h3 className="text-sm font-semibold">Key talking points</h3>
            {talkingPoints.length ? (
              <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-muted">
                {talkingPoints.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-3 text-sm text-muted">
                Talking points appear after you generate a draft.
              </p>
            )}
          </div>
          <div>
            <h3 className="text-sm font-semibold">Why it matches the opportunity</h3>
            <p className="mt-3 text-sm leading-6 text-muted">
              {whyItMatches || "The agent will explain fit against opportunity criteria here."}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

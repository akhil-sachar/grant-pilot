"use client";

import { ExternalLink, SlidersHorizontal, X } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { MatchingActions } from "@/components/matching-actions";
import { ScanStatusPanel } from "@/components/scan-status-panel";
import { StatusPill } from "@/components/status-pill";
import { TagList } from "@/components/tag-list";
import type { MatchResult, Opportunity } from "@/lib/types";
import { formatCurrency, formatDate, scorePercent, statusLabel } from "@/lib/utils";

function opportunityCategory(opportunity: Opportunity) {
  const category = opportunity.metadata.funding_category;
  if (typeof category === "string") {
    return statusLabel(category);
  }
  return statusLabel(opportunity.opportunity_type);
}

export function OpportunitiesWorkspace({
  opportunities,
  matches,
}: {
  opportunities: Opportunity[];
  matches: MatchResult[];
}) {
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [minScore, setMinScore] = useState(0);

  const matchByOpportunity = useMemo(
    () => new Map(matches.map((match) => [match.opportunity_id, match])),
    [matches],
  );

  const types = useMemo(
    () => [...new Set(opportunities.map((item) => item.opportunity_type))].sort(),
    [opportunities],
  );

  const priorities = useMemo(
    () =>
      [...new Set(matches.map((item) => item.priority))].filter(Boolean).sort(),
    [matches],
  );

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return opportunities
      .filter((opportunity) => {
        const match = matchByOpportunity.get(opportunity.id);
        if (typeFilter && opportunity.opportunity_type !== typeFilter) {
          return false;
        }
        if (priorityFilter && match?.priority !== priorityFilter) {
          return false;
        }
        if (minScore > 0 && (match?.score ?? 0) < minScore / 100) {
          return false;
        }
        if (!normalizedQuery) {
          return true;
        }
        const haystack = [
          opportunity.title,
          opportunity.provider_name,
          opportunity.description,
          opportunity.eligibility_summary,
          ...opportunity.tags,
        ]
          .join(" ")
          .toLowerCase();
        return haystack.includes(normalizedQuery);
      })
      .sort((left, right) => {
        const leftScore = matchByOpportunity.get(left.id)?.success_probability ?? -1;
        const rightScore = matchByOpportunity.get(right.id)?.success_probability ?? -1;
        return rightScore - leftScore;
      });
  }, [matchByOpportunity, minScore, opportunities, priorityFilter, query, typeFilter]);

  const activeFilterCount = [typeFilter, priorityFilter, minScore > 0, query.trim()].filter(
    Boolean,
  ).length;

  return (
    <>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setFiltersOpen((value) => !value)}
            className="inline-flex items-center gap-2 rounded-md border border-line bg-panel px-4 py-2 text-sm font-semibold text-ink shadow-soft transition hover:border-spruce hover:text-spruce"
          >
            <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
            Filters
            {activeFilterCount ? (
              <span className="rounded-full bg-spruce px-2 py-0.5 text-xs text-white">
                {activeFilterCount}
              </span>
            ) : null}
          </button>
          {activeFilterCount ? (
            <button
              type="button"
              onClick={() => {
                setQuery("");
                setTypeFilter("");
                setPriorityFilter("");
                setMinScore(0);
              }}
              className="inline-flex items-center gap-1 text-sm text-muted hover:text-spruce"
            >
              <X className="h-3.5 w-3.5" />
              Clear
            </button>
          ) : null}
        </div>
        <MatchingActions compact />
      </div>

      {filtersOpen ? (
        <section className="mb-6 grid gap-4 rounded-lg border border-line bg-panel p-5 shadow-soft md:grid-cols-2 xl:grid-cols-4">
          <label className="grid gap-2 text-sm">
            <span className="font-medium">Search</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Title, provider, tags…"
              className="rounded-md border border-line bg-white px-3 py-2"
            />
          </label>
          <label className="grid gap-2 text-sm">
            <span className="font-medium">Type</span>
            <select
              value={typeFilter}
              onChange={(event) => setTypeFilter(event.target.value)}
              className="rounded-md border border-line bg-white px-3 py-2"
            >
              <option value="">All types</option>
              {types.map((type) => (
                <option key={type} value={type}>
                  {statusLabel(type)}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm">
            <span className="font-medium">Priority</span>
            <select
              value={priorityFilter}
              onChange={(event) => setPriorityFilter(event.target.value)}
              className="rounded-md border border-line bg-white px-3 py-2"
            >
              <option value="">All priorities</option>
              {priorities.map((priority) => (
                <option key={priority} value={priority}>
                  {statusLabel(priority)}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm">
            <span className="font-medium">Min match score ({minScore}%)</span>
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              value={minScore}
              onChange={(event) => setMinScore(Number(event.target.value))}
              className="mt-2"
            />
          </label>
        </section>
      ) : null}

      <div className="mb-6">
        <ScanStatusPanel />
      </div>

      <p className="mb-4 text-sm text-muted">
        Showing {filtered.length} of {opportunities.length} opportunities
      </p>

      <div className="grid gap-4">
        {filtered.map((opportunity) => {
          const match = matchByOpportunity.get(opportunity.id);
          return (
            <section
              key={opportunity.id}
              className="rounded-lg border border-line bg-panel p-5 shadow-soft"
            >
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-lg font-semibold">{opportunity.title}</h2>
                    <StatusPill status={opportunity.status} />
                    {match ? <StatusPill status={match.priority} /> : null}
                  </div>
                  <p className="mt-1 text-sm text-muted">{opportunity.provider_name}</p>
                  <p className="mt-4 max-w-4xl text-sm leading-6 text-muted">
                    {opportunity.description}
                  </p>
                  {match?.fit_explanation ? (
                    <p className="mt-3 text-sm leading-6 text-ink">{match.fit_explanation}</p>
                  ) : (
                    <p className="mt-3 text-sm font-medium text-ink">
                      {opportunity.eligibility_summary}
                    </p>
                  )}
                  {match?.recommended_actions.length ? (
                    <div className="mt-4">
                      <p className="text-xs font-semibold uppercase text-muted">
                        Recommended next steps
                      </p>
                      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-muted">
                        {match.recommended_actions.map((action) => (
                          <li key={action}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                  {match?.missing_materials.length ? (
                    <div className="mt-3">
                      <p className="text-xs font-semibold uppercase text-muted">
                        Missing materials
                      </p>
                      <div className="mt-2">
                        <TagList tags={match.missing_materials} />
                      </div>
                    </div>
                  ) : null}
                  <div className="mt-4">
                    <TagList tags={opportunity.tags} />
                  </div>
                </div>
                <div className="grid min-w-52 gap-3 border-t border-line pt-4 text-sm lg:border-l lg:border-t-0 lg:pl-5 lg:pt-0">
                  <div>
                    <p className="text-xs uppercase text-muted">Match score</p>
                    <p className="mt-1 text-xl font-semibold text-spruce">
                      {scorePercent(match)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-muted">Funding potential</p>
                    <p className="mt-1 font-semibold">
                      {match?.funding_potential ??
                        formatCurrency(opportunity.amount_min, opportunity.amount_max)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-muted">Deadline</p>
                    <p className="mt-1 font-semibold">{formatDate(opportunity.deadline)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-muted">Category</p>
                    <p className="mt-1 font-semibold">{opportunityCategory(opportunity)}</p>
                  </div>
                </div>
              </div>
              {opportunity.source_url ? (
                <Link
                  href={opportunity.source_url}
                  className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-spruce"
                >
                  Source
                  <ExternalLink className="h-4 w-4" aria-hidden="true" />
                </Link>
              ) : null}
            </section>
          );
        })}
      </div>
    </>
  );
}

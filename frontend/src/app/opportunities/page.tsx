import { ExternalLink, SlidersHorizontal } from "lucide-react";
import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { ScanStatusPanel } from "@/components/scan-status-panel";
import { StatusPill } from "@/components/status-pill";
import { TagList } from "@/components/tag-list";
import { getMatches, getOpportunities } from "@/lib/api/client";
import { formatCurrency, formatDate, scorePercent, statusLabel } from "@/lib/utils";

function opportunityCategory(opportunity: {
  opportunity_type: string;
  metadata: Record<string, unknown>;
}) {
  const category = opportunity.metadata.funding_category;
  if (typeof category === "string") {
    return statusLabel(category);
  }
  return statusLabel(opportunity.opportunity_type);
}

export default async function OpportunitiesPage() {
  const [opportunities, matches] = await Promise.all([getOpportunities(), getMatches()]);
  const matchByOpportunity = new Map(
    matches.map((match) => [match.opportunity_id, match]),
  );
  const sorted = [...opportunities].sort((left, right) => {
    const leftScore = matchByOpportunity.get(left.id)?.success_probability ?? -1;
    const rightScore = matchByOpportunity.get(right.id)?.success_probability ?? -1;
    return rightScore - leftScore;
  });

  return (
    <AppShell>
      <PageHeader
        title="Opportunities"
        description="Scholarships, grants, fellowships, and awards scored by MatchingAgent."
        action={
          <button className="inline-flex items-center gap-2 rounded-md border border-line bg-panel px-4 py-2 text-sm font-semibold text-ink shadow-soft transition hover:border-spruce hover:text-spruce">
            <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
            Filters
          </button>
        }
      />

      <div className="mb-6">
        <ScanStatusPanel />
      </div>

      <div className="grid gap-4">
        {sorted.map((opportunity) => {
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
                      <p className="text-xs font-semibold uppercase text-muted">Missing materials</p>
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
                    <p className="mt-1 text-xl font-semibold text-spruce">{scorePercent(match)}</p>
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
                  <div>
                    <p className="text-xs uppercase text-muted">Organization</p>
                    <p className="mt-1 font-semibold">{opportunity.provider_name}</p>
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
    </AppShell>
  );
}

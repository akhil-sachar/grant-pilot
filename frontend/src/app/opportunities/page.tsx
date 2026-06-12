import { ExternalLink, SlidersHorizontal } from "lucide-react";
import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { TagList } from "@/components/tag-list";
import { getMatches, getOpportunities } from "@/lib/api/client";
import { formatCurrency, formatDate, percent, statusLabel } from "@/lib/utils";

export default async function OpportunitiesPage() {
  const [opportunities, matches] = await Promise.all([getOpportunities(), getMatches()]);
  const matchByOpportunity = new Map(
    matches.map((match) => [match.opportunity_id, match]),
  );

  return (
    <AppShell>
      <PageHeader
        title="Opportunities"
        description="Scholarships, grants, fellowships, and awards available to the demo profile."
        action={
          <button className="inline-flex items-center gap-2 rounded-md border border-line bg-panel px-4 py-2 text-sm font-semibold text-ink shadow-soft transition hover:border-spruce hover:text-spruce">
            <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
            Filters
          </button>
        }
      />

      <div className="grid gap-4">
        {opportunities.map((opportunity) => {
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
                  </div>
                  <p className="mt-1 text-sm text-muted">{opportunity.provider_name}</p>
                  <p className="mt-4 max-w-4xl text-sm leading-6 text-muted">
                    {opportunity.description}
                  </p>
                  <p className="mt-3 text-sm font-medium text-ink">
                    {opportunity.eligibility_summary}
                  </p>
                  <div className="mt-4">
                    <TagList tags={opportunity.tags} />
                  </div>
                </div>
                <div className="grid min-w-48 gap-3 border-t border-line pt-4 text-sm lg:border-l lg:border-t-0 lg:pl-5 lg:pt-0">
                  <div>
                    <p className="text-xs uppercase text-muted">Match</p>
                    <p className="mt-1 text-xl font-semibold text-spruce">
                      {match ? percent(match.score) : "Not scored"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-muted">Award</p>
                    <p className="mt-1 font-semibold">
                      {formatCurrency(opportunity.amount_min, opportunity.amount_max)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-muted">Deadline</p>
                    <p className="mt-1 font-semibold">{formatDate(opportunity.deadline)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-muted">Type</p>
                    <p className="mt-1 font-semibold">
                      {statusLabel(opportunity.opportunity_type)}
                    </p>
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

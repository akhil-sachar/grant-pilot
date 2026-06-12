import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { getApplications, getMatches, getOpportunities } from "@/lib/api/client";
import { scorePercent } from "@/lib/utils";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = q.trim().toLowerCase();

  const [opportunities, applications, matches] = await Promise.all([
    getOpportunities(),
    getApplications(),
    getMatches(),
  ]);

  const opportunityById = new Map(opportunities.map((item) => [item.id, item]));
  const matchByOpportunity = new Map(matches.map((item) => [item.opportunity_id, item]));

  const matchedOpportunities = query
    ? opportunities.filter((item) => {
        const haystack = [item.title, item.provider_name, item.description, ...item.tags]
          .join(" ")
          .toLowerCase();
        return haystack.includes(query);
      })
    : [];

  const matchedApplications = query
    ? applications.filter((item) => {
        const opportunity = opportunityById.get(item.opportunity_id);
        const haystack = [
          item.id,
          item.status,
          item.notes ?? "",
          opportunity?.title ?? "",
          opportunity?.provider_name ?? "",
        ]
          .join(" ")
          .toLowerCase();
        return haystack.includes(query);
      })
    : [];

  return (
    <AppShell>
      <PageHeader
        title="Search"
        description="Search opportunities and applications across your workspace."
      />

      <form action="/search" method="get" className="mb-6">
        <label className="grid gap-2 text-sm">
          <span className="font-medium">Query</span>
          <div className="flex gap-2">
            <input
              type="search"
              name="q"
              defaultValue={q}
              placeholder="Scholarship, grant, application status…"
              className="flex-1 rounded-md border border-line bg-white px-3 py-2"
            />
            <button
              type="submit"
              className="rounded-md bg-spruce px-4 py-2 text-sm font-semibold text-white"
            >
              Search
            </button>
          </div>
        </label>
      </form>

      {!query ? (
        <p className="text-sm text-muted">Enter a search term to find opportunities and applications.</p>
      ) : (
        <div className="grid gap-6">
          <section className="rounded-lg border border-line bg-panel shadow-soft">
            <div className="border-b border-line px-5 py-4">
              <h2 className="text-base font-semibold">
                Opportunities ({matchedOpportunities.length})
              </h2>
            </div>
            <div className="divide-y divide-line">
              {matchedOpportunities.length ? (
                matchedOpportunities.map((item) => {
                  const match = matchByOpportunity.get(item.id);
                  return (
                    <div key={item.id} className="px-5 py-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <Link href="/opportunities" className="font-medium hover:text-spruce">
                          {item.title}
                        </Link>
                        {match ? <StatusPill status={match.priority} /> : null}
                      </div>
                      <p className="mt-1 text-sm text-muted">{item.provider_name}</p>
                      {match ? (
                        <p className="mt-2 text-sm text-muted">Match {scorePercent(match)}</p>
                      ) : null}
                    </div>
                  );
                })
              ) : (
                <p className="px-5 py-4 text-sm text-muted">No matching opportunities.</p>
              )}
            </div>
          </section>

          <section className="rounded-lg border border-line bg-panel shadow-soft">
            <div className="border-b border-line px-5 py-4">
              <h2 className="text-base font-semibold">
                Applications ({matchedApplications.length})
              </h2>
            </div>
            <div className="divide-y divide-line">
              {matchedApplications.length ? (
                matchedApplications.map((item) => {
                  const opportunity = opportunityById.get(item.opportunity_id);
                  return (
                    <div key={item.id} className="px-5 py-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <Link
                          href={`/applications/${item.id}`}
                          className="font-medium hover:text-spruce"
                        >
                          {opportunity?.title ?? item.id}
                        </Link>
                        <StatusPill status={item.status} />
                      </div>
                      <p className="mt-1 text-sm text-muted">{opportunity?.provider_name}</p>
                    </div>
                  );
                })
              ) : (
                <p className="px-5 py-4 text-sm text-muted">No matching applications.</p>
              )}
            </div>
          </section>
        </div>
      )}
    </AppShell>
  );
}

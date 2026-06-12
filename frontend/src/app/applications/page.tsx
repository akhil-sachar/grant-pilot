import { CheckCircle2, Circle, Clock3 } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { getApplications, getOpportunities } from "@/lib/api/client";
import { checklistProgress, formatDate, percent } from "@/lib/utils";

export default async function ApplicationsPage() {
  const [applications, opportunities] = await Promise.all([
    getApplications(),
    getOpportunities(),
  ]);
  const opportunityById = new Map(
    opportunities.map((opportunity) => [opportunity.id, opportunity]),
  );

  return (
    <AppShell>
      <PageHeader
        title="Applications"
        description="Application plans, checklists, drafts, and submission readiness."
      />

      <div className="grid gap-5">
        {applications.map((application) => {
          const opportunity = opportunityById.get(application.opportunity_id);
          const progress = checklistProgress(application.checklist);

          return (
            <section
              key={application.id}
              className="rounded-lg border border-line bg-panel shadow-soft"
            >
              <div className="grid gap-5 px-5 py-5 lg:grid-cols-[1fr_220px]">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-lg font-semibold">{opportunity?.title}</h2>
                    <StatusPill status={application.status} />
                  </div>
                  <p className="mt-1 text-sm text-muted">{opportunity?.provider_name}</p>
                  {application.notes ? (
                    <p className="mt-4 text-sm leading-6 text-muted">{application.notes}</p>
                  ) : null}
                </div>
                <div className="border-t border-line pt-4 lg:border-l lg:border-t-0 lg:pl-5 lg:pt-0">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm text-muted">Checklist</p>
                    <p className="font-semibold text-spruce">{percent(progress)}</p>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-canvas">
                    <div
                      className="h-2 rounded-full bg-spruce"
                      style={{ width: percent(progress) }}
                    />
                  </div>
                  <p className="mt-3 text-sm text-muted">Due {formatDate(application.due_at)}</p>
                </div>
              </div>

              <div className="border-t border-line px-5 py-4">
                <div className="grid gap-3 md:grid-cols-3">
                  {application.checklist.map((item) => {
                    const Icon =
                      item.status === "done"
                        ? CheckCircle2
                        : item.status === "in_progress"
                          ? Clock3
                          : Circle;
                    return (
                      <div key={item.id} className="flex min-w-0 items-center gap-3 py-2">
                        <Icon className="h-4 w-4 shrink-0 text-spruce" aria-hidden="true" />
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium">{item.label}</p>
                          <StatusPill status={item.status} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </section>
          );
        })}
      </div>
    </AppShell>
  );
}

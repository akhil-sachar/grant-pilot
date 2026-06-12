import {
  Bell,
  CalendarClock,
  FolderKanban,
  ListChecks,
  Radar,
  Sparkles,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { MetricCard } from "@/components/metric-card";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { TagList } from "@/components/tag-list";
import { getDashboard } from "@/lib/api/client";
import {
  checklistProgress,
  formatCurrency,
  formatDate,
  percent,
} from "@/lib/utils";

export default async function DashboardPage() {
  const dashboard = await getDashboard();
  const opportunityById = new Map(
    dashboard.opportunities.map((opportunity) => [opportunity.id, opportunity]),
  );

  return (
    <AppShell>
      <PageHeader
        title={`Welcome back, ${dashboard.profile.full_name.split(" ")[0]}`}
        description="Track your strongest funding paths, current applications, document readiness, and review queue."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Opportunities Found"
          value={dashboard.metrics.opportunities_found}
          helper={`Storage: ${String(dashboard.storage.storage_mode ?? "local")}`}
          icon={Sparkles}
        />
        <MetricCard
          label="Active Applications"
          value={dashboard.metrics.active_applications}
          helper="Planned or in progress"
          icon={FolderKanban}
        />
        <MetricCard
          label="Upcoming Deadlines"
          value={dashboard.metrics.upcoming_deadlines}
          helper={formatDate(dashboard.metrics.next_deadline)}
          icon={CalendarClock}
        />
        <MetricCard
          label="Match Scores"
          value={percent(dashboard.metrics.average_match_score)}
          helper={`${dashboard.metrics.agent_actions} agent actions logged`}
          icon={Radar}
        />
        <MetricCard
          label="Agent Actions"
          value={dashboard.metrics.agent_actions}
          helper="Logs only; agents are not enabled"
          icon={ListChecks}
        />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <section className="rounded-lg border border-line bg-panel shadow-soft">
          <div className="border-b border-line px-5 py-4">
            <h2 className="text-base font-semibold">Top matches</h2>
          </div>
          <div className="divide-y divide-line">
            {dashboard.top_matches.map((match) => {
              const opportunity = opportunityById.get(match.opportunity_id);
              return (
                <div key={match.id} className="grid gap-4 px-5 py-4 md:grid-cols-[1fr_auto]">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-semibold">{opportunity?.title ?? "Opportunity"}</h3>
                      <StatusPill status={match.status} />
                    </div>
                    <p className="mt-1 text-sm text-muted">{opportunity?.provider_name}</p>
                    <p className="mt-3 text-sm leading-6 text-muted">{match.rationale}</p>
                    <div className="mt-3">
                      <TagList tags={opportunity?.tags ?? []} />
                    </div>
                  </div>
                  <div className="flex min-w-28 flex-col items-start md:items-end">
                    <p className="text-2xl font-semibold text-spruce">{percent(match.score)}</p>
                    <p className="text-sm text-muted">
                      {formatCurrency(opportunity?.amount_min, opportunity?.amount_max)}
                    </p>
                    <p className="mt-2 text-sm text-muted">
                      {formatDate(opportunity?.deadline)}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="rounded-lg border border-line bg-panel shadow-soft">
          <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-4">
            <h2 className="text-base font-semibold">Notifications</h2>
            <Bell className="h-4 w-4 text-muted" aria-hidden="true" />
          </div>
          <div className="divide-y divide-line">
            {dashboard.notifications.map((notification) => (
              <div key={notification.id} className="px-5 py-4">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-sm font-semibold">{notification.title}</h3>
                  <StatusPill status={notification.notification_type} />
                </div>
                <p className="mt-2 text-sm leading-6 text-muted">{notification.message}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="mt-6 rounded-lg border border-line bg-panel shadow-soft">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-base font-semibold">Application pipeline</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-line text-xs uppercase text-muted">
              <tr>
                <th className="px-5 py-3 font-semibold">Opportunity</th>
                <th className="px-5 py-3 font-semibold">Status</th>
                <th className="px-5 py-3 font-semibold">Progress</th>
                <th className="px-5 py-3 font-semibold">Due</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {dashboard.applications.map((application) => {
                const opportunity = opportunityById.get(application.opportunity_id);
                const progress = checklistProgress(application.checklist);
                return (
                  <tr key={application.id}>
                    <td className="px-5 py-4">
                      <p className="font-medium">{opportunity?.title}</p>
                      <p className="text-muted">{opportunity?.provider_name}</p>
                    </td>
                    <td className="px-5 py-4">
                      <StatusPill status={application.status} />
                    </td>
                    <td className="px-5 py-4">
                      <div className="h-2 w-40 rounded-full bg-canvas">
                        <div
                          className="h-2 rounded-full bg-spruce"
                          style={{ width: percent(progress) }}
                        />
                      </div>
                    </td>
                    <td className="px-5 py-4 text-muted">{formatDate(application.due_at)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </AppShell>
  );
}

import { AppShell } from "@/components/app-shell";
import { CreateApplicationPanel } from "@/components/create-application-panel";
import { PageHeader } from "@/components/page-header";
import { ApplicationsList } from "@/components/applications-list";
import { getApplications, getMatches, getOpportunities } from "@/lib/api/client";

export default async function ApplicationsPage() {
  const [applications, opportunities, matches] = await Promise.all([
    getApplications(),
    getOpportunities(),
    getMatches(),
  ]);

  return (
    <AppShell>
      <PageHeader
        title="Applications"
        description="Application plans, checklists, drafts, and submission readiness."
      />

      <div className="mb-6">
        <CreateApplicationPanel
          opportunities={opportunities}
          matches={matches}
          existingOpportunityIds={applications.map((item) => item.opportunity_id)}
        />
      </div>

      <ApplicationsList applications={applications} opportunities={opportunities} />
    </AppShell>
  );
}

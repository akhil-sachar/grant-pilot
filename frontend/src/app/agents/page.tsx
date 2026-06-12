import { AppShell } from "@/components/app-shell";
import { AgentActivityDashboard } from "@/components/agent-activity-dashboard";
import { PageHeader } from "@/components/page-header";
import { getAgentActivity, getOpenUILayout } from "@/lib/api/client";

export default async function AgentsPage() {
  const [activity, layout] = await Promise.all([getAgentActivity(), getOpenUILayout()]);

  return (
    <AppShell>
      <PageHeader
        title="Agent Activity"
        description="Guild AI observability across Sponsor, Matching, Essay, Recommendation, Outreach, and Notification agents."
      />
      <AgentActivityDashboard activity={activity} openuiComponents={layout.components} />
    </AppShell>
  );
}

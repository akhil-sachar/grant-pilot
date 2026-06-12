import { AppShell } from "@/components/app-shell";
import { AgentActivityDashboard } from "@/components/agent-activity-dashboard";
import { PageHeader } from "@/components/page-header";
import { StorageAdminPanel } from "@/components/storage-admin-panel";
import {
  getAgentActivity,
  getIngestionRuns,
  getOpenUILayout,
  getRuntimeConfig,
} from "@/lib/api/client";

export default async function AgentsPage() {
  const [activity, layout, ingestionRuns, runtime] = await Promise.all([
    getAgentActivity(),
    getOpenUILayout(),
    getIngestionRuns(),
    getRuntimeConfig(),
  ]);

  return (
    <AppShell>
      <PageHeader
        title="Agent Activity"
        description="Guild AI observability across Sponsor, Matching, Essay, Recommendation, Outreach, and Notification agents."
      />
      <AgentActivityDashboard
        activity={activity}
        openuiComponents={layout.components}
        openuiEnabled={runtime.integrations.openui_enabled}
      />
      <div className="mt-6">
        <StorageAdminPanel ingestionRuns={ingestionRuns} />
      </div>
    </AppShell>
  );
}

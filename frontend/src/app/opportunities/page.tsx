import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { OpportunitiesWorkspace } from "@/components/opportunities-workspace";
import { PageHeader } from "@/components/page-header";
import { getMatches, getOpportunities } from "@/lib/api/client";

export default async function OpportunitiesPage() {
  const [opportunities, matches] = await Promise.all([getOpportunities(), getMatches()]);

  return (
    <AppShell>
      <PageHeader
        title="Opportunities"
        description="Scholarships, grants, fellowships, and awards scored by MatchingAgent."
      />
      <OpportunitiesWorkspace opportunities={opportunities} matches={matches} />
    </AppShell>
  );
}

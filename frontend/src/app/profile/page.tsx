import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { getProfile } from "@/lib/api/client";

import { ProfileVault } from "./vault";

export default async function ProfilePage() {
  const profile = await getProfile();

  return (
    <AppShell>
      <PageHeader
        title="Profile Vault"
        description="Store the structured applicant facts used by matching, applications, and future agents."
      />
      <ProfileVault initialProfile={profile} />
    </AppShell>
  );
}


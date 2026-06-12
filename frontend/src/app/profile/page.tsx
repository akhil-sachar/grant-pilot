import { Mail, MapPin, Phone, School } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { TagList } from "@/components/tag-list";
import { getProfile } from "@/lib/api/client";
import { formatDate } from "@/lib/utils";

function DetailItem({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div>
      <p className="text-xs uppercase text-muted">{label}</p>
      <p className="mt-1 font-medium text-ink">{value ?? "Not set"}</p>
    </div>
  );
}

export default async function ProfilePage() {
  const profile = await getProfile();
  const preferenceRows = Object.entries(profile.preferences);
  const demographicRows = Object.entries(profile.demographic_info);

  return (
    <AppShell>
      <PageHeader
        title="Profile"
        description="Profile facts used by matching, documents, and future application agents."
      />

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="grid gap-6 px-5 py-5 lg:grid-cols-[1fr_1.2fr]">
          <div className="min-w-0">
            <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-spruce text-2xl font-semibold text-white">
              {profile.full_name
                .split(" ")
                .map((part) => part[0])
                .join("")}
            </div>
            <h2 className="mt-4 text-2xl font-semibold">{profile.full_name}</h2>
            <p className="mt-2 text-sm text-muted">{profile.education_level}</p>
            <div className="mt-5 grid gap-3 text-sm text-muted">
              <p className="flex items-center gap-2">
                <Mail className="h-4 w-4" aria-hidden="true" />
                {profile.email}
              </p>
              <p className="flex items-center gap-2">
                <Phone className="h-4 w-4" aria-hidden="true" />
                {profile.phone}
              </p>
              <p className="flex items-center gap-2">
                <MapPin className="h-4 w-4" aria-hidden="true" />
                {profile.location}
              </p>
              <p className="flex items-center gap-2">
                <School className="h-4 w-4" aria-hidden="true" />
                {profile.school_name}
              </p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <DetailItem label="Graduation" value={profile.graduation_year} />
            <DetailItem label="Citizenship" value={profile.citizenship_status} />
            <DetailItem label="Birth date" value={formatDate(profile.date_of_birth, "Not set")} />
            <DetailItem label="Updated" value={formatDate(profile.updated_at)} />
          </div>
        </div>
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
          <h2 className="text-base font-semibold">Fields of study</h2>
          <div className="mt-4">
            <TagList tags={profile.fields_of_study} />
          </div>
        </section>

        <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
          <h2 className="text-base font-semibold">Funding goals</h2>
          <div className="mt-4">
            <TagList tags={profile.funding_goals} />
          </div>
        </section>
      </div>

      <section className="mt-6 rounded-lg border border-line bg-panel p-5 shadow-soft">
        <h2 className="text-base font-semibold">Career goals</h2>
        <div className="mt-4">
          <TagList tags={profile.career_goals} />
        </div>
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border border-line bg-panel shadow-soft">
          <div className="border-b border-line px-5 py-4">
            <h2 className="text-base font-semibold">Preferences</h2>
          </div>
          <div className="divide-y divide-line">
            {preferenceRows.map(([key, value]) => (
              <div key={key} className="flex items-center justify-between gap-4 px-5 py-3">
                <span className="text-sm text-muted">{key}</span>
                <span className="text-sm font-medium">{String(value)}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-line bg-panel shadow-soft">
          <div className="border-b border-line px-5 py-4">
            <h2 className="text-base font-semibold">Eligibility signals</h2>
          </div>
          <div className="divide-y divide-line">
            {demographicRows.map(([key, value]) => (
              <div key={key} className="flex items-center justify-between gap-4 px-5 py-3">
                <span className="text-sm text-muted">{key}</span>
                <span className="text-sm font-medium">{String(value)}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AppShell>
  );
}

"use client";

import { Loader2, Save } from "lucide-react";
import { useState } from "react";

import { TagList } from "@/components/tag-list";
import { updateProfile } from "@/lib/api/client";
import type { UserProfile } from "@/lib/types";
import { formatDate } from "@/lib/utils";

const listFields = [
  { key: "career_goals", label: "Career Goals" },
  { key: "research_interests", label: "Research Interests" },
  { key: "awards", label: "Awards" },
  { key: "projects", label: "Projects" },
  { key: "leadership_experience", label: "Leadership Experience" },
] as const;

export function ProfileVault({ initialProfile }: { initialProfile: UserProfile }) {
  const [profile, setProfile] = useState(initialProfile);
  const [draft, setDraft] = useState(toDraft(initialProfile));
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function saveProfile() {
    setIsSaving(true);
    setMessage(null);
    try {
      const payload = fromDraft(profile, draft);
      const saved = await updateProfile(payload);
      setProfile(saved);
      setDraft(toDraft(saved));
      setMessage("Profile vault saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Profile save failed.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-base font-semibold">Applicant profile</h2>
        </div>
        <div className="grid gap-4 p-5 sm:grid-cols-2">
          <Field
            label="Name"
            value={draft.full_name}
            onChange={(value) => setDraft({ ...draft, full_name: value })}
          />
          <Field
            label="School"
            value={draft.school_name}
            onChange={(value) => setDraft({ ...draft, school_name: value })}
          />
          <Field
            label="Major"
            value={draft.major}
            onChange={(value) => setDraft({ ...draft, major: value })}
          />
          <Field
            label="GPA"
            value={draft.gpa}
            inputMode="decimal"
            onChange={(value) => setDraft({ ...draft, gpa: value })}
          />
          <Field
            label="Graduation Year"
            value={draft.graduation_year}
            inputMode="numeric"
            onChange={(value) => setDraft({ ...draft, graduation_year: value })}
          />
          <Field
            label="Email"
            value={draft.email}
            onChange={(value) => setDraft({ ...draft, email: value })}
          />
        </div>
        <div className="border-t border-line px-5 py-4">
          <button
            type="button"
            onClick={() => void saveProfile()}
            className="inline-flex h-10 items-center gap-2 rounded-md bg-spruce px-4 text-sm font-semibold text-white transition hover:bg-[#06684b]"
          >
            {isSaving ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <Save className="h-4 w-4" aria-hidden="true" />
            )}
            Save profile
          </button>
          {message ? <p className="mt-3 text-sm text-muted">{message}</p> : null}
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-base font-semibold">Vault summary</h2>
        </div>
        <div className="grid gap-4 p-5 sm:grid-cols-2">
          <SummaryItem label="Name" value={profile.full_name} />
          <SummaryItem label="School" value={profile.school_name} />
          <SummaryItem label="Major" value={profile.major} />
          <SummaryItem label="GPA" value={profile.gpa?.toFixed(2)} />
          <SummaryItem label="Graduation" value={profile.graduation_year} />
          <SummaryItem label="Updated" value={formatDate(profile.updated_at)} />
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-soft xl:col-span-2">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-base font-semibold">Narrative and evidence</h2>
        </div>
        <div className="grid gap-6 p-5 lg:grid-cols-2">
          {listFields.map((field) => (
            <div key={field.key} className="min-w-0">
              <label className="text-sm font-semibold" htmlFor={field.key}>
                {field.label}
              </label>
              <textarea
                id={field.key}
                value={draft[field.key]}
                onChange={(event) =>
                  setDraft({ ...draft, [field.key]: event.target.value })
                }
                rows={4}
                className="mt-2 w-full resize-y rounded-md border border-line bg-canvas px-3 py-2 text-sm outline-none transition focus:border-spruce"
              />
              <div className="mt-3">
                <TagList tags={splitList(draft[field.key])} />
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Field({
  label,
  value,
  inputMode,
  onChange,
}: {
  label: string;
  value: string;
  inputMode?: "decimal" | "numeric";
  onChange: (value: string) => void;
}) {
  return (
    <label className="text-sm font-semibold">
      {label}
      <input
        value={value}
        inputMode={inputMode}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 h-10 w-full rounded-md border border-line bg-canvas px-3 text-sm font-normal outline-none transition focus:border-spruce"
      />
    </label>
  );
}

function SummaryItem({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div>
      <p className="text-xs uppercase text-muted">{label}</p>
      <p className="mt-1 font-medium text-ink">{value ?? "Not set"}</p>
    </div>
  );
}

function toDraft(profile: UserProfile) {
  return {
    email: profile.email ?? "",
    full_name: profile.full_name ?? "",
    school_name: profile.school_name ?? "",
    major: profile.major ?? "",
    gpa: profile.gpa?.toString() ?? "",
    graduation_year: profile.graduation_year?.toString() ?? "",
    career_goals: profile.career_goals.join("\n"),
    research_interests: profile.research_interests.join("\n"),
    awards: profile.awards.join("\n"),
    projects: profile.projects.join("\n"),
    leadership_experience: profile.leadership_experience.join("\n"),
  };
}

function fromDraft(profile: UserProfile, draft: ReturnType<typeof toDraft>): Partial<UserProfile> {
  return {
    ...profile,
    email: draft.email,
    full_name: draft.full_name,
    school_name: draft.school_name,
    major: draft.major,
    gpa: draft.gpa ? Number(draft.gpa) : null,
    graduation_year: draft.graduation_year ? Number(draft.graduation_year) : null,
    career_goals: splitList(draft.career_goals),
    research_interests: splitList(draft.research_interests),
    awards: splitList(draft.awards),
    projects: splitList(draft.projects),
    leadership_experience: splitList(draft.leadership_experience),
  };
}

function splitList(value: string) {
  return value
    .split(/\r?\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}


import Link from "next/link";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { EssayEditor } from "@/components/essay-editor";
import { RecommendationEditor } from "@/components/recommendation-editor";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { TagList } from "@/components/tag-list";
import { getApplicationBundle } from "@/lib/api/client";
import { checklistProgress, formatDate, percent } from "@/lib/utils";

export default async function ApplicationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let bundle;
  try {
    bundle = await getApplicationBundle(id);
  } catch {
    notFound();
  }

  const progress = checklistProgress(bundle.application.checklist);

  return (
    <AppShell>
      <PageHeader
        title={bundle.opportunity.title}
        description={bundle.opportunity.provider_name}
        action={
          <Link
            href="/applications"
            className="inline-flex items-center rounded-md border border-line bg-panel px-4 py-2 text-sm font-semibold text-ink shadow-soft transition hover:border-spruce hover:text-spruce"
          >
            Back to applications
          </Link>
        }
      />

      <div className="mb-6 grid gap-4 rounded-lg border border-line bg-panel p-5 shadow-soft lg:grid-cols-[1fr_220px]">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <StatusPill status={bundle.application.status} />
            <StatusPill status={bundle.opportunity.opportunity_type} />
          </div>
          <p className="mt-4 text-sm leading-6 text-muted">{bundle.opportunity.description}</p>
          <div className="mt-4">
            <TagList tags={bundle.opportunity.tags} />
          </div>
          {bundle.application.notes ? (
            <p className="mt-4 text-sm text-ink">{bundle.application.notes}</p>
          ) : null}
        </div>
        <div className="border-t border-line pt-4 lg:border-l lg:border-t-0 lg:pl-5 lg:pt-0">
          <p className="text-sm text-muted">Checklist progress</p>
          <p className="mt-1 text-2xl font-semibold text-spruce">{percent(progress)}</p>
          <p className="mt-3 text-sm text-muted">Due {formatDate(bundle.application.due_at)}</p>
        </div>
      </div>

      <EssayEditor initialBundle={bundle} />
      <RecommendationEditor initialBundle={bundle} />
    </AppShell>
  );
}

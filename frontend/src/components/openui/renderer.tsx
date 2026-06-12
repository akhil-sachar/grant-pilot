"use client";

import Link from "next/link";

import { StatusPill } from "@/components/status-pill";
import { formatDate, percent } from "@/lib/utils";
import type { OpenUIComponent } from "@/lib/types";

function OpportunityCard({ props }: { props: Record<string, unknown> }) {
  const title = String(props.title ?? "Opportunity");
  const provider = String(props.provider ?? "");
  const score = Number(props.score_percent ?? 0);
  const success = Number(props.success_probability ?? 0);
  const priority = String(props.priority ?? "medium");
  const tags = Array.isArray(props.tags) ? (props.tags as string[]) : [];

  return (
    <article className="rounded-lg border border-line bg-canvas p-4 shadow-soft">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="font-semibold">{title}</h3>
        <StatusPill status={priority} />
      </div>
      <p className="mt-1 text-sm text-muted">{provider}</p>
      <div className="mt-3 flex gap-4 text-sm">
        <span className="font-medium text-spruce">Match {score}%</span>
        <span className="text-muted">Win {percent(success)}</span>
      </div>
      <p className="mt-2 text-xs text-muted">{formatDate(String(props.deadline ?? ""))}</p>
      {tags.length ? (
        <div className="mt-3 flex flex-wrap gap-1">
          {tags.slice(0, 3).map((tag) => (
            <span key={tag} className="rounded-full bg-panel px-2 py-0.5 text-xs text-muted ring-1 ring-line">
              {tag}
            </span>
          ))}
        </div>
      ) : null}
    </article>
  );
}

function MatchPanel({ props }: { props: Record<string, unknown> }) {
  const actions = Array.isArray(props.recommended_actions)
    ? (props.recommended_actions as string[])
    : [];
  const missing = Array.isArray(props.missing_materials)
    ? (props.missing_materials as string[])
    : [];

  return (
    <article className="rounded-lg border border-line bg-panel p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-medium">Match score {percent(Number(props.score ?? 0))}</p>
        <StatusPill status={String(props.priority ?? "medium")} />
      </div>
      <p className="mt-2 text-sm leading-6 text-muted">{String(props.fit_explanation ?? "")}</p>
      {actions.length ? (
        <p className="mt-2 text-sm text-ink">Next: {actions[0]}</p>
      ) : null}
      {missing.length ? (
        <p className="mt-2 text-xs text-muted">Missing: {missing.join(", ")}</p>
      ) : null}
    </article>
  );
}

function PipelineRow({ props }: { props: Record<string, unknown> }) {
  const total = Number(props.checklist_total ?? 1);
  const done = Number(props.checklist_done ?? 0);
  const progress = total ? Math.round((done / total) * 100) : 0;

  return (
    <div className="flex items-center justify-between gap-4 border-b border-line px-4 py-3 last:border-b-0">
      <div>
        <p className="text-sm font-medium">{String(props.application_id ?? "Application")}</p>
        <StatusPill status={String(props.status ?? "planned")} />
      </div>
      <div className="min-w-32 text-right">
        <div className="ml-auto h-2 w-28 rounded-full bg-canvas">
          <div className="h-2 rounded-full bg-spruce" style={{ width: `${progress}%` }} />
        </div>
        <p className="mt-1 text-xs text-muted">{formatDate(String(props.due_at ?? ""))}</p>
      </div>
    </div>
  );
}

function NotificationItem({ props }: { props: Record<string, unknown> }) {
  const actionUrl = props.action_url ? String(props.action_url) : null;
  const content = (
    <>
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold">{String(props.title ?? "Notification")}</h3>
        <StatusPill status={String(props.type ?? "system")} />
      </div>
      <p className="mt-2 text-sm leading-6 text-muted">{String(props.message ?? "")}</p>
      <div className="mt-2 flex gap-2">
        <StatusPill status={String(props.priority ?? "medium")} />
        {!props.is_read ? <StatusPill status="started" /> : null}
      </div>
    </>
  );

  return (
    <article className="rounded-lg border border-line bg-panel p-4">
      {actionUrl ? (
        <Link href={actionUrl} className="block transition hover:text-spruce">
          {content}
        </Link>
      ) : (
        content
      )}
    </article>
  );
}

function TimelineEvent({ props }: { props: Record<string, unknown> }) {
  return (
    <div className="relative border-l-2 border-spruce/30 pl-4 pb-4 last:pb-0">
      <span className="absolute -left-1.5 top-1 h-3 w-3 rounded-full bg-spruce" />
      <div className="flex flex-wrap items-center gap-2">
        <p className="text-sm font-semibold">{String(props.agent_name ?? "agent")}</p>
        <StatusPill status={String(props.status ?? "completed")} />
      </div>
      <p className="mt-1 text-xs text-muted">{String(props.action_type ?? "")}</p>
      <p className="mt-2 text-sm text-muted">{String(props.output_summary ?? props.input_summary ?? "")}</p>
      <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted">
        <span>{formatDate(String(props.created_at ?? ""))}</span>
        {props.runtime_ms ? <span>{String(props.runtime_ms)} ms</span> : null}
        {props.guild_run_id ? <span>Guild {String(props.guild_run_id)}</span> : null}
      </div>
    </div>
  );
}

function SectionBlock({ component }: { component: OpenUIComponent }) {
  const layout = String(component.props.layout ?? "stack");
  const title = String(component.props.title ?? "Section");

  return (
    <section className="rounded-lg border border-line bg-panel shadow-soft">
      <div className="border-b border-line px-5 py-4">
        <h2 className="text-base font-semibold">{title}</h2>
      </div>
      <div
        className={
          layout === "grid"
            ? "grid gap-4 p-4 sm:grid-cols-2"
            : layout === "feed"
              ? "space-y-3 p-4"
              : layout === "timeline"
                ? "p-5"
                : "divide-y divide-line"
        }
      >
        {(component.children ?? []).map((child) => (
          <OpenUINode key={child.id} component={child} />
        ))}
      </div>
    </section>
  );
}

export function OpenUINode({ component }: { component: OpenUIComponent }) {
  switch (component.type) {
    case "section":
      return <SectionBlock component={component} />;
    case "opportunity_card":
      return <OpportunityCard props={component.props} />;
    case "match_panel":
      return <MatchPanel props={component.props} />;
    case "pipeline_row":
      return <PipelineRow props={component.props} />;
    case "notification_item":
      return <NotificationItem props={component.props} />;
    case "timeline_event":
      return <TimelineEvent props={component.props} />;
    default:
      return (
        <div className="rounded-md border border-dashed border-line p-3 text-sm text-muted">
          Unknown component: {component.type}
        </div>
      );
  }
}

export function OpenUIRenderer({ components }: { components: OpenUIComponent[] }) {
  return (
    <div className="space-y-6">
      {components.map((component) => (
        <OpenUINode key={component.id} component={component} />
      ))}
    </div>
  );
}

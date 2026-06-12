"use client";

import { Activity, Bot, Clock3, Gauge, Sparkles, Target } from "lucide-react";

import { MetricCard } from "@/components/metric-card";
import { OpenUIRenderer } from "@/components/openui/renderer";
import { StatusPill } from "@/components/status-pill";
import type { AgentActivityResponse } from "@/lib/types";
import { formatDate, percent } from "@/lib/utils";

const AGENT_LABELS: Record<string, string> = {
  "sponsor-agent": "SponsorAgent",
  "matching-agent": "MatchingAgent",
  "essay-agent": "EssayAgent",
  "recommendation-agent": "RecommendationAgent",
  "outreach-agent": "OutreachAgent",
  "notification-agent": "NotificationAgent",
  "composio-service": "Composio",
};

export function AgentActivityDashboard({
  activity,
  openuiComponents,
  openuiEnabled = true,
}: {
  activity: AgentActivityResponse;
  openuiComponents?: import("@/lib/types").OpenUIComponent[];
  openuiEnabled?: boolean;
}) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Avg Runtime"
          value={`${Math.round(activity.average_runtime_ms)} ms`}
          helper="Across tracked agent runs"
          icon={Clock3}
        />
        <MetricCard
          label="Success Rate"
          value={percent(activity.overall_success_rate)}
          helper={`${activity.total_runs} total runs`}
          icon={Gauge}
        />
        <MetricCard
          label="Actions Completed"
          value={activity.total_actions_completed}
          helper="Outputs produced by agents"
          icon={Target}
        />
        <MetricCard
          label="Opportunities Found"
          value={activity.opportunities_found}
          helper="In workspace catalog"
          icon={Sparkles}
        />
      </div>

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="border-b border-line px-5 py-4">
          <h2 className="flex items-center gap-2 text-base font-semibold">
            <Bot className="h-4 w-4 text-spruce" aria-hidden="true" />
            Agent performance
          </h2>
          <p className="mt-1 text-sm text-muted">Guild AI tracks every autonomous agent run.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[880px] text-left text-sm">
            <thead className="border-b border-line text-xs uppercase text-muted">
              <tr>
                <th className="px-5 py-3 font-semibold">Agent</th>
                <th className="px-5 py-3 font-semibold">Runs</th>
                <th className="px-5 py-3 font-semibold">Success</th>
                <th className="px-5 py-3 font-semibold">Runtime</th>
                <th className="px-5 py-3 font-semibold">Actions</th>
                <th className="px-5 py-3 font-semibold">Last run</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {activity.agents.map((agent) => (
                <tr key={agent.agent_name}>
                  <td className="px-5 py-4 font-medium">
                    {AGENT_LABELS[agent.agent_name] ?? agent.agent_name}
                  </td>
                  <td className="px-5 py-4">{agent.total_runs}</td>
                  <td className="px-5 py-4">{percent(agent.success_rate)}</td>
                  <td className="px-5 py-4">{Math.round(agent.average_runtime_ms)} ms</td>
                  <td className="px-5 py-4">{agent.actions_completed}</td>
                  <td className="px-5 py-4 text-muted">{formatDate(agent.last_run_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="flex items-center gap-2 border-b border-line px-5 py-4">
          <Activity className="h-4 w-4 text-spruce" aria-hidden="true" />
          <h2 className="text-base font-semibold">Guild AI run log</h2>
        </div>
        <div className="divide-y divide-line">
          {activity.recent_actions.map((log) => (
            <div key={log.id} className="grid gap-2 px-5 py-4 md:grid-cols-[1fr_auto]">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium">{AGENT_LABELS[log.agent_name] ?? log.agent_name}</p>
                  <StatusPill status={log.status} />
                  <span className="text-xs text-muted">{log.action_type}</span>
                </div>
                <p className="mt-2 text-sm text-muted">{log.output_summary ?? log.input_summary}</p>
                {log.metadata.guild_run_id ? (
                  <p className="mt-1 text-xs text-muted">Guild: {String(log.metadata.guild_run_id)}</p>
                ) : null}
              </div>
              <div className="text-right text-xs text-muted">
                <p>{formatDate(log.created_at)}</p>
                {log.metadata.runtime_ms ? <p>{String(log.metadata.runtime_ms)} ms</p> : null}
              </div>
            </div>
          ))}
        </div>
      </section>

      {openuiEnabled && openuiComponents?.length ? (
        <OpenUIRenderer components={openuiComponents} />
      ) : openuiEnabled ? (
        <section className="rounded-lg border border-dashed border-line bg-panel p-5 text-sm text-muted shadow-soft">
          OpenUI layout is enabled but no components were returned.
        </section>
      ) : (
        <section className="rounded-lg border border-dashed border-line bg-panel p-5 text-sm text-muted shadow-soft">
          OpenUI is disabled in backend config (<code className="text-xs">OPENUI_ENABLED=false</code>
          ).
        </section>
      )}
    </div>
  );
}

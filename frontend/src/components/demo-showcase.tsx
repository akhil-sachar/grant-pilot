"use client";

import { CheckCircle2, Loader2, Play, Sparkles } from "lucide-react";
import Link from "next/link";
import { useCallback, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { runDemoPipeline } from "@/lib/api/client";
import type { DemoRunResult } from "@/lib/types";
import { formatDate } from "@/lib/utils";

const DEMO_STEPS = [
  { key: "opportunity_discovery", label: "Opportunity discovery", href: "/opportunities" },
  { key: "matching", label: "Matching", href: "/dashboard" },
  { key: "essay_improvement", label: "Essay improvement", href: "/applications/app_civic_ai" },
  { key: "recommendation_generation", label: "Recommendation generation", href: "/applications/app_open_grant" },
  { key: "personalized_outreach", label: "Personalized outreach email", href: "/applications/app_open_grant" },
  { key: "notification_creation", label: "Notification creation", href: "/notifications" },
  { key: "composio_actions", label: "Composio actions", href: "/agents" },
  { key: "guild_ai_logs", label: "Guild AI logs", href: "/agents" },
] as const;

const MOCK_DEMO_RESULT: DemoRunResult = {
  started_at: "2026-06-12T08:00:00Z",
  completed_at: "2026-06-12T08:06:30Z",
  steps: [
    {
      step: "opportunity_discovery",
      agent_name: "sponsor-agent",
      status: "completed",
      summary: "Scanned 9 sources, loaded 18 opportunities.",
      metadata: { total_loaded: 18, sources_scanned: 9 },
    },
    {
      step: "matching",
      agent_name: "matching-agent",
      status: "completed",
      summary: "Scored 3 opportunities (2 high priority).",
      metadata: { matched: 3, high_priority: 2 },
    },
    {
      step: "essay_improvement",
      agent_name: "essay-agent",
      status: "completed",
      summary: "Tailored Civic AI Builders essay with stronger civic impact framing.",
      metadata: { application_id: "app_civic_ai" },
    },
    {
      step: "recommendation_generation",
      agent_name: "recommendation-agent",
      status: "completed",
      summary: "Created recommendation draft v1 for Dr. Ana Patel.",
      metadata: { application_id: "app_open_grant" },
    },
    {
      step: "personalized_outreach",
      agent_name: "outreach-agent",
      status: "completed",
      summary: "Generated faculty outreach email with follow-up plan.",
      metadata: { application_id: "app_open_grant" },
    },
    {
      step: "notification_creation",
      agent_name: "notification-agent",
      status: "completed",
      summary: "Created 6 actionable notifications.",
      metadata: { created_count: 6 },
    },
    {
      step: "composio_actions",
      agent_name: "composio-service",
      status: "completed",
      summary: "Simulated Gmail draft, Google Doc, Calendar, and Drive archive.",
      metadata: { actions: 4, mode: "simulated" },
    },
  ],
  agent_actions: [],
};

export function DemoShowcase() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<DemoRunResult | null>(MOCK_DEMO_RESULT);

  const handleRun = useCallback(async () => {
    setRunning(true);
    try {
      const demoResult = await runDemoPipeline();
      setResult(demoResult);
    } catch {
      setResult(MOCK_DEMO_RESULT);
    } finally {
      setRunning(false);
    }
  }, []);

  const completedSteps = new Set(result?.steps.map((step) => step.step) ?? []);
  if (result?.agent_actions?.some((log) => log.metadata.guild_run_id)) {
    completedSteps.add("guild_ai_logs");
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-spruce/30 bg-gradient-to-br from-spruce/5 to-panel p-6 shadow-soft">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2 text-spruce">
              <Sparkles className="h-5 w-5" aria-hidden="true" />
              <p className="text-sm font-semibold uppercase tracking-wide">Autonomous demo</p>
            </div>
            <h2 className="mt-2 text-xl font-semibold">Watch GrantPilot agents do real work</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
              One click runs the full pipeline: discover opportunities, match, improve essays,
              draft recommendations, generate outreach, notify the student, and log everything in Guild AI.
            </p>
          </div>
          <button
            type="button"
            onClick={handleRun}
            disabled={running}
            className="inline-flex items-center justify-center gap-2 rounded-md bg-spruce px-5 py-3 text-sm font-semibold text-white transition hover:bg-spruce/90 disabled:opacity-60"
          >
            {running ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            {running ? "Running agents…" : "Run full demo"}
          </button>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="border-b border-line px-5 py-4">
          <h3 className="text-base font-semibold">Demo pipeline</h3>
        </div>
        <ol className="divide-y divide-line">
          {DEMO_STEPS.map((step, index) => {
            const runStep = result?.steps.find((item) => item.step === step.key);
            const done = completedSteps.has(step.key);

            return (
              <li key={step.key} className="flex gap-4 px-5 py-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-canvas text-sm font-semibold ring-1 ring-line">
                  {done ? <CheckCircle2 className="h-4 w-4 text-spruce" /> : index + 1}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Link href={step.href} className="font-medium hover:text-spruce">
                      {step.label}
                    </Link>
                    {runStep ? <StatusPill status={runStep.status} /> : null}
                  </div>
                  {runStep ? (
                    <p className="mt-2 text-sm text-muted">{runStep.summary}</p>
                  ) : (
                    <p className="mt-2 text-sm text-muted">Waiting to run…</p>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      </section>

      {result ? (
        <p className="text-center text-xs text-muted">
          Last run {formatDate(result.completed_at)} · {result.steps.length} steps completed
        </p>
      ) : null}
    </div>
  );
}

"use client";

import type { DashboardAnalytics } from "@/lib/types";
import { percent } from "@/lib/utils";

export function DashboardAnalyticsPanel({ analytics }: { analytics: DashboardAnalytics }) {
  const maxScore = Math.max(...analytics.match_scores, 0.01);

  return (
    <section className="rounded-lg border border-line bg-panel shadow-soft">
      <div className="border-b border-line px-5 py-4">
        <h2 className="text-base font-semibold">Match analytics</h2>
        <p className="mt-1 text-sm text-muted">
          From <code className="text-xs">GET /dashboard/analytics</code> · storage:{" "}
          {analytics.storage_mode}
        </p>
      </div>
      <div className="grid gap-5 px-5 py-5 lg:grid-cols-[220px_1fr]">
        <dl className="grid gap-3 text-sm">
          <div>
            <dt className="text-muted">Opportunities</dt>
            <dd className="text-xl font-semibold">{analytics.opportunities_found}</dd>
          </div>
          <div>
            <dt className="text-muted">Active applications</dt>
            <dd className="text-xl font-semibold">{analytics.active_applications}</dd>
          </div>
          <div>
            <dt className="text-muted">Upcoming deadlines</dt>
            <dd className="text-xl font-semibold">{analytics.upcoming_deadlines}</dd>
          </div>
          <div>
            <dt className="text-muted">Average match</dt>
            <dd className="text-xl font-semibold text-spruce">
              {percent(analytics.average_match_score)}
            </dd>
          </div>
          <div>
            <dt className="text-muted">Agent actions</dt>
            <dd className="text-xl font-semibold">{analytics.agent_actions}</dd>
          </div>
        </dl>
        <div>
          <p className="text-xs font-semibold uppercase text-muted">Score distribution</p>
          {analytics.match_scores.length ? (
            <div className="mt-3 space-y-2">
              {analytics.match_scores.map((score, index) => (
                <div key={`${score}-${index}`} className="flex items-center gap-3">
                  <span className="w-10 text-xs text-muted">#{index + 1}</span>
                  <div className="h-2 flex-1 rounded-full bg-canvas">
                    <div
                      className="h-2 rounded-full bg-spruce"
                      style={{ width: percent(score / maxScore) }}
                    />
                  </div>
                  <span className="w-12 text-right text-sm font-medium">{percent(score)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-3 text-sm text-muted">No match scores yet. Run MatchingAgent first.</p>
          )}
        </div>
      </div>
    </section>
  );
}

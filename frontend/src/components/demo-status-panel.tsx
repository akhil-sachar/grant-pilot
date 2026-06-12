"use client";

import { useEffect, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { getDemoStatus } from "@/lib/api/client";
import type { DemoStatus } from "@/lib/types";

export function DemoStatusPanel() {
  const [status, setStatus] = useState<DemoStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void getDemoStatus()
      .then(setStatus)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load demo status"));
  }, []);

  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  if (!status) {
    return null;
  }

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <h2 className="text-base font-semibold">Backend demo configuration</h2>
      <p className="mt-1 text-sm text-muted">
        From <code className="text-xs">GET /demo/status</code>. The demo pipeline requires{" "}
        <code className="text-xs">DEMO_MODE=true</code> on the API.
      </p>
      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div className="flex items-center justify-between gap-3 rounded-md border border-line bg-white px-3 py-2">
          <dt className="text-muted">Demo mode</dt>
          <dd>
            <StatusPill status={status.demo_mode ? "active" : "inactive"} />
          </dd>
        </div>
        <div className="flex items-center justify-between gap-3 rounded-md border border-line bg-white px-3 py-2">
          <dt className="text-muted">Auto-run on startup</dt>
          <dd>
            <StatusPill status={status.demo_auto_run ? "active" : "inactive"} />
          </dd>
        </div>
        <div className="flex items-center justify-between gap-3 rounded-md border border-line bg-white px-3 py-2">
          <dt className="text-muted">Guild AI</dt>
          <dd>
            <StatusPill status={status.guild_ai_enabled ? "active" : "inactive"} />
          </dd>
        </div>
        <div className="flex items-center justify-between gap-3 rounded-md border border-line bg-white px-3 py-2">
          <dt className="text-muted">OpenUI</dt>
          <dd>
            <StatusPill status={status.openui_enabled ? "active" : "inactive"} />
          </dd>
        </div>
      </dl>
    </section>
  );
}

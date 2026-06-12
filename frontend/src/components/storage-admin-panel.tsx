"use client";

import { Database, Loader2, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import {
  getStorageHealth,
  initializeStorage,
  loadSampleData,
} from "@/lib/api/client";
import type { IngestionRun, StorageHealth } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export function StorageAdminPanel({
  ingestionRuns,
}: {
  ingestionRuns: IngestionRun[];
}) {
  const [health, setHealth] = useState<StorageHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const next = await getStorageHealth();
      setHealth(next);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load storage health");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function runAction(action: "initialize" | "sample") {
    setBusy(action);
    setMessage(null);
    setError(null);
    try {
      if (action === "initialize") {
        const result = await initializeStorage();
        setHealth(result);
        setMessage("Storage initialized.");
      } else {
        const run = await loadSampleData();
        setMessage(`Sample data loaded (${run.records_loaded} records).`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Storage action failed");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-4">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-spruce" aria-hidden="true" />
            <h2 className="text-base font-semibold">Storage admin</h2>
          </div>
          <button
            type="button"
            onClick={() => void refresh()}
            className="inline-flex items-center gap-1 text-sm text-muted hover:text-spruce"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
        </div>
        <div className="space-y-4 px-5 py-5 text-sm">
          {loading && !health ? (
            <div className="flex items-center gap-2 text-muted">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading storage health…
            </div>
          ) : health ? (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <StatusPill status={health.storage_mode} />
                {health.primary_available ? (
                  <StatusPill status="active" />
                ) : (
                  <StatusPill status="degraded" />
                )}
              </div>
              <dl className="grid gap-2">
                <div className="flex justify-between gap-4">
                  <dt className="text-muted">Primary</dt>
                  <dd className="font-medium">{health.primary ?? "none"}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted">Fallback enabled</dt>
                  <dd className="font-medium">{health.fallback_enabled ? "Yes" : "No"}</dd>
                </div>
                {health.last_error ? (
                  <div>
                    <dt className="text-muted">Last error</dt>
                    <dd className="mt-1 text-red-600">{health.last_error}</dd>
                  </div>
                ) : null}
              </dl>
            </>
          ) : null}
          <div className="flex flex-wrap gap-2 pt-2">
            <button
              type="button"
              disabled={busy !== null}
              onClick={() => void runAction("initialize")}
              className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold shadow-soft transition hover:border-spruce hover:text-spruce disabled:opacity-60"
            >
              {busy === "initialize" ? "Initializing…" : "Initialize storage"}
            </button>
            <button
              type="button"
              disabled={busy !== null}
              onClick={() => void runAction("sample")}
              className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold shadow-soft transition hover:border-spruce hover:text-spruce disabled:opacity-60"
            >
              {busy === "sample" ? "Loading…" : "Load sample data"}
            </button>
          </div>
          {message ? <p className="text-spruce">{message}</p> : null}
          {error ? <p className="text-red-600">{error}</p> : null}
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-base font-semibold">Ingestion runs</h2>
          <p className="mt-1 text-sm text-muted">Recent SponsorAgent funding ingestion history.</p>
        </div>
        <div className="divide-y divide-line">
          {ingestionRuns.length ? (
            ingestionRuns.map((run) => (
              <div key={run.id} className="px-5 py-4 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium">{run.source_name}</span>
                  <StatusPill status={run.status} />
                </div>
                <p className="mt-2 text-muted">
                  {run.records_loaded}/{run.records_seen} records loaded
                </p>
                <p className="mt-1 text-xs text-muted">
                  {formatDate(run.started_at)}
                  {run.completed_at ? ` → ${formatDate(run.completed_at)}` : ""}
                </p>
                {run.error_message ? (
                  <p className="mt-2 text-red-600">{run.error_message}</p>
                ) : null}
              </div>
            ))
          ) : (
            <p className="px-5 py-4 text-sm text-muted">No ingestion runs yet.</p>
          )}
        </div>
      </section>
    </div>
  );
}

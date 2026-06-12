"use client";

import { Loader2, Radio, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import {
  getSponsorScanStatus,
  triggerSponsorScan,
  triggerSponsorScanSource,
} from "@/lib/api/client";
import type { SponsorScanStatus } from "@/lib/types";
import { formatDate, statusLabel } from "@/lib/utils";

const POLL_INTERVAL_MS = 5000;

export function ScanStatusPanel() {
  const [status, setStatus] = useState<SponsorScanStatus | null>(null);
  const [isTriggering, setIsTriggering] = useState(false);
  const [scanningSource, setScanningSource] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const next = await getSponsorScanStatus();
      setStatus(next);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load scan status");
    }
  }, []);

  useEffect(() => {
    void refresh();
    const interval = setInterval(() => {
      void refresh();
    }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [refresh]);

  async function handleScanNow() {
    setIsTriggering(true);
    try {
      await triggerSponsorScan();
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setIsTriggering(false);
    }
  }

  async function handleScanSource(sourceName: string) {
    setScanningSource(sourceName);
    try {
      await triggerSponsorScanSource(sourceName);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Source scan failed");
    } finally {
      setScanningSource(null);
    }
  }

  if (!status && !error) {
    return (
      <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
        <div className="flex items-center gap-2 text-sm text-muted">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          Loading scan status…
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Radio
              className={`h-4 w-4 ${status?.is_scanning ? "animate-pulse text-spruce" : "text-muted"}`}
              aria-hidden="true"
            />
            <h2 className="text-base font-semibold">SponsorAgent Scan Status</h2>
            {status?.is_scanning ? (
              <StatusPill status="in_progress" />
            ) : (
              <StatusPill status="active" />
            )}
          </div>
          <p className="mt-1 text-sm text-muted">
            {status?.is_scanning
              ? "Scanning funding sources in the background…"
              : `Monitoring ${status?.sources.length ?? 0} sources · ${status?.total_opportunities ?? 0} opportunities indexed`}
          </p>
          <p className="mt-1 text-xs text-muted">
            {status?.last_full_scan_at
              ? `Last scan ${formatDate(status.last_full_scan_at, "Never")}`
              : "No full scan completed yet"}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void handleScanNow()}
          disabled={isTriggering || status?.is_scanning}
          className="inline-flex items-center gap-2 self-start rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink shadow-soft transition hover:border-spruce hover:text-spruce disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isTriggering || status?.is_scanning ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
          )}
          Scan all sources
        </button>
      </div>

      {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}

      {status ? (
        <div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {status.sources.map((source) => (
            <div
              key={source.source_name}
              className="rounded-md border border-line bg-white px-3 py-2 text-sm"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium">{source.display_name}</span>
                <StatusPill status={source.status} />
              </div>
              <p className="mt-1 text-xs text-muted">
                {statusLabel(source.category)} · {source.opportunities_found} found
              </p>
              <button
                type="button"
                onClick={() => void handleScanSource(source.source_name)}
                disabled={
                  scanningSource === source.source_name ||
                  isTriggering ||
                  status.is_scanning
                }
                className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-spruce hover:underline disabled:opacity-60"
              >
                {scanningSource === source.source_name ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <RefreshCw className="h-3 w-3" />
                )}
                Scan source
              </button>
            </div>
          ))}
        </div>
      ) : null}

      {status?.recent_ingestion_runs.length ? (
        <div className="mt-5 border-t border-line pt-4">
          <p className="text-xs font-semibold uppercase text-muted">Recent ingestion runs</p>
          <div className="mt-2 space-y-2">
            {status.recent_ingestion_runs.slice(0, 5).map((run) => (
              <div
                key={run.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-canvas px-3 py-2 text-xs"
              >
                <span className="font-medium">{run.source_name}</span>
                <span className="text-muted">
                  {run.records_loaded}/{run.records_seen} loaded
                </span>
                <StatusPill status={run.status} />
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}

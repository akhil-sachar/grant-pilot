"use client";

import { Loader2, Target } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { triggerMatching } from "@/lib/api/client";

export function MatchingActions({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleRunMatching() {
    setRunning(true);
    setError(null);
    setMessage(null);
    try {
      const result = await triggerMatching();
      setMessage(result.summary);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Matching failed");
    } finally {
      setRunning(false);
    }
  }

  if (compact) {
    return (
      <div className="flex flex-col items-end gap-2">
        <button
          type="button"
          onClick={() => void handleRunMatching()}
          disabled={running}
          className="inline-flex items-center gap-2 rounded-md bg-spruce px-4 py-2 text-sm font-semibold text-white transition hover:bg-spruce/90 disabled:opacity-60"
        >
          {running ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Target className="h-4 w-4" aria-hidden="true" />
          )}
          Run matching
        </button>
        {message ? <p className="max-w-xs text-right text-xs text-muted">{message}</p> : null}
        {error ? <p className="max-w-xs text-right text-xs text-red-600">{error}</p> : null}
      </div>
    );
  }

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-base font-semibold">MatchingAgent</h2>
          <p className="mt-1 text-sm text-muted">
            Score all opportunities against your profile and refresh match rankings.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void handleRunMatching()}
          disabled={running}
          className="inline-flex items-center gap-2 self-start rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink shadow-soft transition hover:border-spruce hover:text-spruce disabled:cursor-not-allowed disabled:opacity-60"
        >
          {running ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Target className="h-4 w-4" aria-hidden="true" />
          )}
          Run matching
        </button>
      </div>
      {message ? <p className="mt-3 text-sm text-spruce">{message}</p> : null}
      {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
    </section>
  );
}

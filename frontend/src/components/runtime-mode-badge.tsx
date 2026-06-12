"use client";

import { appConfig } from "@/lib/config";

export function RuntimeModeBadge({
  backendDemoMode,
  openaiEnabled,
}: {
  backendDemoMode: boolean;
  openaiEnabled: boolean;
}) {
  const frontendMock = appConfig.demoMode;

  return (
    <div className="flex flex-wrap gap-1.5">
      <span
        className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
          frontendMock
            ? "bg-amber-100 text-amber-900"
            : "bg-emerald-100 text-emerald-900"
        }`}
      >
        UI {frontendMock ? "mock" : "live API"}
      </span>
      <span
        className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
          backendDemoMode ? "bg-sky-100 text-sky-900" : "bg-slate-100 text-slate-700"
        }`}
      >
        API {backendDemoMode ? "demo" : "production"}
      </span>
      {openaiEnabled ? (
        <span className="rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-violet-900">
          OpenAI
        </span>
      ) : null}
    </div>
  );
}

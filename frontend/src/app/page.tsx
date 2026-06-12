import {
  ArrowRight,
  Bell,
  FileText,
  LayoutDashboard,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import Link from "next/link";

import { appConfig } from "@/lib/config";

const stages = [
  {
    label: "Profile",
    value: "88%",
    icon: ShieldCheck,
  },
  {
    label: "Documents",
    value: "2 ready",
    icon: FileText,
  },
  {
    label: "Matches",
    value: "3 active",
    icon: Sparkles,
  },
  {
    label: "Alerts",
    value: "2 unread",
    icon: Bell,
  },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-canvas text-ink">
      <section className="relative overflow-hidden bg-[#12382f] text-white">
        <div className="mx-auto flex min-h-[82svh] max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
          <header className="flex items-center justify-between gap-4">
            <Link href="/" className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-md bg-white text-[#12382f]">
                <LayoutDashboard className="h-5 w-5" aria-hidden="true" />
              </span>
              <span className="font-semibold">{appConfig.appName}</span>
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-semibold text-[#12382f] transition hover:bg-[#e8f5ef]"
            >
              Open dashboard
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </header>

          <div className="flex flex-1 flex-col justify-center py-12">
            <p className="text-sm font-semibold uppercase tracking-normal text-[#a7f3d0]">
              Hackathon foundation
            </p>
            <h1 className="mt-4 max-w-4xl text-5xl font-semibold tracking-normal sm:text-6xl lg:text-7xl">
              GrantPilot
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-[#d7ede5]">
              Autonomous scholarship and grant applications, starting with a clean
              human-reviewed workspace for profiles, documents, matches, deadlines,
              drafts, and notifications.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-md bg-white px-5 py-3 text-sm font-semibold text-[#12382f] transition hover:bg-[#e8f5ef]"
              >
                View demo
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
              <Link
                href="/opportunities"
                className="inline-flex items-center gap-2 rounded-md border border-white/30 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                Browse opportunities
              </Link>
            </div>

            <div className="mt-12 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {stages.map((stage) => {
                const Icon = stage.icon;
                return (
                  <div
                    key={stage.label}
                    className="rounded-lg border border-white/15 bg-white/[0.08] p-4 backdrop-blur"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm text-[#d7ede5]">{stage.label}</p>
                      <Icon className="h-4 w-4 text-[#a7f3d0]" aria-hidden="true" />
                    </div>
                    <p className="mt-3 text-2xl font-semibold">{stage.value}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-4 py-10 sm:px-6 lg:grid-cols-3 lg:px-8">
        {[
          "Typed FastAPI contracts",
          "Mock-first Next.js pages",
          "ClickHouse-ready schemas",
        ].map((item) => (
          <div key={item} className="rounded-lg border border-line bg-panel p-5 shadow-soft">
            <p className="text-sm font-semibold text-spruce">{item}</p>
            <p className="mt-2 text-sm leading-6 text-muted">
              Built as a replaceable foundation for real storage, syncs, and agents.
            </p>
          </div>
        ))}
      </section>
    </main>
  );
}

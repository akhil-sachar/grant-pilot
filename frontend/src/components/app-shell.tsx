import { Bell, Command, Search } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { SidebarNav } from "@/components/sidebar-nav";
import { appConfig } from "@/lib/config";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-canvas text-ink lg:grid lg:grid-cols-[264px_1fr]">
      <aside className="hidden border-r border-line bg-panel lg:flex lg:min-h-screen lg:flex-col">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-spruce text-white">
            <Command className="h-5 w-5" aria-hidden="true" />
          </div>
          <Link href="/dashboard" className="min-w-0">
            <p className="truncate text-lg font-semibold">{appConfig.appName}</p>
            <p className="text-xs text-muted">Demo workspace</p>
          </Link>
        </div>
        <SidebarNav />
        <div className="mt-auto border-t border-line px-5 py-4 text-xs text-muted">
          <p className="font-medium text-ink">Agent status</p>
          <p>No autonomous agents enabled</p>
        </div>
      </aside>

      <div className="min-w-0">
        <header className="sticky top-0 z-10 border-b border-line bg-panel/95 backdrop-blur">
          <div className="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
            <Link href="/dashboard" className="flex items-center gap-2 lg:hidden">
              <span className="flex h-9 w-9 items-center justify-center rounded-md bg-spruce text-white">
                <Command className="h-5 w-5" aria-hidden="true" />
              </span>
              <span className="font-semibold">{appConfig.appName}</span>
            </Link>
            <div className="ml-auto flex items-center gap-2">
              <div className="hidden h-10 items-center gap-2 rounded-md border border-line bg-canvas px-3 text-sm text-muted sm:flex">
                <Search className="h-4 w-4" aria-hidden="true" />
                <span>Search</span>
              </div>
              <Link
                href="/notifications"
                className="flex h-10 w-10 items-center justify-center rounded-md border border-line bg-panel text-muted transition hover:border-spruce hover:text-spruce"
                aria-label="Notifications"
              >
                <Bell className="h-4 w-4" aria-hidden="true" />
              </Link>
            </div>
          </div>
          <div className="border-t border-line px-2 py-2 lg:hidden">
            <SidebarNav mobile />
          </div>
        </header>

        <main className="px-4 py-6 sm:px-6 lg:px-8 lg:py-8">{children}</main>
      </div>
    </div>
  );
}


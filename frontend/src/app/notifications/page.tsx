import { BellRing, CheckCircle2 } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { getNotifications } from "@/lib/api/client";
import { formatDate } from "@/lib/utils";

export default async function NotificationsPage() {
  const notifications = await getNotifications();

  return (
    <AppShell>
      <PageHeader
        title="Notifications"
        description="Deadlines, document reviews, and system updates for the current workspace."
      />

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="divide-y divide-line">
          {notifications.map((notification) => (
            <div key={notification.id} className="grid gap-4 px-5 py-5 md:grid-cols-[auto_1fr_auto]">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-canvas text-spruce">
                {notification.is_read ? (
                  <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <BellRing className="h-5 w-5" aria-hidden="true" />
                )}
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="font-semibold">{notification.title}</h2>
                  <StatusPill status={notification.notification_type} />
                </div>
                <p className="mt-2 text-sm leading-6 text-muted">{notification.message}</p>
              </div>
              <div className="text-sm text-muted md:text-right">
                {formatDate(notification.created_at)}
              </div>
            </div>
          ))}
        </div>
      </section>
    </AppShell>
  );
}


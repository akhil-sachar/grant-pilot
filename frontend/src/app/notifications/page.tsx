import { AppShell } from "@/components/app-shell";
import { NotificationCenter } from "@/components/notification-center";
import { PageHeader } from "@/components/page-header";
import { getNotifications } from "@/lib/api/client";

export default async function NotificationsPage() {
  const notifications = await getNotifications();

  return (
    <AppShell>
      <PageHeader
        title="Notifications"
        description="Opportunity alerts, deadline reminders, and draft readiness updates from NotificationAgent."
      />

      <NotificationCenter initialNotifications={notifications} />
    </AppShell>
  );
}

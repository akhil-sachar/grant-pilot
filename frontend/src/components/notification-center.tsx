"use client";

import { BellRing, CheckCircle2, Filter, Loader2, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import {
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  runNotificationAgent,
} from "@/lib/api/client";
import type { Notification } from "@/lib/types";
import { formatDate } from "@/lib/utils";

const TYPE_OPTIONS = [
  { value: "all", label: "All types" },
  { value: "new_opportunity", label: "New Opportunity" },
  { value: "high_match", label: "High Match" },
  { value: "deadline_approaching", label: "Deadline Approaching" },
  { value: "missing_document", label: "Missing Documents" },
  { value: "essay_ready", label: "Essay Ready" },
  { value: "recommendation_ready", label: "Recommendation Draft Ready" },
  { value: "email_draft_ready", label: "Email Draft Ready" },
] as const;

const PRIORITY_OPTIONS = [
  { value: "all", label: "All priorities" },
  { value: "urgent", label: "Urgent" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
] as const;

const SORT_OPTIONS = [
  { value: "created_desc", label: "Newest first" },
  { value: "created_asc", label: "Oldest first" },
  { value: "priority_desc", label: "Priority high → low" },
  { value: "priority_asc", label: "Priority low → high" },
] as const;

const PRIORITY_RANK: Record<string, number> = {
  urgent: 4,
  high: 3,
  medium: 2,
  low: 1,
};

type ReadFilter = "all" | "unread" | "read";

export function NotificationCenter({ initialNotifications }: { initialNotifications: Notification[] }) {
  const [notifications, setNotifications] = useState(initialNotifications);
  const [typeFilter, setTypeFilter] = useState<(typeof TYPE_OPTIONS)[number]["value"]>("all");
  const [priorityFilter, setPriorityFilter] =
    useState<(typeof PRIORITY_OPTIONS)[number]["value"]>("all");
  const [readFilter, setReadFilter] = useState<ReadFilter>("all");
  const [sort, setSort] = useState<(typeof SORT_OPTIONS)[number]["value"]>("created_desc");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsRefreshing(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (typeFilter !== "all") params.set("type", typeFilter);
      if (priorityFilter !== "all") params.set("priority", priorityFilter);
      if (readFilter === "unread") params.set("is_read", "false");
      if (readFilter === "read") params.set("is_read", "true");
      params.set("sort", sort);
      const next = await getNotifications(params.toString());
      setNotifications(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load notifications");
    } finally {
      setIsRefreshing(false);
    }
  }, [typeFilter, priorityFilter, readFilter, sort]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const filteredLocally = useMemo(() => {
    let items = [...notifications];
    if (typeFilter !== "all") {
      items = items.filter((item) => item.notification_type === typeFilter);
    }
    if (priorityFilter !== "all") {
      items = items.filter((item) => item.priority === priorityFilter);
    }
    if (readFilter === "unread") {
      items = items.filter((item) => !item.is_read);
    }
    if (readFilter === "read") {
      items = items.filter((item) => item.is_read);
    }
    if (sort === "created_asc") {
      return items.sort((a, b) => a.created_at.localeCompare(b.created_at));
    }
    if (sort === "priority_desc") {
      return items.sort(
        (a, b) =>
          (PRIORITY_RANK[b.priority] ?? 0) - (PRIORITY_RANK[a.priority] ?? 0) ||
          b.created_at.localeCompare(a.created_at),
      );
    }
    if (sort === "priority_asc") {
      return items.sort(
        (a, b) =>
          (PRIORITY_RANK[a.priority] ?? 0) - (PRIORITY_RANK[b.priority] ?? 0) ||
          a.created_at.localeCompare(b.created_at),
      );
    }
    return items.sort((a, b) => b.created_at.localeCompare(a.created_at));
  }, [notifications, typeFilter, priorityFilter, readFilter, sort]);

  async function handleMarkRead(id: string) {
    const updated = await markNotificationRead(id);
    setNotifications((current) =>
      current.map((item) => (item.id === id ? updated : item)),
    );
  }

  async function handleMarkAllRead() {
    const updated = await markAllNotificationsRead();
    const updatedIds = new Set(updated.map((item) => item.id));
    setNotifications((current) =>
      current.map((item) =>
        updatedIds.has(item.id) ? { ...item, is_read: true } : item,
      ),
    );
  }

  async function handleRunAgent() {
    setIsRefreshing(true);
    try {
      await runNotificationAgent();
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Notification scan failed");
    } finally {
      setIsRefreshing(false);
    }
  }

  return (
    <section className="rounded-lg border border-line bg-panel shadow-soft">
      <div className="flex flex-col gap-4 border-b border-line px-5 py-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-base font-semibold">Notification Center</h2>
          <p className="mt-1 text-sm text-muted">
            NotificationAgent monitors opportunities, matches, deadlines, and draft readiness.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void handleRunAgent()}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold text-ink hover:border-spruce hover:text-spruce disabled:opacity-60"
          >
            {isRefreshing ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <RefreshCw className="h-4 w-4" aria-hidden="true" />
            )}
            Scan now
          </button>
          <button
            type="button"
            onClick={() => void handleMarkAllRead()}
            className="inline-flex items-center gap-2 rounded-md bg-spruce px-3 py-2 text-sm font-semibold text-white hover:bg-spruce/90"
          >
            <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
            Mark all read
          </button>
        </div>
      </div>

      <div className="grid gap-3 border-b border-line bg-canvas px-5 py-4 md:grid-cols-2 xl:grid-cols-4">
        <label className="text-sm">
          <span className="mb-1 flex items-center gap-1 text-xs font-semibold uppercase text-muted">
            <Filter className="h-3 w-3" aria-hidden="true" />
            Type
          </span>
          <select
            value={typeFilter}
            onChange={(event) =>
              setTypeFilter(event.target.value as typeof typeFilter)
            }
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
          >
            {TYPE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-xs font-semibold uppercase text-muted">Priority</span>
          <select
            value={priorityFilter}
            onChange={(event) =>
              setPriorityFilter(event.target.value as typeof priorityFilter)
            }
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
          >
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-xs font-semibold uppercase text-muted">Read status</span>
          <select
            value={readFilter}
            onChange={(event) => setReadFilter(event.target.value as ReadFilter)}
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
          >
            <option value="all">All</option>
            <option value="unread">Unread only</option>
            <option value="read">Read only</option>
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-xs font-semibold uppercase text-muted">Sort</span>
          <select
            value={sort}
            onChange={(event) => setSort(event.target.value as typeof sort)}
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
          >
            {SORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      {error ? <p className="px-5 pt-4 text-sm text-red-600">{error}</p> : null}

      <div className="divide-y divide-line">
        {filteredLocally.length === 0 ? (
          <p className="px-5 py-8 text-sm text-muted">No notifications match your filters.</p>
        ) : (
          filteredLocally.map((notification) => (
            <div
              key={notification.id}
              className={`grid gap-4 px-5 py-5 md:grid-cols-[auto_1fr_auto] ${
                notification.is_read ? "opacity-80" : "bg-white/40"
              }`}
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-canvas text-spruce">
                {notification.is_read ? (
                  <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <BellRing className="h-5 w-5" aria-hidden="true" />
                )}
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-semibold">{notification.title}</h3>
                  <StatusPill status={notification.notification_type} />
                  <StatusPill status={notification.priority} />
                </div>
                <p className="mt-2 text-sm leading-6 text-muted">{notification.message}</p>
                {notification.action_url ? (
                  <Link
                    href={notification.action_url}
                    className="mt-2 inline-flex text-sm font-semibold text-spruce hover:underline"
                  >
                    View details
                  </Link>
                ) : null}
              </div>
              <div className="flex flex-col items-start gap-2 text-sm md:items-end">
                <span className="text-muted">{formatDate(notification.created_at)}</span>
                {!notification.is_read ? (
                  <button
                    type="button"
                    onClick={() => void handleMarkRead(notification.id)}
                    className="font-semibold text-spruce hover:underline"
                  >
                    Mark read
                  </button>
                ) : (
                  <span className="text-muted">Read</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

import { clsx, type ClassValue } from "clsx";

export function cn(...values: ClassValue[]) {
  return clsx(values);
}

export function formatDate(value?: string | null, fallback = "No deadline") {
  if (!value) {
    return fallback;
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

export function formatCurrency(min?: number | null, max?: number | null) {
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

  if (min && max && min !== max) {
    return `${formatter.format(min)}-${formatter.format(max)}`;
  }
  if (max) {
    return formatter.format(max);
  }
  if (min) {
    return formatter.format(min);
  }
  return "Variable";
}

export function statusLabel(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function checklistProgress(items: { status: string }[]) {
  if (items.length === 0) {
    return 0;
  }
  return items.filter((item) => item.status === "done").length / items.length;
}

export function formatBytes(value: number) {
  if (value < 1024) {
    return `${value} B`;
  }
  const units = ["KB", "MB", "GB"];
  let size = value / 1024;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toFixed(size >= 10 ? 0 : 1)} ${units[unitIndex]}`;
}

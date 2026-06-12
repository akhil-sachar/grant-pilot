"use client";

import {
  Bell,
  BriefcaseBusiness,
  FileText,
  Home,
  LayoutDashboard,
  UserRound,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/profile", label: "Profile", icon: UserRound },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/opportunities", label: "Opportunities", icon: Home },
  { href: "/applications", label: "Applications", icon: BriefcaseBusiness },
  { href: "/notifications", label: "Notifications", icon: Bell },
] as const;

export function SidebarNav({ mobile = false }: { mobile?: boolean }) {
  const pathname = usePathname();

  return (
    <nav
      className={cn(
        mobile ? "flex gap-2 overflow-x-auto" : "flex flex-col gap-1 p-4",
      )}
      aria-label="Primary"
    >
      {navItems.map((item) => {
        const Icon = item.icon;
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition",
              mobile && "shrink-0",
              active
                ? "bg-spruce text-white shadow-soft"
                : "text-muted hover:bg-canvas hover:text-ink",
            )}
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}


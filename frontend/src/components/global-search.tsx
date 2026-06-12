"use client";

import { Search, X } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function GlobalSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      return;
    }
    router.push(`/search?q=${encodeURIComponent(trimmed)}`);
  }

  return (
    <form onSubmit={handleSubmit} className="hidden sm:block">
      <div className="flex h-10 items-center gap-2 rounded-md border border-line bg-canvas px-3 text-sm">
        <Search className="h-4 w-4 shrink-0 text-muted" aria-hidden="true" />
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search opportunities & applications"
          className="w-48 bg-transparent text-ink outline-none placeholder:text-muted lg:w-64"
          aria-label="Search workspace"
        />
        {query ? (
          <button
            type="button"
            onClick={() => setQuery("")}
            className="text-muted hover:text-ink"
            aria-label="Clear search"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        ) : null}
      </div>
    </form>
  );
}

export function MobileSearchLink() {
  return (
    <Link
      href="/search"
      className="flex h-10 w-10 items-center justify-center rounded-md border border-line bg-panel text-muted transition hover:border-spruce hover:text-spruce sm:hidden"
      aria-label="Search"
    >
      <Search className="h-4 w-4" />
    </Link>
  );
}

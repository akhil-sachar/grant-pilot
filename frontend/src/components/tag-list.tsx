export function TagList({ tags }: { tags: string[] }) {
  if (tags.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <span
          key={tag}
          className="rounded border border-line bg-canvas px-2 py-1 text-xs text-muted"
        >
          {tag}
        </span>
      ))}
    </div>
  );
}


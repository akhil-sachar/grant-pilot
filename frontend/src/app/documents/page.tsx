import { FilePlus2 } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { TagList } from "@/components/tag-list";
import { getDocuments } from "@/lib/api/client";
import { formatBytes, formatDate, statusLabel } from "@/lib/utils";

export default async function DocumentsPage() {
  const documents = await getDocuments();

  return (
    <AppShell>
      <PageHeader
        title="Documents"
        description="Application materials and parsed readiness states."
        action={
          <button className="inline-flex items-center gap-2 rounded-md bg-spruce px-4 py-2 text-sm font-semibold text-white shadow-soft transition hover:bg-[#06684b]">
            <FilePlus2 className="h-4 w-4" aria-hidden="true" />
            Add document
          </button>
        }
      />

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-line text-xs uppercase text-muted">
              <tr>
                <th className="px-5 py-3 font-semibold">File</th>
                <th className="px-5 py-3 font-semibold">Type</th>
                <th className="px-5 py-3 font-semibold">Status</th>
                <th className="px-5 py-3 font-semibold">Size</th>
                <th className="px-5 py-3 font-semibold">Uploaded</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {documents.map((document) => (
                <tr key={document.id}>
                  <td className="px-5 py-4">
                    <p className="font-medium">{document.file_name}</p>
                    <p className="mt-1 max-w-xl text-muted">
                      {document.extracted_text_preview ?? "No preview available"}
                    </p>
                    <div className="mt-3">
                      <TagList tags={document.tags} />
                    </div>
                  </td>
                  <td className="px-5 py-4 text-muted">{statusLabel(document.document_type)}</td>
                  <td className="px-5 py-4">
                    <StatusPill status={document.status} />
                  </td>
                  <td className="px-5 py-4 text-muted">{formatBytes(document.size_bytes)}</td>
                  <td className="px-5 py-4 text-muted">{formatDate(document.uploaded_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </AppShell>
  );
}


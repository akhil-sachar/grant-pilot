"use client";

import {
  FileText,
  History,
  Loader2,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import { useMemo, useRef, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { TagList } from "@/components/tag-list";
import {
  deleteDocument,
  getDocumentVersions,
  uploadDocument,
  uploadDocumentVersion,
} from "@/lib/api/client";
import type { DocumentVersion, UploadedDocument } from "@/lib/types";
import { cn, formatBytes, formatDate, statusLabel } from "@/lib/utils";

const documentTypes = [
  { value: "transcript", label: "Transcript" },
  { value: "resume", label: "Resume" },
  { value: "essay", label: "Personal Essay" },
  { value: "recommendation", label: "Recommendation Letter" },
];

export function DocumentVault({
  initialDocuments,
}: {
  initialDocuments: UploadedDocument[];
}) {
  const [documents, setDocuments] = useState(initialDocuments);
  const [selectedId, setSelectedId] = useState(initialDocuments[0]?.id ?? "");
  const [documentType, setDocumentType] = useState(documentTypes[0].value);
  const [dragActive, setDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const versionInputRef = useRef<HTMLInputElement>(null);

  const selectedDocument = useMemo(
    () => documents.find((document) => document.id === selectedId) ?? documents[0],
    [documents, selectedId],
  );

  async function handleFiles(fileList: FileList | null) {
    const file = fileList?.[0];
    if (!file) {
      return;
    }
    setError(null);
    setIsUploading(true);
    try {
      const uploaded = await uploadDocument(file, documentType);
      setDocuments((current) => [uploaded, ...current]);
      setSelectedId(uploaded.id);
      setVersions([]);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  async function handleVersionUpload(fileList: FileList | null) {
    const file = fileList?.[0];
    if (!file || !selectedDocument) {
      return;
    }
    setError(null);
    setIsUploading(true);
    try {
      const updated = await uploadDocumentVersion(selectedDocument.id, file);
      setDocuments((current) =>
        current.map((document) => (document.id === updated.id ? updated : document)),
      );
      setSelectedId(updated.id);
      setVersions([]);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Version upload failed");
    } finally {
      setIsUploading(false);
      if (versionInputRef.current) {
        versionInputRef.current.value = "";
      }
    }
  }

  async function loadVersions(documentId: string) {
    setSelectedId(documentId);
    setLoadingVersions(true);
    setError(null);
    try {
      setVersions(await getDocumentVersions(documentId));
    } catch (versionError) {
      setError(versionError instanceof Error ? versionError.message : "Could not load versions");
    } finally {
      setLoadingVersions(false);
    }
  }

  async function removeDocument(documentId: string) {
    setError(null);
    try {
      await deleteDocument(documentId);
      setDocuments((current) => current.filter((document) => document.id !== documentId));
      if (selectedId === documentId) {
        setSelectedId("");
        setVersions([]);
      }
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Delete failed");
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
        <div
          className={cn(
            "flex min-h-56 flex-col items-center justify-center rounded-lg border border-dashed border-line bg-canvas px-5 py-8 text-center transition",
            dragActive && "border-spruce bg-emerald-50",
          )}
          onDragOver={(event) => {
            event.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragActive(false);
            void handleFiles(event.dataTransfer.files);
          }}
        >
          <UploadCloud className="h-10 w-10 text-spruce" aria-hidden="true" />
          <h2 className="mt-4 text-lg font-semibold">Drop a PDF or text file</h2>
          <p className="mt-2 max-w-sm text-sm leading-6 text-muted">
            Transcripts, resumes, essays, and recommendation letters are extracted and
            stored for future application agents.
          </p>
          <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
            <select
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value)}
              className="h-10 rounded-md border border-line bg-panel px-3 text-sm"
            >
              {documentTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex h-10 items-center gap-2 rounded-md bg-spruce px-4 text-sm font-semibold text-white transition hover:bg-[#06684b]"
            >
              {isUploading ? (
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              ) : (
                <UploadCloud className="h-4 w-4" aria-hidden="true" />
              )}
              Upload
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf,text/plain,text/markdown,.pdf,.txt,.md"
              className="hidden"
              onChange={(event) => void handleFiles(event.target.files)}
            />
          </div>
        </div>

        {error ? (
          <div className="mt-4 flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <X className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            <span>{error}</span>
          </div>
        ) : null}

        <div className="mt-5 grid gap-3">
          {documents.map((document) => (
            <button
              key={document.id}
              type="button"
              onClick={() => void loadVersions(document.id)}
              className={cn(
                "w-full rounded-md border border-line bg-panel p-4 text-left transition hover:border-spruce",
                selectedDocument?.id === document.id && "border-spruce ring-1 ring-spruce",
              )}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="truncate font-medium">{document.file_name}</p>
                  <p className="mt-1 text-sm text-muted">
                    {statusLabel(document.document_type)} · v{document.version_number}
                  </p>
                </div>
                <StatusPill status={document.status} />
              </div>
              <p className="mt-3 line-clamp-2 text-sm leading-6 text-muted">
                {document.extracted_text_preview ?? "No extracted preview yet."}
              </p>
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-soft">
        {selectedDocument ? (
          <div>
            <div className="border-b border-line px-5 py-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <h2 className="truncate text-lg font-semibold">{selectedDocument.file_name}</h2>
                  <p className="mt-1 text-sm text-muted">
                    {formatBytes(selectedDocument.size_bytes)} · {formatDate(selectedDocument.updated_at)}
                  </p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <button
                    type="button"
                    onClick={() => versionInputRef.current?.click()}
                    className="inline-flex h-9 items-center gap-2 rounded-md border border-line px-3 text-sm font-semibold text-ink transition hover:border-spruce hover:text-spruce"
                  >
                    <History className="h-4 w-4" aria-hidden="true" />
                    New version
                  </button>
                  <button
                    type="button"
                    onClick={() => void removeDocument(selectedDocument.id)}
                    className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-line text-muted transition hover:border-red-300 hover:text-red-600"
                    aria-label="Delete document"
                  >
                    <Trash2 className="h-4 w-4" aria-hidden="true" />
                  </button>
                  <input
                    ref={versionInputRef}
                    type="file"
                    accept="application/pdf,text/plain,text/markdown,.pdf,.txt,.md"
                    className="hidden"
                    onChange={(event) => void handleVersionUpload(event.target.files)}
                  />
                </div>
              </div>
              <div className="mt-4">
                <TagList tags={selectedDocument.tags} />
              </div>
            </div>

            <div className="grid gap-0 lg:grid-cols-[1fr_280px]">
              <div className="p-5">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <FileText className="h-4 w-4 text-spruce" aria-hidden="true" />
                  Extracted text preview
                </div>
                <div className="mt-4 max-h-[520px] overflow-auto rounded-md border border-line bg-canvas p-4">
                  <pre className="whitespace-pre-wrap text-sm leading-6 text-ink">
                    {selectedDocument.extracted_text ||
                      selectedDocument.extracted_text_preview ||
                      "No extracted text available yet."}
                  </pre>
                </div>
              </div>

              <aside className="border-t border-line p-5 lg:border-l lg:border-t-0">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-sm font-semibold">Version history</h3>
                  {loadingVersions ? (
                    <Loader2 className="h-4 w-4 animate-spin text-muted" aria-hidden="true" />
                  ) : null}
                </div>
                <div className="mt-4 grid gap-3">
                  {(versions.length > 0 ? versions : []).map((version) => (
                    <div key={version.id} className="border-b border-line pb-3 last:border-b-0">
                      <p className="text-sm font-medium">Version {version.version_number}</p>
                      <p className="mt-1 text-xs text-muted">{formatDate(version.created_at)}</p>
                      <p className="mt-2 line-clamp-2 text-xs leading-5 text-muted">
                        {version.extracted_text_preview ?? version.file_name}
                      </p>
                    </div>
                  ))}
                  {versions.length === 0 && !loadingVersions ? (
                    <p className="text-sm leading-6 text-muted">
                      Select a document to load stored versions.
                    </p>
                  ) : null}
                </div>
              </aside>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-sm text-muted">No documents in the vault.</div>
        )}
      </section>
    </div>
  );
}


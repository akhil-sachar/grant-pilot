import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { getDocuments } from "@/lib/api/client";

import { DocumentVault } from "./vault";

export default async function DocumentsPage() {
  const documents = await getDocuments();

  return (
    <AppShell>
      <PageHeader
        title="Document Vault"
        description="Upload, preview, extract, and version application materials for future agents."
      />
      <DocumentVault initialDocuments={documents} />
    </AppShell>
  );
}


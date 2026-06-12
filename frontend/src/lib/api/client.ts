import { appConfig } from "@/lib/config";
import type {
  ApplicationBundle,
  DocumentVersion,
  DashboardResponse,
  GrantApplication,
  MatchResult,
  Notification,
  Opportunity,
  RuntimeConfig,
  UploadedDocument,
  UserProfile,
} from "@/lib/types";

import {
  mockApplicationBundles,
  mockApplications,
  mockDashboard,
  mockDocumentVersions,
  mockDocuments,
  mockMatches,
  mockNotifications,
  mockOpportunities,
  mockProfile,
  mockRuntimeConfig,
} from "./mock-data";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${appConfig.apiBaseUrl}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`GrantPilot API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function getRuntimeConfig(): Promise<RuntimeConfig> {
  if (appConfig.demoMode) {
    return mockRuntimeConfig;
  }
  return request<RuntimeConfig>("/config");
}

export async function getDashboard(): Promise<DashboardResponse> {
  if (appConfig.demoMode) {
    return mockDashboard;
  }
  return request<DashboardResponse>("/dashboard");
}

export async function getProfile(): Promise<UserProfile> {
  if (appConfig.demoMode) {
    return mockProfile;
  }
  return request<UserProfile>("/profile/me");
}

export async function updateProfile(payload: Partial<UserProfile>): Promise<UserProfile> {
  if (appConfig.demoMode) {
    return { ...mockProfile, ...payload };
  }
  const response = await fetch(`${appConfig.apiBaseUrl}/api/v1/profile/me`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Profile update failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<UserProfile>;
}

export async function getDocuments(): Promise<UploadedDocument[]> {
  if (appConfig.demoMode) {
    return mockDocuments;
  }
  return request<UploadedDocument[]>("/documents");
}

export async function getDocumentVersions(documentId: string): Promise<DocumentVersion[]> {
  if (appConfig.demoMode) {
    return mockDocumentVersions[documentId] ?? [];
  }
  return request<DocumentVersion[]>(`/documents/${documentId}/versions`);
}

export async function uploadDocument(
  file: File,
  documentType: string,
): Promise<UploadedDocument> {
  if (appConfig.demoMode) {
    const now = new Date().toISOString();
    const extractedText = await extractTextPreview(file);
    return {
      id: `doc_demo_${Date.now()}`,
      user_id: "usr_demo_001",
      file_name: file.name,
      document_type: documentType,
      storage_uri: `demo://${file.name}`,
      mime_type: file.type || "application/octet-stream",
      size_bytes: file.size,
      extracted_text: extractedText,
      extracted_text_preview: extractedText || "PDF uploaded. Backend extraction stores text for future agents.",
      current_version_id: `docver_demo_${Date.now()}`,
      version_number: 1,
      tags: [documentType],
      metadata: { demo_upload: true },
      status: "processed",
      uploaded_at: now,
      updated_at: now,
    };
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", documentType);
  formData.append("tags", documentType);
  const response = await fetch(`${appConfig.apiBaseUrl}/api/v1/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`Document upload failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<UploadedDocument>;
}

export async function uploadDocumentVersion(
  documentId: string,
  file: File,
): Promise<UploadedDocument> {
  if (appConfig.demoMode) {
    const now = new Date().toISOString();
    const extractedText = await extractTextPreview(file);
    const current = mockDocuments.find((document) => document.id === documentId);
    if (!current) {
      throw new Error(`Unknown mock document: ${documentId}`);
    }
    return {
      ...current,
      file_name: file.name,
      mime_type: file.type || current.mime_type,
      size_bytes: file.size,
      extracted_text: extractedText,
      extracted_text_preview: extractedText || current.extracted_text_preview,
      version_number: current.version_number + 1,
      current_version_id: `docver_demo_${Date.now()}`,
      updated_at: now,
    };
  }

  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(
    `${appConfig.apiBaseUrl}/api/v1/documents/${documentId}/versions`,
    {
      method: "POST",
      body: formData,
    },
  );
  if (!response.ok) {
    throw new Error(`Document version upload failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<UploadedDocument>;
}

export async function deleteDocument(documentId: string): Promise<void> {
  if (appConfig.demoMode) {
    return;
  }
  const response = await fetch(`${appConfig.apiBaseUrl}/api/v1/documents/${documentId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Document delete failed: ${response.status} ${response.statusText}`);
  }
}

export async function getOpportunities(): Promise<Opportunity[]> {
  if (appConfig.demoMode) {
    return mockOpportunities;
  }
  return request<Opportunity[]>("/opportunities");
}

export async function getMatches(): Promise<MatchResult[]> {
  if (appConfig.demoMode) {
    return mockMatches;
  }
  return request<MatchResult[]>("/matches");
}

export async function getApplications(): Promise<GrantApplication[]> {
  if (appConfig.demoMode) {
    return mockApplications;
  }
  return request<GrantApplication[]>("/applications");
}

export async function getApplicationBundle(id: string): Promise<ApplicationBundle> {
  if (appConfig.demoMode) {
    const bundle = mockApplicationBundles[id];
    if (!bundle) {
      throw new Error(`Unknown mock application: ${id}`);
    }
    return bundle;
  }
  return request<ApplicationBundle>(`/applications/${id}`);
}

export async function getNotifications(): Promise<Notification[]> {
  if (appConfig.demoMode) {
    return mockNotifications;
  }
  return request<Notification[]>("/notifications");
}

export async function markNotificationRead(id: string): Promise<Notification> {
  if (appConfig.demoMode) {
    const notification = mockNotifications.find((item) => item.id === id);
    if (!notification) {
      throw new Error(`Unknown mock notification: ${id}`);
    }
    return { ...notification, is_read: true };
  }
  return request<Notification>(`/notifications/${id}/read`, {
    method: "PATCH",
  });
}

async function extractTextPreview(file: File): Promise<string> {
  if (file.type.startsWith("text/") || file.name.toLowerCase().endsWith(".txt")) {
    return file.text();
  }
  return "";
}

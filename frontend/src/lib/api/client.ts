import { appConfig } from "@/lib/config";
import type {
  ApplicationBundle,
  DocumentVersion,
  DashboardResponse,
  EssayImproveResult,
  GrantApplication,
  MatchResult,
  Notification,
  Opportunity,
  RecommendationGenerateResult,
  RuntimeConfig,
  SponsorScanStatus,
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
  mockSponsorScanStatus,
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

export async function getSponsorScanStatus(): Promise<SponsorScanStatus> {
  if (appConfig.demoMode) {
    return mockSponsorScanStatus;
  }
  return request<SponsorScanStatus>("/sponsor/status");
}

export async function triggerSponsorScan(): Promise<{ status: string; summary: string }> {
  if (appConfig.demoMode) {
    return { status: "completed", summary: "Demo scan completed with mock data." };
  }
  return request<{ status: string; summary: string }>("/sponsor/scan", { method: "POST" });
}

export async function triggerMatching(): Promise<{ status: string; summary: string }> {
  if (appConfig.demoMode) {
    return { status: "completed", summary: "Demo matching completed with deterministic scores." };
  }
  return request<{ status: string; summary: string }>("/matching/run", { method: "POST" });
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

export async function generateApplicationRecommendation(
  applicationId: string,
  payload: { recommender_type?: string; recommender_name?: string; recommender_email?: string } = {},
): Promise<RecommendationGenerateResult> {
  if (appConfig.demoMode) {
    const bundle = mockApplicationBundles[applicationId];
    if (!bundle) {
      throw new Error(`Unknown mock application: ${applicationId}`);
    }
    const recommenderType = payload.recommender_type ?? "professor";
    const defaults: Record<string, { name: string; email: string; relationship: string }> = {
      professor: {
        name: "Dr. Ana Patel",
        email: "apatel@example.edu",
        relationship: "Faculty research mentor",
      },
      advisor: {
        name: "Jordan Lee",
        email: "jlee@example.edu",
        relationship: "Academic advisor",
      },
      mentor: {
        name: "Sam Rivera",
        email: "sam.rivera@example.org",
        relationship: "Civic tech mentor",
      },
      manager: {
        name: "Taylor Brooks",
        email: "tbrooks@example.com",
        relationship: "Project supervisor",
      },
    };
    const recommender = defaults[recommenderType] ?? defaults.professor;
    const nextVersion = bundle.recommendation_drafts.length + 1;
    const result: RecommendationGenerateResult = {
      key_talking_points: [
        `${mockProfile.full_name}'s GPA ${mockProfile.gpa} and coursework in ${mockProfile.major}.`,
        `Demonstrated execution on ${mockProfile.projects[0]}.`,
        `Clear alignment with ${bundle.opportunity.title}.`,
      ],
      why_it_matches: `${mockProfile.full_name} meets ${bundle.opportunity.title} criteria through ${bundle.opportunity.eligibility_summary}`,
      recommendation_draft: {
        id: `rec_${applicationId}_v${nextVersion}_demo`,
        application_id: applicationId,
        recommender_name: payload.recommender_name ?? recommender.name,
        recommender_email: payload.recommender_email ?? recommender.email,
        relationship: recommender.relationship,
        recommender_type: recommenderType,
        draft_body: `[DRAFT FOR RECOMMENDER REVIEW — NOT FOR SUBMISSION]\nDear Selection Committee,\n\nI am pleased to recommend ${mockProfile.full_name} for ${bundle.opportunity.title}.\n\n${mockProfile.full_name} has shown strong preparation through civic technology projects and public policy coursework.\n\nSincerely,\n${recommender.name}\n${recommender.relationship}`,
        version_number: nextVersion,
        source_draft_id: bundle.recommendation_drafts.at(-1)?.id ?? null,
        key_talking_points: [
          `${mockProfile.full_name}'s academic record and relevant project work.`,
          `Alignment with ${bundle.opportunity.provider_name}'s mission.`,
        ],
        why_it_matches: `Strong fit for ${bundle.opportunity.title} based on opportunity criteria.`,
        status: "drafted",
        metadata: {
          agent: "recommendation-agent",
          generation_method: "deterministic",
          draft_for_recommender_review: true,
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    };
    mockApplicationBundles[applicationId] = {
      ...bundle,
      recommendation_drafts: [...bundle.recommendation_drafts, result.recommendation_draft],
    };
    return result;
  }
  return request<RecommendationGenerateResult>(
    `/applications/${applicationId}/generate-recommendation`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export async function improveApplicationEssay(applicationId: string): Promise<EssayImproveResult> {
  if (appConfig.demoMode) {
    const bundle = mockApplicationBundles[applicationId];
    if (!bundle) {
      throw new Error(`Unknown mock application: ${applicationId}`);
    }
    const original =
      bundle.essay_versions.find((version) => Boolean(version.metadata.is_original))?.content ??
      bundle.essay_versions[0]?.content ??
      mockDocuments.find((doc) => doc.document_type === "essay")?.extracted_text ??
      "";
    const nextVersion = bundle.essay_versions.length + 1;
    const result: EssayImproveResult = {
      original_essay: original,
      change_summary: `Added opportunity-specific opening and closing tailored to ${bundle.opportunity.title}; integrated profile themes and preserved the original narrative core.`,
      improvement_suggestions: [
        `Lead with a concrete story tied to ${bundle.opportunity.provider_name}'s mission.`,
        "Name one measurable outcome from your civic technology project.",
        "Tighten the closing paragraph to mirror the opportunity's evaluation criteria.",
      ],
      essay_version: {
        id: `essay_${applicationId}_v${nextVersion}_demo`,
        application_id: applicationId,
        prompt: `Describe how your background aligns with ${bundle.opportunity.title}.`,
        content: `When I learned about ${bundle.opportunity.title}, I saw a direct connection to my work in civic technology.\n\n${original}\n\nAward support would help me deepen this work and deliver outcomes aligned with ${bundle.opportunity.provider_name}'s mission.`,
        version_number: nextVersion,
        status: "review",
        feedback_notes: [
          `Lead with a concrete story tied to ${bundle.opportunity.provider_name}'s mission.`,
          "Name one measurable outcome from your civic technology project.",
        ],
        source_version_id: bundle.essay_versions.at(-1)?.id ?? null,
        change_summary: `Added opportunity-specific framing for ${bundle.opportunity.title}.`,
        metadata: {
          agent: "essay-agent",
          generation_method: "deterministic",
          opportunity_id: bundle.opportunity.id,
        },
        created_at: new Date().toISOString(),
      },
    };
    mockApplicationBundles[applicationId] = {
      ...bundle,
      essay_versions: [...bundle.essay_versions, result.essay_version],
    };
    return result;
  }
  return request<EssayImproveResult>(`/applications/${applicationId}/improve-essay`, {
    method: "POST",
  });
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

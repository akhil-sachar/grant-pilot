import { appConfig } from "@/lib/config";
import type {
  ApplicationBundle,
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

export async function getDocuments(): Promise<UploadedDocument[]> {
  if (appConfig.demoMode) {
    return mockDocuments;
  }
  return request<UploadedDocument[]>("/documents");
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


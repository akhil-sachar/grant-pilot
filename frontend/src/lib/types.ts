export type Metadata = Record<string, unknown>;

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone?: string | null;
  location?: string | null;
  date_of_birth?: string | null;
  education_level?: string | null;
  school_name?: string | null;
  major?: string | null;
  gpa?: number | null;
  graduation_year?: number | null;
  fields_of_study: string[];
  career_goals: string[];
  research_interests: string[];
  awards: string[];
  projects: string[];
  leadership_experience: string[];
  citizenship_status?: string | null;
  funding_goals: string[];
  demographic_info: Metadata;
  preferences: Metadata;
  created_at: string;
  updated_at: string;
}

export interface UploadedDocument {
  id: string;
  user_id: string;
  file_name: string;
  document_type: string;
  storage_uri: string;
  mime_type: string;
  size_bytes: number;
  extracted_text?: string | null;
  extracted_text_preview?: string | null;
  current_version_id?: string | null;
  version_number: number;
  tags: string[];
  metadata: Metadata;
  status: string;
  uploaded_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  user_id: string;
  version_number: number;
  file_name: string;
  storage_uri: string;
  mime_type: string;
  size_bytes: number;
  extracted_text?: string | null;
  extracted_text_preview?: string | null;
  metadata: Metadata;
  created_at: string;
}

export interface Opportunity {
  id: string;
  provider_name: string;
  title: string;
  description: string;
  opportunity_type: string;
  amount_min?: number | null;
  amount_max?: number | null;
  currency: string;
  deadline?: string | null;
  eligibility_summary: string;
  requirements: string[];
  source_url?: string | null;
  status: string;
  tags: string[];
  metadata: Metadata;
  created_at: string;
  updated_at: string;
}

export interface MatchResult {
  id: string;
  user_id: string;
  opportunity_id: string;
  score: number;
  rationale: string;
  strengths: string[];
  gaps: string[];
  recommended_actions: string[];
  status: string;
  metadata: Metadata;
  created_at: string;
}

export interface ApplicationChecklistItem {
  id: string;
  label: string;
  status: string;
  due_at?: string | null;
}

export interface GrantApplication {
  id: string;
  user_id: string;
  opportunity_id: string;
  match_result_id?: string | null;
  status: string;
  due_at?: string | null;
  submitted_at?: string | null;
  checklist: ApplicationChecklistItem[];
  notes?: string | null;
  metadata: Metadata;
  created_at: string;
  updated_at: string;
}

export interface EssayVersion {
  id: string;
  application_id: string;
  prompt: string;
  content: string;
  version_number: number;
  status: string;
  feedback_notes: string[];
  metadata: Metadata;
  created_at: string;
}

export interface RecommendationDraft {
  id: string;
  application_id: string;
  recommender_name: string;
  recommender_email: string;
  relationship: string;
  draft_body: string;
  status: string;
  metadata: Metadata;
  created_at: string;
  updated_at: string;
}

export interface OutreachEmail {
  id: string;
  application_id: string;
  recipient_email: string;
  subject: string;
  body: string;
  status: string;
  sent_at?: string | null;
  metadata: Metadata;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  action_url?: string | null;
  metadata: Metadata;
  created_at: string;
}

export interface AgentActionLog {
  id: string;
  user_id: string;
  agent_name: string;
  action_type: string;
  status: string;
  input_summary?: string | null;
  output_summary?: string | null;
  metadata: Metadata;
  created_at: string;
}

export interface DashboardMetrics {
  active_matches: number;
  applications_in_progress: number;
  documents_uploaded: number;
  unread_notifications: number;
  next_deadline?: string | null;
  opportunities_found: number;
  active_applications: number;
  upcoming_deadlines: number;
  average_match_score: number;
  agent_actions: number;
}

export interface DashboardResponse {
  profile: UserProfile;
  metrics: DashboardMetrics;
  top_matches: MatchResult[];
  opportunities: Opportunity[];
  applications: GrantApplication[];
  documents: UploadedDocument[];
  notifications: Notification[];
  recent_agent_actions: AgentActionLog[];
  storage: Record<string, unknown>;
}

export interface ApplicationBundle {
  application: GrantApplication;
  opportunity: Opportunity;
  essay_versions: EssayVersion[];
  recommendation_drafts: RecommendationDraft[];
  outreach_emails: OutreachEmail[];
}

export interface RuntimeConfig {
  app_name: string;
  app_env: string;
  api_prefix: string;
  demo_mode: boolean;
  cors_origins: string[];
  integrations: {
    clickhouse_enabled: boolean;
    airbyte_enabled: boolean;
    composio_enabled: boolean;
    guild_ai_enabled: boolean;
    openui_enabled: boolean;
  };
}

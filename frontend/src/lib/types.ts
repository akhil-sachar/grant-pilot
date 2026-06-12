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
  score_percent?: number;
  rationale: string;
  strengths: string[];
  gaps: string[];
  recommended_actions: string[];
  priority: string;
  missing_materials: string[];
  fit_explanation: string;
  funding_potential: string;
  success_probability: number;
  status: string;
  metadata: Metadata;
  created_at: string;
}

export interface RankedOpportunity {
  opportunity: Opportunity;
  match: MatchResult;
  success_probability: number;
  score_percent: number;
  priority: string;
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
  source_version_id?: string | null;
  change_summary?: string;
  metadata: Metadata;
  created_at: string;
}

export interface EssayImproveResult {
  essay_version: EssayVersion;
  original_essay: string;
  improvement_suggestions: string[];
  change_summary: string;
}

export interface RecommendationDraft {
  id: string;
  application_id: string;
  recommender_name: string;
  recommender_email: string;
  relationship: string;
  recommender_type: string;
  draft_body: string;
  version_number: number;
  source_draft_id?: string | null;
  key_talking_points: string[];
  why_it_matches: string;
  status: string;
  metadata: Metadata;
  created_at: string;
  updated_at: string;
}

export interface RecommendationGenerateResult {
  recommendation_draft: RecommendationDraft;
  key_talking_points: string[];
  why_it_matches: string;
}

export interface OutreachEmail {
  id: string;
  application_id: string;
  recipient_email: string;
  recipient_role: string;
  email_type: string;
  subject: string;
  body: string;
  suggested_follow_up: string;
  version_number: number;
  source_email_id?: string | null;
  status: string;
  sent_at?: string | null;
  metadata: Metadata;
  created_at: string;
  updated_at: string;
}

export interface ComposioActionResult {
  action: string;
  provider: string;
  status: string;
  mode: string;
  detail: string;
  metadata: Metadata;
}

export interface ComposioStatus {
  mode: string;
  api_key_configured: boolean;
  connected_tools: string[];
  message: string;
}

export interface OutreachGenerateResult {
  outreach_email: OutreachEmail;
  suggested_follow_up: string;
  composio_mode: string;
  composio_actions: ComposioActionResult[];
}

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  priority: string;
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
  high_priority_matches?: number;
}

export interface DashboardResponse {
  profile: UserProfile;
  metrics: DashboardMetrics;
  top_matches: MatchResult[];
  ranked_opportunities?: RankedOpportunity[];
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
  demo_auto_run?: boolean;
  cors_origins: string[];
  integrations: {
    clickhouse_enabled: boolean;
    airbyte_enabled: boolean;
    composio_enabled: boolean;
    composio_mode: string;
    openai_enabled: boolean;
    openai_model: string;
    langfuse_enabled: boolean;
    agent_generation_method: string;
    guild_ai_enabled: boolean;
    openui_enabled: boolean;
  };
}

export interface AgentMetricSummary {
  agent_name: string;
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  success_rate: number;
  average_runtime_ms: number;
  actions_completed: number;
  opportunities_found: number;
  last_run_at?: string | null;
}

export interface AgentActivityResponse {
  agents: AgentMetricSummary[];
  total_runs: number;
  overall_success_rate: number;
  average_runtime_ms: number;
  total_actions_completed: number;
  opportunities_found: number;
  recent_actions: AgentActionLog[];
  guild_runs: Record<string, unknown>[];
}

export interface OpenUIComponent {
  type: string;
  id: string;
  props: Record<string, unknown>;
  children?: OpenUIComponent[];
}

export interface OpenUILayout {
  title: string;
  description: string;
  components: OpenUIComponent[];
}

export interface DemoStepResult {
  step: string;
  agent_name: string;
  status: string;
  summary: string;
  metadata: Metadata;
}

export interface DemoRunResult {
  started_at: string;
  completed_at: string;
  steps: DemoStepResult[];
  agent_actions: AgentActionLog[];
}

export interface IngestionRun {
  id: string;
  source_name: string;
  status: string;
  records_seen: number;
  records_loaded: number;
  error_message?: string | null;
  metadata: Metadata;
  started_at: string;
  completed_at?: string | null;
}

export interface SourceScanState {
  source_name: string;
  display_name: string;
  category: string;
  status: string;
  opportunities_found: number;
  last_scan_at?: string | null;
  last_ingestion_run_id?: string | null;
  error_message?: string | null;
}

export interface SponsorScanStatus {
  is_scanning: boolean;
  last_full_scan_at?: string | null;
  total_opportunities: number;
  sources: SourceScanState[];
  recent_ingestion_runs: IngestionRun[];
  airbyte_mode: string;
  metadata: Metadata;
  updated_at: string;
}

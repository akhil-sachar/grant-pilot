import type {
  AgentActionLog,
  AgentActivityResponse,
  ApplicationBundle,
  DashboardAnalytics,
  DashboardResponse,
  DemoRunResult,
  DemoStatus,
  DocumentVersion,
  GrantApplication,
  IngestionRun,
  MatchResult,
  Notification,
  OpenUILayout,
  Opportunity,
  RuntimeConfig,
  SponsorScanStatus,
  StorageHealth,
  UploadedDocument,
  UserProfile,
} from "@/lib/types";

export const mockProfile: UserProfile = {
  id: "usr_demo_001",
  email: "maya.chen@example.com",
  full_name: "Maya Chen",
  phone: "+1 415 555 0198",
  location: "Oakland, CA",
  date_of_birth: "2005-07-19",
  education_level: "Undergraduate sophomore",
  school_name: "Bay City College",
  major: "Computer Science and Public Policy",
  gpa: 3.82,
  graduation_year: 2028,
  fields_of_study: ["Computer Science", "Public Policy"],
  career_goals: ["Civic technology", "AI safety", "Public-interest software"],
  research_interests: [
    "Human-centered AI",
    "Open data for local government",
    "Scholarship access automation",
  ],
  awards: ["Dean's List 2025", "Bay City Civic Hackathon Winner"],
  projects: ["Open transit delay dashboard", "Community benefits eligibility checker"],
  leadership_experience: [
    "Founder, Civic Tech Student Lab",
    "Peer mentor for first-generation CS students",
  ],
  citizenship_status: "US citizen",
  funding_goals: ["Tuition", "Research stipend", "Conference travel"],
  demographic_info: { first_generation: true, low_income: true },
  preferences: {
    deadline_window_days: 45,
    minimum_award_amount: 1000,
    remote_friendly: true,
  },
  created_at: "2026-05-01T09:00:00Z",
  updated_at: "2026-06-10T16:30:00Z",
};

export const mockOpportunities: Opportunity[] = [
  {
    id: "opp_civic_ai",
    provider_name: "Civic Futures Foundation",
    title: "Civic AI Builders Scholarship",
    description: "Funding for students building applied technology for public benefit.",
    opportunity_type: "scholarship",
    amount_min: 2500,
    amount_max: 10000,
    currency: "USD",
    deadline: "2026-08-15",
    eligibility_summary:
      "Open to undergraduate students with demonstrated civic technology work.",
    requirements: ["Resume", "Transcript", "Personal statement", "Project portfolio"],
    source_url: "https://example.org/civic-ai-builders",
    status: "active",
    tags: ["ai", "public-interest", "undergraduate"],
    metadata: { source: "demo_seed" },
    created_at: "2026-05-12T12:00:00Z",
    updated_at: "2026-06-01T12:00:00Z",
  },
  {
    id: "opp_open_grant",
    provider_name: "Open Knowledge Trust",
    title: "Open Data Research Grant",
    description:
      "Small grants for students using open datasets to answer community questions.",
    opportunity_type: "grant",
    amount_min: 1000,
    amount_max: 5000,
    currency: "USD",
    deadline: "2026-07-30",
    eligibility_summary:
      "Applicants must submit a research plan and public data source list.",
    requirements: ["Research proposal", "Budget", "Faculty reference"],
    source_url: "https://example.org/open-data-research",
    status: "active",
    tags: ["open-data", "research", "community"],
    metadata: { source: "demo_seed" },
    created_at: "2026-05-18T10:15:00Z",
    updated_at: "2026-06-03T11:20:00Z",
  },
  {
    id: "opp_first_gen",
    provider_name: "Horizon Scholars Network",
    title: "First Generation STEM Award",
    description: "Scholarship for first-generation students pursuing STEM degrees.",
    opportunity_type: "award",
    amount_min: 1500,
    amount_max: 7500,
    currency: "USD",
    deadline: "2026-09-05",
    eligibility_summary:
      "First-generation undergraduate students in accredited STEM programs.",
    requirements: ["Transcript", "Short essay", "Financial need statement"],
    source_url: "https://example.org/first-gen-stem",
    status: "active",
    tags: ["stem", "first-generation", "need-based"],
    metadata: { source: "demo_seed" },
    created_at: "2026-05-24T08:45:00Z",
    updated_at: "2026-06-05T09:00:00Z",
  },
];

export const mockDocuments: UploadedDocument[] = [
  {
    id: "doc_resume",
    user_id: "usr_demo_001",
    file_name: "Maya_Chen_Resume.pdf",
    document_type: "resume",
    storage_uri: "mock://documents/doc_resume/Maya_Chen_Resume.pdf",
    mime_type: "application/pdf",
    size_bytes: 242112,
    extracted_text:
      "Maya Chen resume. Computer science and public policy student. Projects include an open transit delay dashboard and community benefits eligibility checker.",
    extracted_text_preview:
      "Computer science student focused on civic AI prototypes and open data tools.",
    current_version_id: "docver_resume_v1",
    version_number: 1,
    tags: ["profile", "ready"],
    metadata: { pages: 2 },
    status: "processed",
    uploaded_at: "2026-06-04T14:00:00Z",
    updated_at: "2026-06-04T14:00:00Z",
  },
  {
    id: "doc_transcript",
    user_id: "usr_demo_001",
    file_name: "Unofficial_Transcript.pdf",
    document_type: "transcript",
    storage_uri: "mock://documents/doc_transcript/Unofficial_Transcript.pdf",
    mime_type: "application/pdf",
    size_bytes: 518002,
    extracted_text:
      "Unofficial transcript. GPA 3.82. Coursework includes data structures, policy analysis, statistics, and public sector data systems.",
    extracted_text_preview:
      "GPA 3.82, coursework includes data structures, policy analysis, statistics.",
    current_version_id: "docver_transcript_v1",
    version_number: 1,
    tags: ["academic", "needs-review"],
    metadata: { pages: 4 },
    status: "needs_review",
    uploaded_at: "2026-06-06T17:35:00Z",
    updated_at: "2026-06-06T17:35:00Z",
  },
  {
    id: "doc_personal_essay",
    user_id: "usr_demo_001",
    file_name: "Personal_Essay_Civic_AI.pdf",
    document_type: "essay",
    storage_uri: "mock://documents/doc_personal_essay/Personal_Essay_Civic_AI.pdf",
    mime_type: "application/pdf",
    size_bytes: 188440,
    extracted_text:
      "Personal essay draft about building civic technology after seeing neighbors struggle to find local assistance programs.",
    extracted_text_preview:
      "Essay draft about civic technology and access to public benefit programs.",
    current_version_id: "docver_personal_essay_v1",
    version_number: 1,
    tags: ["essay", "draft"],
    metadata: { pages: 3 },
    status: "processed",
    uploaded_at: "2026-06-08T13:20:00Z",
    updated_at: "2026-06-08T13:20:00Z",
  },
  {
    id: "doc_recommendation_patel",
    user_id: "usr_demo_001",
    file_name: "Recommendation_Dr_Patel.pdf",
    document_type: "recommendation",
    storage_uri: "mock://documents/doc_recommendation_patel/Recommendation_Dr_Patel.pdf",
    mime_type: "application/pdf",
    size_bytes: 154880,
    extracted_text:
      "Recommendation letter from Dr. Ana Patel highlighting research discipline, public-interest motivation, and software execution.",
    extracted_text_preview:
      "Letter highlighting research discipline and public-interest software work.",
    current_version_id: "docver_recommendation_patel_v1",
    version_number: 1,
    tags: ["recommendation", "ready"],
    metadata: { pages: 1 },
    status: "processed",
    uploaded_at: "2026-06-09T09:45:00Z",
    updated_at: "2026-06-09T09:45:00Z",
  },
];

export const mockDocumentVersions: Record<string, DocumentVersion[]> = Object.fromEntries(
  mockDocuments.map((document) => [
    document.id,
    [
      {
        id: document.current_version_id ?? `${document.id}_v1`,
        document_id: document.id,
        user_id: document.user_id,
        version_number: document.version_number,
        file_name: document.file_name,
        storage_uri: document.storage_uri,
        mime_type: document.mime_type,
        size_bytes: document.size_bytes,
        extracted_text: document.extracted_text,
        extracted_text_preview: document.extracted_text_preview,
        metadata: document.metadata,
        created_at: document.uploaded_at,
      },
    ],
  ]),
);

export const mockMatches: MatchResult[] = [
  {
    id: "match_civic_ai",
    user_id: "usr_demo_001",
    opportunity_id: "opp_civic_ai",
    score: 0.92,
    score_percent: 92,
    rationale:
      "Strong alignment with civic technology, public-interest software, and AI safety goals.",
    strengths: ["Civic tech portfolio", "Relevant coursework", "Clear public-benefit theme"],
    gaps: ["Portfolio link needs a stronger project outcome summary"],
    recommended_actions: ["Refresh resume impact bullets", "Draft 650-word personal statement"],
    priority: "high",
    missing_materials: ["Project portfolio"],
    fit_explanation:
      "Maya's civic technology projects and public policy coursework align strongly with this scholarship.",
    funding_potential: "High — strong fit for $2,500–$10,000",
    success_probability: 0.88,
    status: "in_application",
    metadata: { scoring_method: "deterministic", score_percent: 92 },
    created_at: "2026-06-09T15:00:00Z",
  },
  {
    id: "match_open_grant",
    user_id: "usr_demo_001",
    opportunity_id: "opp_open_grant",
    score: 0.84,
    score_percent: 84,
    rationale: "Research interests and open data experience fit the grant goals.",
    strengths: ["Open data project idea", "Public policy minor"],
    gaps: ["Needs faculty reference confirmed", "Budget not started"],
    recommended_actions: ["Ask faculty mentor", "Create one-page research budget"],
    priority: "high",
    missing_materials: ["Budget", "Faculty reference"],
    fit_explanation:
      "Open data research interests and policy background map well to the grant's civic data focus.",
    funding_potential: "High — strong fit for up to $5,000",
    success_probability: 0.79,
    status: "saved",
    metadata: { scoring_method: "deterministic", score_percent: 84 },
    created_at: "2026-06-10T10:10:00Z",
  },
  {
    id: "match_first_gen",
    user_id: "usr_demo_001",
    opportunity_id: "opp_first_gen",
    score: 0.78,
    score_percent: 78,
    rationale:
      "Eligibility is strong, but application materials need tailoring for STEM award criteria.",
    strengths: ["First-generation eligibility", "STEM program"],
    gaps: ["Financial need statement missing"],
    recommended_actions: ["Upload financial aid summary", "Draft short essay"],
    priority: "medium",
    missing_materials: ["Financial need statement"],
    fit_explanation:
      "First-generation STEM eligibility is a strong fit; financial documentation still needed.",
    funding_potential: "Medium — competitive for $1,500–$4,000",
    success_probability: 0.71,
    status: "new",
    metadata: { scoring_method: "deterministic", score_percent: 78 },
    created_at: "2026-06-11T09:25:00Z",
  },
];

export const mockApplications: GrantApplication[] = [
  {
    id: "app_civic_ai",
    user_id: "usr_demo_001",
    opportunity_id: "opp_civic_ai",
    match_result_id: "match_civic_ai",
    status: "in_progress",
    due_at: "2026-08-15T23:59:00Z",
    submitted_at: null,
    checklist: [
      { id: "task_resume", label: "Resume", status: "done" },
      { id: "task_statement", label: "Personal statement", status: "in_progress" },
      { id: "task_portfolio", label: "Project portfolio", status: "todo" },
    ],
    notes: "Prioritize public-benefit outcomes and prototype screenshots.",
    metadata: {},
    created_at: "2026-06-09T16:00:00Z",
    updated_at: "2026-06-11T12:00:00Z",
  },
  {
    id: "app_open_grant",
    user_id: "usr_demo_001",
    opportunity_id: "opp_open_grant",
    match_result_id: "match_open_grant",
    status: "planned",
    due_at: "2026-07-30T23:59:00Z",
    submitted_at: null,
    checklist: [
      { id: "task_proposal", label: "Research proposal", status: "todo" },
      { id: "task_budget", label: "Budget", status: "todo" },
      { id: "task_reference", label: "Faculty reference", status: "blocked" },
    ],
    notes: null,
    metadata: {},
    created_at: "2026-06-10T11:00:00Z",
    updated_at: "2026-06-10T11:00:00Z",
  },
];

export const mockNotifications: Notification[] = [
  {
    id: "not_high_match_civic",
    user_id: "usr_demo_001",
    title: "High match opportunity",
    message: "Civic AI Builders Scholarship scored 92% — strong fit for your profile.",
    notification_type: "high_match",
    priority: "high",
    is_read: false,
    action_url: "/opportunities",
    metadata: { dedupe_key: "high_match:opp_civic_ai", agent: "notification-agent" },
    created_at: "2026-06-12T09:00:00Z",
  },
  {
    id: "not_deadline_open_grant",
    user_id: "usr_demo_001",
    title: "Deadline approaching",
    message: "Open Data Research Grant is due soon — research proposal and budget are still pending.",
    notification_type: "deadline_approaching",
    priority: "medium",
    is_read: false,
    action_url: "/applications/app_open_grant",
    metadata: { dedupe_key: "deadline_approaching:app_open_grant", agent: "notification-agent" },
    created_at: "2026-06-11T08:00:00Z",
  },
  {
    id: "not_transcript_review",
    user_id: "usr_demo_001",
    title: "Missing document",
    message: "Confirm the parsed coursework before matching uses it.",
    notification_type: "missing_document",
    priority: "high",
    is_read: false,
    action_url: "/documents",
    metadata: { dedupe_key: "missing_document:transcript", agent: "notification-agent" },
    created_at: "2026-06-10T18:00:00Z",
  },
  {
    id: "not_essay_ready",
    user_id: "usr_demo_001",
    title: "Essay ready for review",
    message: "Version 1 for Civic AI Builders Scholarship is ready to review.",
    notification_type: "essay_ready",
    priority: "medium",
    is_read: false,
    action_url: "/applications/app_civic_ai",
    metadata: { dedupe_key: "essay_ready:essay_civic_ai_v1", agent: "notification-agent" },
    created_at: "2026-06-11T11:00:00Z",
  },
  {
    id: "not_rec_ready",
    user_id: "usr_demo_001",
    title: "Recommendation draft ready",
    message: "A draft for Dr. Ana Patel on Open Data Research Grant is ready for recommender review.",
    notification_type: "recommendation_ready",
    priority: "medium",
    is_read: false,
    action_url: "/applications/app_open_grant",
    metadata: { dedupe_key: "recommendation_ready:rec_open_grant_faculty", agent: "notification-agent" },
    created_at: "2026-06-10T13:00:00Z",
  },
  {
    id: "not_email_ready",
    user_id: "usr_demo_001",
    title: "Email draft ready",
    message: "Outreach draft for Open Data Research Grant is ready to send.",
    notification_type: "email_draft_ready",
    priority: "low",
    is_read: true,
    action_url: "/applications/app_open_grant",
    metadata: { dedupe_key: "email_draft_ready:email_open_grant_faculty", agent: "notification-agent" },
    created_at: "2026-06-10T14:00:00Z",
  },
];

export const mockAgentActions: AgentActionLog[] = [
  {
    id: "log_sponsor_scan",
    user_id: "usr_demo_001",
    agent_name: "sponsor-agent",
    action_type: "full_scan",
    status: "completed",
    input_summary: "Scanning all configured funding sources",
    output_summary: "Scanned 9 sources, loaded 18 opportunities.",
    metadata: {
      guild_run_id: "guild_demo_sponsor_001",
      runtime_ms: 4200,
      sources_scanned: 9,
      total_loaded: 18,
      tracked_by: "guild-ai",
    },
    created_at: "2026-06-12T08:00:00Z",
  },
  {
    id: "log_matching_run",
    user_id: "usr_demo_001",
    agent_name: "matching-agent",
    action_type: "full_match",
    status: "completed",
    input_summary: "Scoring all opportunities against profile and documents",
    output_summary: "Scored 3 opportunities (2 high priority).",
    metadata: {
      guild_run_id: "guild_demo_match_001",
      runtime_ms: 890,
      matched: 3,
      high_priority: 2,
      tracked_by: "guild-ai",
    },
    created_at: "2026-06-12T08:01:30Z",
  },
  {
    id: "log_essay_improve",
    user_id: "usr_demo_001",
    agent_name: "essay-agent",
    action_type: "improve_essay",
    status: "completed",
    input_summary: "Tailoring essay for application app_civic_ai",
    output_summary: "Tailored Civic AI Builders essay with stronger civic impact framing.",
    metadata: {
      guild_run_id: "guild_demo_essay_001",
      runtime_ms: 1240,
      application_id: "app_civic_ai",
      tracked_by: "guild-ai",
    },
    created_at: "2026-06-12T08:03:00Z",
  },
  {
    id: "log_rec_draft",
    user_id: "usr_demo_001",
    agent_name: "recommendation-agent",
    action_type: "generate_recommendation",
    status: "completed",
    input_summary: "Drafting recommendation for application app_open_grant",
    output_summary: "Created recommendation draft v1 for Dr. Ana Patel.",
    metadata: {
      guild_run_id: "guild_demo_rec_001",
      runtime_ms: 980,
      tracked_by: "guild-ai",
    },
    created_at: "2026-06-12T08:04:15Z",
  },
  {
    id: "log_outreach",
    user_id: "usr_demo_001",
    agent_name: "outreach-agent",
    action_type: "generate_outreach",
    status: "completed",
    input_summary: "Outreach for application app_open_grant",
    output_summary: "Created outreach email v1 and ran 4 Composio actions.",
    metadata: {
      guild_run_id: "guild_demo_outreach_001",
      runtime_ms: 1560,
      actions: 4,
      tracked_by: "guild-ai",
    },
    created_at: "2026-06-12T08:05:30Z",
  },
  {
    id: "log_notifications",
    user_id: "usr_demo_001",
    agent_name: "notification-agent",
    action_type: "generate_notifications",
    status: "completed",
    input_summary: "Scanning workspace for notification events",
    output_summary: "Created 6 notifications.",
    metadata: {
      guild_run_id: "guild_demo_notif_001",
      runtime_ms: 320,
      created_count: 6,
      tracked_by: "guild-ai",
    },
    created_at: "2026-06-12T08:06:00Z",
  },
  {
    id: "log_composio",
    user_id: "usr_demo_001",
    agent_name: "composio-service",
    action_type: "outreach_workflow",
    status: "completed",
    input_summary: "Gmail draft, Google Doc, Calendar follow-up, Drive archive",
    output_summary: "Simulated Composio workflow completed.",
    metadata: {
      guild_run_id: "guild_demo_composio_001",
      runtime_ms: 640,
      actions: 4,
      tracked_by: "guild-ai",
    },
    created_at: "2026-06-12T08:05:45Z",
  },
];

export const mockDashboard: DashboardResponse = {
  profile: mockProfile,
  metrics: {
    active_matches: mockMatches.length,
    applications_in_progress: mockApplications.length,
    documents_uploaded: mockDocuments.length,
    unread_notifications: mockNotifications.filter((item) => !item.is_read).length,
    next_deadline: "2026-07-30T23:59:00Z",
    opportunities_found: mockOpportunities.length,
    active_applications: mockApplications.length,
    upcoming_deadlines: mockApplications.filter((item) => item.due_at).length,
    average_match_score:
      mockMatches.reduce((total, match) => total + match.score, 0) / mockMatches.length,
    agent_actions: mockAgentActions.length,
    high_priority_matches: mockMatches.filter((match) => match.priority === "high").length,
  },
  top_matches: mockMatches,
  ranked_opportunities: mockMatches
    .map((match) => {
      const opportunity = mockOpportunities.find((item) => item.id === match.opportunity_id);
      if (!opportunity) {
        return null;
      }
      return {
        opportunity,
        match,
        success_probability: match.success_probability,
        score_percent: match.score_percent ?? Math.round(match.score * 100),
        priority: match.priority,
      };
    })
    .filter((item): item is NonNullable<typeof item> => item !== null)
    .sort((a, b) => b.success_probability - a.success_probability),
  opportunities: mockOpportunities,
  applications: mockApplications,
  documents: mockDocuments,
  notifications: mockNotifications,
  recent_agent_actions: mockAgentActions,
  storage: {
    storage_mode: "local",
    primary: "clickhouse",
    primary_available: false,
    fallback_enabled: true,
    last_error: "ClickHouse is unavailable",
  },
};

export const mockRuntimeConfig: RuntimeConfig = {
  app_name: "GrantPilot API",
  app_env: "development",
  api_prefix: "/api/v1",
  demo_mode: true,
  demo_auto_run: false,
  cors_origins: ["http://localhost:3000"],
  integrations: {
    clickhouse_enabled: false,
    composio_enabled: false,
    composio_mode: "simulated",
    openai_enabled: false,
    openai_model: "gpt-4o-mini",
    langfuse_enabled: false,
    agent_generation_method: "auto",
    guild_ai_enabled: true,
    openui_enabled: true,
  },
};

export const mockApplicationBundles: Record<string, ApplicationBundle> = {
  app_civic_ai: {
    application: mockApplications[0],
    opportunity: mockOpportunities[0],
    essay_versions: [
      {
        id: "essay_civic_ai_v1",
        application_id: "app_civic_ai",
        prompt: "Describe how your work uses technology to improve public outcomes.",
        content:
          "Draft outline: community problem, prototype, measurable outcome, future plan.",
        version_number: 1,
        status: "outline",
        feedback_notes: ["Add a concrete beneficiary story", "Quantify prototype usage"],
        metadata: { is_original: true, agent: "essay-agent" },
        created_at: "2026-06-11T10:00:00Z",
      },
    ],
    recommendation_drafts: [],
    outreach_emails: [],
  },
  app_open_grant: {
    application: mockApplications[1],
    opportunity: mockOpportunities[1],
    essay_versions: [],
    recommendation_drafts: [
      {
        id: "rec_open_grant_faculty",
        application_id: "app_open_grant",
        recommender_name: "Dr. Ana Patel",
        recommender_email: "apatel@example.edu",
        relationship: "Faculty research mentor",
        recommender_type: "professor",
        draft_body:
          "[DRAFT FOR RECOMMENDER REVIEW — NOT FOR SUBMISSION]\nShort request draft for a research-focused recommendation.",
        version_number: 1,
        key_talking_points: [
          "Strong research preparation in public-sector data systems.",
          "Consistent follow-through on open data coursework.",
        ],
        why_it_matches: "Student research interests align with the Open Data Research Grant criteria.",
        status: "drafted",
        metadata: { draft_for_recommender_review: true, agent: "recommendation-agent" },
        created_at: "2026-06-10T12:30:00Z",
        updated_at: "2026-06-10T12:30:00Z",
      },
    ],
    outreach_emails: [
      {
        id: "email_open_grant_faculty",
        application_id: "app_open_grant",
        recipient_email: "apatel@example.edu",
        recipient_role: "professor",
        email_type: "recommendation_request",
        subject: "Recommendation request for Open Data Research Grant",
        body:
          "Draft email asking for a faculty reference and offering a short project summary.",
        suggested_follow_up: "Follow up with Dr. Patel in 5–7 days if you have not received a response.",
        version_number: 1,
        status: "draft",
        sent_at: null,
        metadata: { agent: "outreach-agent", recipient_name: "Dr. Ana Patel" },
        created_at: "2026-06-10T12:40:00Z",
        updated_at: "2026-06-10T12:40:00Z",
      },
    ],
  },
};

export const mockSponsorScanStatus: SponsorScanStatus = {
  is_scanning: false,
  last_full_scan_at: "2026-06-12T08:00:00Z",
  total_opportunities: mockOpportunities.length,
  metadata: {},
  updated_at: "2026-06-12T08:05:00Z",
  sources: [
    {
      source_name: "grants_gov",
      display_name: "Grants Gov",
      category: "federal_grant",
      status: "completed",
      opportunities_found: 2,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
    {
      source_name: "nsf",
      display_name: "Nsf",
      category: "research_grant",
      status: "completed",
      opportunities_found: 2,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
    {
      source_name: "nih",
      display_name: "Nih",
      category: "health_research",
      status: "completed",
      opportunities_found: 1,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
    {
      source_name: "sbir_sttr",
      display_name: "Sbir Sttr",
      category: "sbir_sttr",
      status: "completed",
      opportunities_found: 2,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
    {
      source_name: "yc_grants",
      display_name: "Yc Grants",
      category: "startup_grant",
      status: "completed",
      opportunities_found: 1,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
    {
      source_name: "foundation_directories",
      display_name: "Foundation Directories",
      category: "foundation",
      status: "completed",
      opportunities_found: 2,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
    {
      source_name: "university_grants",
      display_name: "University Grants",
      category: "university",
      status: "completed",
      opportunities_found: 2,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
    {
      source_name: "scholarships",
      display_name: "Scholarships",
      category: "scholarship",
      status: "completed",
      opportunities_found: 2,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
    {
      source_name: "corporate_innovation",
      display_name: "Corporate Innovation",
      category: "corporate",
      status: "completed",
      opportunities_found: 2,
      last_scan_at: "2026-06-12T08:00:00Z",
    },
  ],
  recent_ingestion_runs: [
    {
      id: "ingest_grants_gov_demo",
      source_name: "grants_gov",
      status: "completed",
      records_seen: 2,
      records_loaded: 2,
      metadata: { mode: "mock" },
      started_at: "2026-06-12T08:00:00Z",
      completed_at: "2026-06-12T08:00:05Z",
    },
  ],
};

const trackedAgents = [
  "sponsor-agent",
  "matching-agent",
  "essay-agent",
  "recommendation-agent",
  "outreach-agent",
  "notification-agent",
] as const;

export const mockAgentActivity: AgentActivityResponse = {
  agents: trackedAgents.map((agentName) => {
    const logs = mockAgentActions.filter((log) => log.agent_name === agentName);
    const completed = logs.filter((log) => log.status === "completed");
    const runtimes = logs
      .map((log) => log.metadata.runtime_ms)
      .filter((value): value is number => typeof value === "number");
    const actions = completed.reduce((total, log) => {
      const value =
        log.metadata.matched ??
        log.metadata.created_count ??
        log.metadata.actions ??
        log.metadata.total_loaded ??
        1;
      return total + (typeof value === "number" ? value : 1);
    }, 0);

    return {
      agent_name: agentName,
      total_runs: logs.length,
      completed_runs: completed.length,
      failed_runs: logs.filter((log) => log.status === "failed").length,
      success_rate: logs.length ? completed.length / logs.length : 0,
      average_runtime_ms: runtimes.length
        ? runtimes.reduce((a, b) => a + b, 0) / runtimes.length
        : 0,
      actions_completed: actions,
      opportunities_found:
        agentName === "sponsor-agent"
          ? Number(completed[0]?.metadata.total_loaded ?? 0)
          : 0,
      last_run_at: logs[0]?.created_at ?? null,
    };
  }),
  total_runs: mockAgentActions.length,
  overall_success_rate: mockAgentActions.filter((log) => log.status === "completed").length / mockAgentActions.length,
  average_runtime_ms:
    mockAgentActions.reduce((total, log) => total + Number(log.metadata.runtime_ms ?? 0), 0) /
    mockAgentActions.length,
  total_actions_completed: 38,
  opportunities_found: mockOpportunities.length,
  recent_actions: mockAgentActions,
  guild_runs: mockAgentActions.map((log) => ({
    run_id: log.metadata.guild_run_id,
    agent_name: log.agent_name,
    status: log.status,
    runtime_ms: log.metadata.runtime_ms,
  })),
};

export const mockOpenUILayout: OpenUILayout = {
  title: "GrantPilot Agent Workspace",
  description: "Dynamic OpenUI layout generated from live agent activity and workspace state.",
  components: [
    {
      type: "section",
      id: "section_opportunities",
      props: { title: "Opportunity Cards", layout: "grid" },
      children: mockDashboard.ranked_opportunities!.slice(0, 3).map((item) => ({
        type: "opportunity_card",
        id: `opp_card_${item.match.id}`,
        props: {
          title: item.opportunity.title,
          provider: item.opportunity.provider_name,
          score_percent: item.score_percent,
          success_probability: item.success_probability,
          priority: item.priority,
          deadline: item.opportunity.deadline,
          tags: item.opportunity.tags,
        },
      })),
    },
    {
      type: "section",
      id: "section_matches",
      props: { title: "Match Panels", layout: "stack" },
      children: mockMatches.slice(0, 2).map((match) => ({
        type: "match_panel",
        id: `match_panel_${match.id}`,
        props: {
          score: match.score,
          priority: match.priority,
          fit_explanation: match.fit_explanation,
          recommended_actions: match.recommended_actions,
          missing_materials: match.missing_materials,
        },
      })),
    },
    {
      type: "section",
      id: "section_pipeline",
      props: { title: "Application Pipeline", layout: "table" },
      children: mockApplications.map((app) => ({
        type: "pipeline_row",
        id: `pipeline_${app.id}`,
        props: {
          application_id: app.id,
          status: app.status,
          due_at: app.due_at,
          checklist_total: app.checklist.length,
          checklist_done: app.checklist.filter((item) => item.status === "done").length,
        },
      })),
    },
    {
      type: "section",
      id: "section_notifications",
      props: { title: "Notification Feed", layout: "feed" },
      children: mockNotifications.slice(0, 4).map((item) => ({
        type: "notification_item",
        id: `notif_${item.id}`,
        props: {
          title: item.title,
          message: item.message,
          type: item.notification_type,
          priority: item.priority,
          is_read: item.is_read,
          action_url: item.action_url,
        },
      })),
    },
    {
      type: "section",
      id: "section_timeline",
      props: { title: "Agent Timeline", layout: "timeline" },
      children: mockAgentActions.map((log) => ({
        type: "timeline_event",
        id: `timeline_${log.id}`,
        props: {
          agent_name: log.agent_name,
          action_type: log.action_type,
          status: log.status,
          input_summary: log.input_summary,
          output_summary: log.output_summary,
          runtime_ms: log.metadata.runtime_ms,
          guild_run_id: log.metadata.guild_run_id,
          created_at: log.created_at,
        },
      })),
    },
  ],
};

export const mockDemoRunResult: DemoRunResult = {
  started_at: "2026-06-12T08:00:00Z",
  completed_at: "2026-06-12T08:06:30Z",
  steps: [
    {
      step: "opportunity_discovery",
      agent_name: "sponsor-agent",
      status: "completed",
      summary: "Scanned 9 sources, loaded 18 opportunities.",
      metadata: { total_loaded: 18 },
    },
    {
      step: "matching",
      agent_name: "matching-agent",
      status: "completed",
      summary: "Scored 3 opportunities (2 high priority).",
      metadata: { matched: 3 },
    },
    {
      step: "essay_improvement",
      agent_name: "essay-agent",
      status: "completed",
      summary: "Tailored Civic AI Builders essay.",
      metadata: {},
    },
    {
      step: "recommendation_generation",
      agent_name: "recommendation-agent",
      status: "completed",
      summary: "Created recommendation draft for Dr. Ana Patel.",
      metadata: {},
    },
    {
      step: "personalized_outreach",
      agent_name: "outreach-agent",
      status: "completed",
      summary: "Generated personalized faculty outreach email.",
      metadata: {},
    },
    {
      step: "notification_creation",
      agent_name: "notification-agent",
      status: "completed",
      summary: "Created 6 notifications.",
      metadata: { created_count: 6 },
    },
    {
      step: "composio_actions",
      agent_name: "composio-service",
      status: "completed",
      summary: "Simulated Composio workflow completed.",
      metadata: { actions: 4 },
    },
  ],
  agent_actions: mockAgentActions,
};

export const mockDashboardAnalytics: DashboardAnalytics = {
  opportunities_found: mockOpportunities.length,
  active_applications: mockApplications.length,
  upcoming_deadlines: mockApplications.filter((item) => item.due_at).length,
  match_scores: mockMatches.map((match) => match.score),
  average_match_score:
    mockMatches.reduce((total, match) => total + match.score, 0) / mockMatches.length,
  agent_actions: mockAgentActions.length,
  storage_mode: "local",
};

export const mockDemoStatus: DemoStatus = {
  demo_mode: true,
  demo_auto_run: false,
  guild_ai_enabled: true,
  openui_enabled: true,
};

export const mockStorageHealth: StorageHealth = {
  storage_mode: "local",
  primary: "clickhouse",
  primary_available: false,
  fallback_enabled: true,
  last_error: "ClickHouse is unavailable",
};

export const mockIngestionRuns: IngestionRun[] = mockSponsorScanStatus.recent_ingestion_runs;

from datetime import date, datetime, timezone

from app.models import (
    AgentActionLog,
    AgentActionStatus,
    Application,
    ApplicationChecklistItem,
    ApplicationStatus,
    ChecklistItemStatus,
    DocumentProcessingStatus,
    DocumentType,
    EssayStatus,
    EssayVersion,
    IngestionRun,
    IngestionRunStatus,
    MatchResult,
    MatchStatus,
    Notification,
    NotificationType,
    Opportunity,
    OpportunityType,
    OutreachEmail,
    OutreachEmailStatus,
    RecommendationDraft,
    RecommendationStatus,
    UploadedDocument,
    UserProfile,
)


DEFAULT_USER_ID = "usr_demo_001"


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def build_seed_data() -> dict[str, list[dict]]:
    profile = UserProfile(
        id=DEFAULT_USER_ID,
        email="maya.chen@example.com",
        full_name="Maya Chen",
        phone="+1 415 555 0198",
        location="Oakland, CA",
        date_of_birth=date(2005, 7, 19),
        education_level="Undergraduate sophomore",
        school_name="Bay City College",
        graduation_year=2028,
        fields_of_study=["Computer Science", "Public Policy"],
        career_goals=["Civic technology", "AI safety", "Public-interest software"],
        citizenship_status="US citizen",
        funding_goals=["Tuition", "Research stipend", "Conference travel"],
        demographic_info={"first_generation": True, "low_income": True},
        preferences={
            "deadline_window_days": 45,
            "minimum_award_amount": 1000,
            "remote_friendly": True,
        },
        created_at=_dt("2026-05-01T09:00:00"),
        updated_at=_dt("2026-06-10T16:30:00"),
    )

    opportunities = [
        Opportunity(
            id="opp_civic_ai",
            provider_name="Civic Futures Foundation",
            title="Civic AI Builders Scholarship",
            description="Funding for students building applied technology for public benefit.",
            opportunity_type=OpportunityType.SCHOLARSHIP,
            amount_min=2500,
            amount_max=10000,
            deadline=date(2026, 8, 15),
            eligibility_summary="Open to undergraduate students with demonstrated civic technology work.",
            requirements=["Resume", "Transcript", "Personal statement", "Project portfolio"],
            source_url="https://example.org/civic-ai-builders",
            tags=["ai", "public-interest", "undergraduate"],
            metadata={"source": "demo_seed"},
            created_at=_dt("2026-05-12T12:00:00"),
            updated_at=_dt("2026-06-01T12:00:00"),
        ),
        Opportunity(
            id="opp_open_grant",
            provider_name="Open Knowledge Trust",
            title="Open Data Research Grant",
            description="Small grants for students using open datasets to answer community questions.",
            opportunity_type=OpportunityType.GRANT,
            amount_min=1000,
            amount_max=5000,
            deadline=date(2026, 7, 30),
            eligibility_summary="Applicants must submit a research plan and public data source list.",
            requirements=["Research proposal", "Budget", "Faculty reference"],
            source_url="https://example.org/open-data-research",
            tags=["open-data", "research", "community"],
            metadata={"source": "demo_seed"},
            created_at=_dt("2026-05-18T10:15:00"),
            updated_at=_dt("2026-06-03T11:20:00"),
        ),
        Opportunity(
            id="opp_first_gen",
            provider_name="Horizon Scholars Network",
            title="First Generation STEM Award",
            description="Scholarship for first-generation students pursuing STEM degrees.",
            opportunity_type=OpportunityType.AWARD,
            amount_min=1500,
            amount_max=7500,
            deadline=date(2026, 9, 5),
            eligibility_summary="First-generation undergraduate students in accredited STEM programs.",
            requirements=["Transcript", "Short essay", "Financial need statement"],
            source_url="https://example.org/first-gen-stem",
            tags=["stem", "first-generation", "need-based"],
            metadata={"source": "demo_seed"},
            created_at=_dt("2026-05-24T08:45:00"),
            updated_at=_dt("2026-06-05T09:00:00"),
        ),
    ]

    documents = [
        UploadedDocument(
            id="doc_resume",
            user_id=DEFAULT_USER_ID,
            file_name="Maya_Chen_Resume.pdf",
            document_type=DocumentType.RESUME,
            storage_uri="mock://documents/doc_resume/Maya_Chen_Resume.pdf",
            mime_type="application/pdf",
            size_bytes=242112,
            extracted_text_preview="Computer science student focused on civic AI prototypes and open data tools.",
            tags=["profile", "ready"],
            metadata={"pages": 2},
            status=DocumentProcessingStatus.PROCESSED,
            uploaded_at=_dt("2026-06-04T14:00:00"),
        ),
        UploadedDocument(
            id="doc_transcript",
            user_id=DEFAULT_USER_ID,
            file_name="Unofficial_Transcript.pdf",
            document_type=DocumentType.TRANSCRIPT,
            storage_uri="mock://documents/doc_transcript/Unofficial_Transcript.pdf",
            mime_type="application/pdf",
            size_bytes=518002,
            extracted_text_preview="GPA 3.82, coursework includes data structures, policy analysis, statistics.",
            tags=["academic", "needs-review"],
            metadata={"pages": 4},
            status=DocumentProcessingStatus.NEEDS_REVIEW,
            uploaded_at=_dt("2026-06-06T17:35:00"),
        ),
    ]

    matches = [
        MatchResult(
            id="match_civic_ai",
            user_id=DEFAULT_USER_ID,
            opportunity_id="opp_civic_ai",
            score=0.92,
            rationale="Strong alignment with civic technology, public-interest software, and AI safety goals.",
            strengths=["Civic tech portfolio", "Relevant coursework", "Clear public-benefit theme"],
            gaps=["Portfolio link needs a stronger project outcome summary"],
            recommended_actions=["Refresh resume impact bullets", "Draft 650-word personal statement"],
            status=MatchStatus.IN_APPLICATION,
            created_at=_dt("2026-06-09T15:00:00"),
        ),
        MatchResult(
            id="match_open_grant",
            user_id=DEFAULT_USER_ID,
            opportunity_id="opp_open_grant",
            score=0.84,
            rationale="Research interests and open data experience fit the grant goals.",
            strengths=["Open data project idea", "Public policy minor"],
            gaps=["Needs faculty reference confirmed", "Budget not started"],
            recommended_actions=["Ask faculty mentor", "Create one-page research budget"],
            status=MatchStatus.SAVED,
            created_at=_dt("2026-06-10T10:10:00"),
        ),
        MatchResult(
            id="match_first_gen",
            user_id=DEFAULT_USER_ID,
            opportunity_id="opp_first_gen",
            score=0.78,
            rationale="Eligibility is strong, but application materials need tailoring for STEM award criteria.",
            strengths=["First-generation eligibility", "STEM program"],
            gaps=["Financial need statement missing"],
            recommended_actions=["Upload financial aid summary", "Draft short essay"],
            status=MatchStatus.NEW,
            created_at=_dt("2026-06-11T09:25:00"),
        ),
    ]

    applications = [
        Application(
            id="app_civic_ai",
            user_id=DEFAULT_USER_ID,
            opportunity_id="opp_civic_ai",
            match_result_id="match_civic_ai",
            status=ApplicationStatus.IN_PROGRESS,
            due_at=_dt("2026-08-15T23:59:00"),
            checklist=[
                ApplicationChecklistItem(id="task_resume", label="Resume", status=ChecklistItemStatus.DONE),
                ApplicationChecklistItem(id="task_statement", label="Personal statement", status=ChecklistItemStatus.IN_PROGRESS),
                ApplicationChecklistItem(id="task_portfolio", label="Project portfolio", status=ChecklistItemStatus.TODO),
            ],
            notes="Prioritize public-benefit outcomes and prototype screenshots.",
            created_at=_dt("2026-06-09T16:00:00"),
            updated_at=_dt("2026-06-11T12:00:00"),
        ),
        Application(
            id="app_open_grant",
            user_id=DEFAULT_USER_ID,
            opportunity_id="opp_open_grant",
            match_result_id="match_open_grant",
            status=ApplicationStatus.PLANNED,
            due_at=_dt("2026-07-30T23:59:00"),
            checklist=[
                ApplicationChecklistItem(id="task_proposal", label="Research proposal", status=ChecklistItemStatus.TODO),
                ApplicationChecklistItem(id="task_budget", label="Budget", status=ChecklistItemStatus.TODO),
                ApplicationChecklistItem(id="task_reference", label="Faculty reference", status=ChecklistItemStatus.BLOCKED),
            ],
            created_at=_dt("2026-06-10T11:00:00"),
            updated_at=_dt("2026-06-10T11:00:00"),
        ),
    ]

    essay_versions = [
        EssayVersion(
            id="essay_civic_ai_v1",
            application_id="app_civic_ai",
            prompt="Describe how your work uses technology to improve public outcomes.",
            content="Draft outline: community problem, prototype, measurable outcome, future plan.",
            version_number=1,
            status=EssayStatus.OUTLINE,
            feedback_notes=["Add a concrete beneficiary story", "Quantify prototype usage"],
            created_at=_dt("2026-06-11T10:00:00"),
        )
    ]

    recommendation_drafts = [
        RecommendationDraft(
            id="rec_open_grant_faculty",
            application_id="app_open_grant",
            recommender_name="Dr. Ana Patel",
            recommender_email="apatel@example.edu",
            relationship="Faculty research mentor",
            draft_body="Short request draft for a research-focused recommendation.",
            status=RecommendationStatus.DRAFTED,
            created_at=_dt("2026-06-10T12:30:00"),
            updated_at=_dt("2026-06-10T12:30:00"),
        )
    ]

    outreach_emails = [
        OutreachEmail(
            id="email_open_grant_faculty",
            application_id="app_open_grant",
            recipient_email="apatel@example.edu",
            subject="Recommendation request for Open Data Research Grant",
            body="Draft email asking for a faculty reference and offering a short project summary.",
            status=OutreachEmailStatus.DRAFT,
            created_at=_dt("2026-06-10T12:40:00"),
            updated_at=_dt("2026-06-10T12:40:00"),
        )
    ]

    notifications = [
        Notification(
            id="not_deadline_open_grant",
            user_id=DEFAULT_USER_ID,
            title="Open Data Research Grant closes soon",
            message="Research proposal and budget are still pending.",
            notification_type=NotificationType.DEADLINE,
            action_url="/applications",
            created_at=_dt("2026-06-11T08:00:00"),
        ),
        Notification(
            id="not_transcript_review",
            user_id=DEFAULT_USER_ID,
            title="Transcript needs review",
            message="Confirm the parsed coursework before matching uses it.",
            notification_type=NotificationType.DOCUMENT,
            action_url="/documents",
            created_at=_dt("2026-06-10T18:00:00"),
        ),
    ]

    agent_action_logs = [
        AgentActionLog(
            id="log_seed_match",
            user_id=DEFAULT_USER_ID,
            agent_name="matching-agent",
            action_type="seeded_match_preview",
            status=AgentActionStatus.SKIPPED,
            input_summary="Demo profile and seeded opportunities",
            output_summary="Static match records loaded for interface development",
            metadata={"agent_logic_enabled": False},
            created_at=_dt("2026-06-09T15:00:00"),
        )
    ]

    ingestion_runs = [
        IngestionRun(
            id="ingest_demo_seed",
            source_name="demo_seed_loader",
            status=IngestionRunStatus.COMPLETED,
            records_seen=18,
            records_loaded=18,
            metadata={"storage_mode": "seed"},
            started_at=_dt("2026-06-09T14:45:00"),
            completed_at=_dt("2026-06-09T14:46:00"),
        )
    ]

    collections = {
        "user_profiles": [profile],
        "uploaded_documents": documents,
        "opportunities": opportunities,
        "match_results": matches,
        "applications": applications,
        "essay_versions": essay_versions,
        "recommendation_drafts": recommendation_drafts,
        "outreach_emails": outreach_emails,
        "notifications": notifications,
        "agent_action_logs": agent_action_logs,
        "ingestion_runs": ingestion_runs,
    }
    return {
        name: [
            item.model_dump(mode="json") if hasattr(item, "model_dump") else item
            for item in values
        ]
        for name, values in collections.items()
    }

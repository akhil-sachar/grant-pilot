CREATE DATABASE IF NOT EXISTS grantpilot;

USE grantpilot;

CREATE TABLE IF NOT EXISTS user_profiles
(
    id String,
    email String,
    full_name String,
    phone Nullable(String),
    location Nullable(String),
    date_of_birth Nullable(Date),
    education_level Nullable(String),
    school_name Nullable(String),
    major Nullable(String),
    gpa Nullable(Float32),
    graduation_year Nullable(UInt16),
    fields_of_study Array(String),
    career_goals Array(String),
    research_interests Array(String),
    awards Array(String),
    projects Array(String),
    leadership_experience Array(String),
    citizenship_status Nullable(String),
    funding_goals Array(String),
    demographic_info_json String,
    preferences_json String,
    created_at DateTime64(3, 'UTC'),
    updated_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY id;

CREATE TABLE IF NOT EXISTS uploaded_documents
(
    id String,
    user_id String,
    file_name String,
    document_type LowCardinality(String),
    storage_uri String,
    mime_type String,
    size_bytes UInt64,
    extracted_text Nullable(String),
    extracted_text_preview Nullable(String),
    current_version_id Nullable(String),
    version_number UInt16,
    tags Array(String),
    metadata_json String,
    status LowCardinality(String),
    uploaded_at DateTime64(3, 'UTC'),
    updated_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (user_id, id);

CREATE TABLE IF NOT EXISTS document_versions
(
    id String,
    document_id String,
    user_id String,
    version_number UInt16,
    file_name String,
    storage_uri String,
    mime_type String,
    size_bytes UInt64,
    extracted_text Nullable(String),
    extracted_text_preview Nullable(String),
    metadata_json String,
    created_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(created_at)
ORDER BY (document_id, version_number, id);

CREATE TABLE IF NOT EXISTS opportunities
(
    id String,
    provider_name String,
    title String,
    description String,
    opportunity_type LowCardinality(String),
    amount_min Nullable(UInt32),
    amount_max Nullable(UInt32),
    currency LowCardinality(String),
    deadline Nullable(Date),
    eligibility_summary String,
    requirements Array(String),
    source_url Nullable(String),
    status LowCardinality(String),
    tags Array(String),
    metadata_json String,
    created_at DateTime64(3, 'UTC'),
    updated_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY id;

CREATE TABLE IF NOT EXISTS match_results
(
    id String,
    user_id String,
    opportunity_id String,
    score Float32,
    rationale String,
    strengths Array(String),
    gaps Array(String),
    recommended_actions Array(String),
    status LowCardinality(String),
    metadata_json String,
    created_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(created_at)
ORDER BY (user_id, opportunity_id, id);

CREATE TABLE IF NOT EXISTS applications
(
    id String,
    user_id String,
    opportunity_id String,
    match_result_id Nullable(String),
    status LowCardinality(String),
    due_at Nullable(DateTime64(3, 'UTC')),
    submitted_at Nullable(DateTime64(3, 'UTC')),
    checklist_json String,
    notes Nullable(String),
    metadata_json String,
    created_at DateTime64(3, 'UTC'),
    updated_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (user_id, opportunity_id, id);

CREATE TABLE IF NOT EXISTS essay_versions
(
    id String,
    application_id String,
    prompt String,
    content String,
    version_number UInt16,
    status LowCardinality(String),
    feedback_notes Array(String),
    metadata_json String,
    created_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(created_at)
ORDER BY (application_id, version_number, id);

CREATE TABLE IF NOT EXISTS recommendation_drafts
(
    id String,
    application_id String,
    recommender_name String,
    recommender_email String,
    relationship String,
    draft_body String,
    status LowCardinality(String),
    metadata_json String,
    created_at DateTime64(3, 'UTC'),
    updated_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (application_id, id);

CREATE TABLE IF NOT EXISTS outreach_emails
(
    id String,
    application_id String,
    recipient_email String,
    subject String,
    body String,
    status LowCardinality(String),
    sent_at Nullable(DateTime64(3, 'UTC')),
    metadata_json String,
    created_at DateTime64(3, 'UTC'),
    updated_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (application_id, id);

CREATE TABLE IF NOT EXISTS notifications
(
    id String,
    user_id String,
    title String,
    message String,
    notification_type LowCardinality(String),
    is_read Bool,
    action_url Nullable(String),
    metadata_json String,
    created_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(created_at)
ORDER BY (user_id, created_at, id);

CREATE TABLE IF NOT EXISTS agent_action_logs
(
    id String,
    user_id String,
    agent_name LowCardinality(String),
    action_type LowCardinality(String),
    status LowCardinality(String),
    input_summary Nullable(String),
    output_summary Nullable(String),
    metadata_json String,
    created_at DateTime64(3, 'UTC')
)
ENGINE = MergeTree
ORDER BY (user_id, created_at, id);

CREATE TABLE IF NOT EXISTS ingestion_runs
(
    id String,
    source_name LowCardinality(String),
    status LowCardinality(String),
    records_seen UInt64,
    records_loaded UInt64,
    error_message Nullable(String),
    metadata_json String,
    started_at DateTime64(3, 'UTC'),
    completed_at Nullable(DateTime64(3, 'UTC'))
)
ENGINE = ReplacingMergeTree(started_at)
ORDER BY (source_name, started_at, id);

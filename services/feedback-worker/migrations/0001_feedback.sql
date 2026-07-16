CREATE TABLE IF NOT EXISTS feedback_submissions (
  id TEXT PRIMARY KEY,
  client_event_id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  consent_version TEXT NOT NULL,
  gpt_config_version TEXT NOT NULL,
  package_version TEXT,
  rfe_ids_json TEXT NOT NULL,
  flow_type TEXT NOT NULL,
  completion_status TEXT NOT NULL,
  safety_level TEXT NOT NULL,
  turn_count INTEGER NOT NULL,
  answered_fact_count INTEGER NOT NULL,
  data_absent_count INTEGER NOT NULL,
  clarification_count INTEGER NOT NULL,
  revision_count INTEGER NOT NULL,
  additional_comment_count INTEGER NOT NULL,
  terminology_status TEXT NOT NULL,
  knowledge_load_status TEXT NOT NULL,
  issue_tags_json TEXT NOT NULL,
  rating INTEGER
);

CREATE INDEX IF NOT EXISTS feedback_created_at_idx
  ON feedback_submissions(created_at);
CREATE INDEX IF NOT EXISTS feedback_completion_idx
  ON feedback_submissions(completion_status);
CREATE INDEX IF NOT EXISTS feedback_safety_idx
  ON feedback_submissions(safety_level);
